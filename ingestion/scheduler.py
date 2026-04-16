"""Automated ingestion scheduler using APScheduler.

Runs three jobs:
  1. Daily (17:00 ET) — fetch prices + compute metrics
  2. Weekly (Sunday 18:00 ET) — sync Fama-French factors
  3. Daily (17:30 ET) — compute FF3 betas (after prices are in)

Usage:
    uv run python -m ingestion.scheduler
"""

from __future__ import annotations

import logging
import signal
import sys

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from db.session import init_db

logger = logging.getLogger(__name__)


def _job_fetch_prices() -> None:
    from ingestion.fetch_prices import fetch_and_store

    logger.info("Scheduler: starting price ingestion…")
    count = fetch_and_store()
    logger.info("Scheduler: price ingestion complete — %d rows", count)


def _job_fetch_factors() -> None:
    from ingestion.fetch_factors import fetch_and_store

    logger.info("Scheduler: starting factor sync…")
    count = fetch_and_store(force=False)
    logger.info("Scheduler: factor sync complete — %d rows", count)


def _job_compute_betas() -> None:
    from ingestion.compute_betas import compute_and_store_betas

    logger.info("Scheduler: starting beta computation…")
    count = compute_and_store_betas()
    logger.info("Scheduler: beta computation complete — %d rows", count)


def build_scheduler() -> BlockingScheduler:
    """Create and configure the scheduler with all ingestion jobs."""
    scheduler = BlockingScheduler(timezone="US/Eastern")

    scheduler.add_job(
        _job_fetch_prices,
        trigger=CronTrigger(hour=17, minute=0, day_of_week="mon-fri"),
        id="fetch_prices",
        name="Fetch daily prices + compute metrics",
        misfire_grace_time=3600,
    )

    scheduler.add_job(
        _job_fetch_factors,
        trigger=CronTrigger(hour=18, minute=0, day_of_week="sun"),
        id="fetch_factors",
        name="Sync Fama-French factors",
        misfire_grace_time=7200,
    )

    scheduler.add_job(
        _job_compute_betas,
        trigger=CronTrigger(hour=17, minute=30, day_of_week="mon-fri"),
        id="compute_betas",
        name="Compute FF3 betas",
        misfire_grace_time=3600,
    )

    return scheduler


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    init_db()
    scheduler = build_scheduler()

    def _shutdown(signum: int, frame: object) -> None:
        logger.info("Received signal %s — shutting down scheduler", signum)
        scheduler.shutdown(wait=False)
        sys.exit(0)

    signal.signal(signal.SIGTERM, _shutdown)
    signal.signal(signal.SIGINT, _shutdown)

    logger.info("AlphaForge scheduler started. Jobs:")
    for job in scheduler.get_jobs():
        logger.info("  %s — %s", job.id, job.trigger)

    scheduler.start()
