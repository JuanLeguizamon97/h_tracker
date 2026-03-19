"""
Invoice auto-generation scheduler.

Runs daily at 08:00 and checks each active project to see if today is
its invoice generation day based on its billing_period configuration.
"""
import logging
import uuid
from datetime import date, datetime, timezone, timedelta
from dateutil.relativedelta import relativedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


# ── Period calculation helpers ────────────────────────────────────────────────

def _next_invoice_date(project, last_invoice_date: date | None = None) -> date | None:
    """
    Return the next invoice generation date for a project based on its
    billing_period, billing_day_of_period, and billing_anchor_date.
    Returns None if the project has no billing configuration.
    """
    period = getattr(project, 'billing_period', None) or 'monthly'
    day = getattr(project, 'billing_day_of_period', None) or 3
    anchor = getattr(project, 'billing_anchor_date', None)
    custom_days = getattr(project, 'custom_period_days', None)

    today = date.today()

    if period == 'monthly':
        # Billing day of the current month; if already passed, next month
        try:
            candidate = today.replace(day=day)
        except ValueError:
            # day > days in month (e.g. day=31 in April)
            import calendar
            last_day = calendar.monthrange(today.year, today.month)[1]
            candidate = today.replace(day=last_day)
        if candidate < today:
            candidate = (today + relativedelta(months=1)).replace(day=min(
                day,
                _days_in_month((today + relativedelta(months=1)).year,
                               (today + relativedelta(months=1)).month)
            ))
        return candidate

    elif period == 'bimonthly':
        base = today.replace(day=min(day, _days_in_month(today.year, today.month)))
        if base < today:
            nxt = today + relativedelta(months=2)
            base = nxt.replace(day=min(day, _days_in_month(nxt.year, nxt.month)))
        return base

    elif period == 'quarterly':
        # Months: 1, 4, 7, 10
        quarterly_months = [1, 4, 7, 10]
        for m in quarterly_months:
            candidate = date(today.year, m, min(day, _days_in_month(today.year, m)))
            if candidate >= today:
                return candidate
        # Wrap to next year
        return date(today.year + 1, 1, min(day, _days_in_month(today.year + 1, 1)))

    elif period == 'weekly':
        ref = anchor or last_invoice_date or today
        nxt = ref + timedelta(days=7)
        while nxt < today:
            nxt += timedelta(days=7)
        return nxt

    elif period == 'biweekly':
        ref = anchor or last_invoice_date or today
        nxt = ref + timedelta(days=14)
        while nxt < today:
            nxt += timedelta(days=14)
        return nxt

    elif period == 'custom':
        if not custom_days or custom_days < 1:
            return None
        ref = anchor or last_invoice_date or today
        nxt = ref + timedelta(days=custom_days)
        while nxt < today:
            nxt += timedelta(days=custom_days)
        return nxt

    return None


def _days_in_month(year: int, month: int) -> int:
    import calendar
    return calendar.monthrange(year, month)[1]


def _period_bounds_for_project(project, today: date) -> tuple[date, date]:
    """
    Calculate (period_start, period_end) for a project's current billing cycle.
    """
    period = getattr(project, 'billing_period', None) or 'monthly'
    day = getattr(project, 'billing_day_of_period', None) or 3
    anchor = getattr(project, 'billing_anchor_date', None)
    custom_days = getattr(project, 'custom_period_days', None)

    if period == 'monthly':
        period_end = (today - relativedelta(months=1)).replace(
            day=_days_in_month((today - relativedelta(months=1)).year,
                               (today - relativedelta(months=1)).month)
        )
        period_start = period_end.replace(day=1)
        return period_start, period_end

    elif period == 'bimonthly':
        period_end = today - timedelta(days=1)
        period_start = (today - relativedelta(months=2)).replace(day=day)
        return period_start, period_end

    elif period == 'quarterly':
        period_end = today - timedelta(days=1)
        period_start = today - relativedelta(months=3)
        return period_start, period_end

    elif period in ('weekly', 'biweekly', 'custom'):
        if period == 'weekly':
            delta = timedelta(days=7)
        elif period == 'biweekly':
            delta = timedelta(days=14)
        else:
            delta = timedelta(days=(custom_days or 30))
        period_end = today - timedelta(days=1)
        period_start = today - delta
        return period_start, period_end

    # fallback: last calendar month
    period_end = (today - relativedelta(months=1)).replace(
        day=_days_in_month((today - relativedelta(months=1)).year,
                           (today - relativedelta(months=1)).month)
    )
    return period_end.replace(day=1), period_end


# ── Main scheduler job ────────────────────────────────────────────────────────

def auto_generate_daily_invoices():
    """
    Runs every day at 08:00.
    For each active, non-internal project: check if today is the invoice
    generation day per its billing_period. If yes, generate a draft invoice
    for its current billing period.
    """
    from config.database import SessionLocal
    from services.invoice_generator import generate_invoice_for_project_period
    from models.projects import Project
    from models.scheduler_log import SchedulerLog

    db = SessionLocal()
    today = date.today()
    total_generated = 0
    total_skipped = 0
    errors = []

    try:
        active_projects = db.query(Project).filter(
            Project.is_active == True,
            Project.is_internal == False,
        ).all()

        for project in active_projects:
            try:
                next_date = _next_invoice_date(project)
                if next_date != today:
                    total_skipped += 1
                    continue

                period_start, period_end = _period_bounds_for_project(project, today)
                result = generate_invoice_for_project_period(db, project, period_start, period_end)
                if result.get('generated'):
                    total_generated += 1
                    logger.info(
                        f"[Scheduler] Generated invoice for project {project.name} "
                        f"({period_start} -> {period_end})"
                    )
                else:
                    total_skipped += 1
            except Exception as e:
                errors.append(f"{project.id}: {e}")
                logger.error(f"[Scheduler] Error for project {project.id}: {e}")

        log = SchedulerLog(
            id=str(uuid.uuid4()),
            run_at=datetime.now(timezone.utc),
            period_start=str(today),
            period_end=str(today),
            invoices_generated=total_generated,
            invoices_skipped=total_skipped,
            status="success" if not errors else "error",
            error_message="; ".join(errors) if errors else None,
        )
        db.add(log)
        db.commit()
        logger.info(
            f"[Scheduler] Daily run complete: {total_generated} generated, "
            f"{total_skipped} skipped, {len(errors)} errors"
        )
    except Exception as e:
        logger.error(f"[Scheduler] Fatal error: {e}")
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(
        auto_generate_daily_invoices,
        CronTrigger(hour=8, minute=0),
        id="auto_invoice_generation",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Invoice scheduler started — runs daily at 08:00")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
