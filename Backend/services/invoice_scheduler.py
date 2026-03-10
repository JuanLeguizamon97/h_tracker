import logging
import uuid
from datetime import date, datetime, timezone
from dateutil.relativedelta import relativedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


def auto_generate_monthly_invoices():
    """
    Runs on the 5th of every month at 00:00.
    Generates draft invoices for all active projects
    covering the previous calendar month.
    """
    from config.database import SessionLocal
    from services.invoice_generator import generate_invoices_for_period
    from models.scheduler_log import SchedulerLog

    db = SessionLocal()
    try:
        today = date.today()
        period_end = today.replace(day=1) - relativedelta(days=1)
        period_start = period_end.replace(day=1)

        logger.info(f"Running auto invoice generation for {period_start} -> {period_end}")
        result = generate_invoices_for_period(db, period_start, period_end)

        log = SchedulerLog(
            id=str(uuid.uuid4()),
            run_at=datetime.now(timezone.utc),
            period_start=str(period_start),
            period_end=str(period_end),
            invoices_generated=result["generated"],
            invoices_skipped=result["skipped"],
            status="success" if not result["errors"] else "error",
            error_message="; ".join(result["errors"]) if result["errors"] else None,
        )
        db.add(log)
        db.commit()
        logger.info(f"Auto generation complete: {result['generated']} generated, {result['skipped']} skipped")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(
        auto_generate_monthly_invoices,
        CronTrigger(day=5, hour=0, minute=0),
        id="auto_invoice_generation",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Invoice scheduler started — runs on 5th of each month at 00:00")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
