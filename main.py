
#!/usr/bin/env python3
"""
Telegram Bot для парсинга, рассылок и инвайтинга
Основной файл запуска приложения
"""

import asyncio
import logging
import signal
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Thread

from config import Config
from database.database import db_manager
from app.bot import TelegramBot
from web.app import create_flask_app
from services.scheduler import SchedulerService

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'{Config.LOGS_DIR}/bot.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class Application:
    def __init__(self):
        self.bot = None
        self.flask_app = None
        self.scheduler = None
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._stop_event = asyncio.Event()
    
    async def start(self):
        """Запуск всех компонентов приложения"""
        logger.info("Starting Telegram Bot Application...")
        
        try:
            # Инициализация базы данных
            logger.info("Initializing database...")
            db_manager.init_database()
            
            # Создание и запуск бота
            logger.info("Starting Telegram bot...")
            self.bot = TelegramBot()
            
            # Создание Flask приложения
            logger.info("Creating Flask web interface...")
            self.flask_app = create_flask_app()
            
            # Запуск планировщика задач
            logger.info("Starting scheduler service...")
            self.scheduler = SchedulerService()
            self.scheduler.start()
            
            # Запуск Flask в отдельном потоке
            flask_thread = Thread(
                target=self._run_flask,
                daemon=True
            )
            flask_thread.start()
            
            # Запуск бота
            self.running = True
            await self.bot.start()
            await self._stop_event.wait()

            
        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            await self.stop()
            raise

    async def stop(self):
        """Остановка всех компонентов приложения"""
        logger.info("Stopping application...")
        self.running = False
        if self.scheduler:
            self.scheduler.stop()
        if self.bot:
            await self.bot.stop()
        logger.info("Application stopped.")
        self._stop_event.set()

    def _run_flask(self):
        """Запуск Flask приложения в отдельном потоке"""
        try:
            self.flask_app.run(
                host='0.0.0.0',
                port=Config.FLASK_PORT,
                debug=Config.DEBUG,
                use_reloader=False
            )
        except Exception as e:
            logger.error(f"Error running Flask app: {e}")

def shutdown(signal_num, frame):
    logger.info(f"Received exit signal {signal_num}")
    loop = asyncio.get_event_loop()
    loop.create_task(app.stop())

if __name__ == "__main__":
    app = Application()
    loop = asyncio.get_event_loop()
    for s in (signal.SIGINT, signal.SIGTERM):
        signal.signal(s, shutdown)

    try:
        loop.run_until_complete(app.start())
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Exiting...")
    finally:
        loop.run_until_complete(app.stop())
        loop.close()
