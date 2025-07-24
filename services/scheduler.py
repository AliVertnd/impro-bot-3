import asyncio
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from database.database import db_manager
from database.models import AutoPost, NeuroComment
from config import Config

logger = logging.getLogger(__name__)

# Глобальная переменная для хранения ссылки на scheduler
scheduler_instance = None

# --- Асинхронные задачи, вынесены из класса ---

async def check_auto_posts(scheduler: AsyncIOScheduler):
    """Проверка и выполнение автопостов"""
    try:
        current_time = datetime.utcnow()
        with db_manager.get_session() as session:
            auto_posts = session.query(AutoPost).filter(
                AutoPost.is_active == True,
                AutoPost.next_post_time <= current_time
            ).all()

            for auto_post in auto_posts:
                scheduler.add_job(
                    execute_auto_post,
                    'date',
                    run_date=datetime.utcnow(),
                    args=[auto_post.id],
                    id=f'auto_post_{auto_post.id}_{int(current_time.timestamp())}',
                    replace_existing=False
                )
                auto_post.next_post_time = current_time + timedelta(seconds=auto_post.interval_seconds)

            session.commit()

    except Exception as e:
        logger.error(f"Error checking auto posts: {e}")

async def check_neuro_comments(scheduler: AsyncIOScheduler):
    """Проверка и выполнение нейрокомментирования"""
    try:
        current_time = datetime.utcnow()
        with db_manager.get_session() as session:
            neuro_comments = session.query(NeuroComment).filter(
                NeuroComment.is_active == True
            ).all()

            for neuro_comment in neuro_comments:
                if should_make_neuro_comment(neuro_comment, current_time):
                    scheduler.add_job(
                        execute_neuro_comment,
                        'date',
                        run_date=datetime.utcnow(),
                        args=[neuro_comment.id],
                        id=f'neuro_comment_{neuro_comment.id}_{int(current_time.timestamp())}',
                        replace_existing=False
                    )

    except Exception as e:
        logger.error(f"Error checking neuro comments: {e}")

def should_make_neuro_comment(neuro_comment, current_time):
    if not neuro_comment.last_comment_time:
        return True
    interval_hours = 24 / max(neuro_comment.comments_per_day, 1)
    next_comment_time = neuro_comment.last_comment_time + timedelta(hours=interval_hours)
    return current_time >= next_comment_time

async def execute_auto_post(auto_post_id):
    try:
        from services.broadcast_service import BroadcastService
        broadcast_service = BroadcastService()
        await broadcast_service.execute_auto_post(auto_post_id)
    except Exception as e:
        logger.error(f"Error executing auto post {auto_post_id}: {e}")

async def execute_neuro_comment(neuro_comment_id):
    try:
        from services.neuro_service import NeuroService
        neuro_service = NeuroService()
        await neuro_service.execute_neuro_comment(neuro_comment_id)
    except Exception as e:
        logger.error(f"Error executing neuro comment {neuro_comment_id}: {e}")

async def cleanup_logs():
    try:
        from database.models import ActivityLog
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        with db_manager.get_session() as session:
            deleted_count = session.query(ActivityLog).filter(
                ActivityLog.created_at < cutoff_date
            ).delete()
            session.commit()
            logger.info(f"Cleaned up {deleted_count} old log entries")
    except Exception as e:
        logger.error(f"Error cleaning up logs: {e}")

# --- Обёртки для APScheduler (имена функций должны быть на верхнем уровне модуля) ---

def job_check_auto_posts():
    asyncio.create_task(check_auto_posts(scheduler_instance))

def job_check_neuro_comments():
    asyncio.create_task(check_neuro_comments(scheduler_instance))

def job_cleanup_logs():
    asyncio.create_task(cleanup_logs())

# --- Класс планировщика ---

class SchedulerService:
    def __init__(self):
        jobstores = {'default': SQLAlchemyJobStore(url=Config.DATABASE_URL)}
        executors = {'default': AsyncIOExecutor()}
        job_defaults = {'coalesce': False, 'max_instances': 3}
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='UTC'
        )
        self.running = False

    def start(self):
        global scheduler_instance
        scheduler_instance = self.scheduler

        try:
            # Добавляем задачи с использованием обёрток, которые APScheduler сможет сериализовать
            self.scheduler.add_job(
                job_check_auto_posts,
                'interval',
                minutes=1,
                id='check_auto_posts',
                replace_existing=True
            )
            self.scheduler.add_job(
                job_check_neuro_comments,
                'interval',
                minutes=5,
                id='check_neuro_comments',
                replace_existing=True
            )
            self.scheduler.add_job(
                job_cleanup_logs,
                'cron',
                hour=3,
                minute=0,
                id='cleanup_logs',
                replace_existing=True
            )

            self.scheduler.start()
            self.running = True
            logger.info("Scheduler started successfully")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
            raise

    def stop(self):
        if self.running:
            self.scheduler.shutdown()
            self.running = False
            logger.info("Scheduler stopped")

    def schedule_auto_post(self, auto_post_id, next_run_time):
        self.scheduler.add_job(
            execute_auto_post,
            'date',
            run_date=next_run_time,
            args=[auto_post_id],
            id=f'auto_post_{auto_post_id}_{int(next_run_time.timestamp())}',
            replace_existing=True
        )

    def cancel_auto_post(self, auto_post_id):
        for job in self.scheduler.get_jobs():
            if job.id.startswith(f'auto_post_{auto_post_id}_'):
                job.remove()

    def schedule_neuro_comment(self, neuro_comment_id, next_run_time):
        self.scheduler.add_job(
            execute_neuro_comment,
            'date',
            run_date=next_run_time,
            args=[neuro_comment_id],
            id=f'neuro_comment_{neuro_comment_id}_{int(next_run_time.timestamp())}',
            replace_existing=True
        )

    def cancel_neuro_comment(self, neuro_comment_id):
        for job in self.scheduler.get_jobs():
            if job.id.startswith(f'neuro_comment_{neuro_comment_id}_'):
                job.remove()
