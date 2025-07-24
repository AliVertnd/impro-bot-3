from datetime import datetime, timedelta
from database.database import db_manager
from database.models import AutoPost, NeuroComment, ActivityLog
from services.broadcast_service import BroadcastService
from services.neuro_service import NeuroService
import logging

logger = logging.getLogger(__name__)

async def check_auto_posts():
    from services.scheduler import scheduler_service
    scheduler = scheduler_service.scheduler
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

                auto_post.next_post_time = current_time + timedelta(
                    seconds=auto_post.interval_seconds
                )

            session.commit()

    except Exception as e:
        logger.error(f"Error checking auto posts: {e}")

async def check_neuro_comments(scheduler):
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
        broadcast_service = BroadcastService()
        await broadcast_service.execute_auto_post(auto_post_id)
    except Exception as e:
        logger.error(f"Error executing auto post {auto_post_id}: {e}")

async def execute_neuro_comment(neuro_comment_id):
    try:
        neuro_service = NeuroService()
        await neuro_service.execute_neuro_comment(neuro_comment_id)
    except Exception as e:
        logger.error(f"Error executing neuro comment {neuro_comment_id}: {e}")

async def cleanup_logs():
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        with db_manager.get_session() as session:
            deleted_count = session.query(ActivityLog).filter(
                ActivityLog.created_at < cutoff_date
            ).delete()
            session.commit()
            logger.info(f"Cleaned up {deleted_count} old log entries")
    except Exception as e:
        logger.error(f"Error cleaning up logs: {e}")
