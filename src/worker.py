import asyncio
import logging.config

from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.logger import LOGGING
from core.settings import SchedulerSettings
from db.config import async_session
from services.billing import YookassaBilling
from services.database import AlchemyDatabase

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('worker')

config = SchedulerSettings()
jobstores = {
    'default': RedisJobStore(host=config.jobstore.host, port=config.jobstore.port, db=2)
}
scheduler = AsyncIOScheduler(jobstores=jobstores)


@scheduler.scheduled_job("cron", hour=config.subscribe_hour, minute=config.subscribe_minute)
async def daily_check_end_of_subscribes():
    async with async_session() as session:
        async with session.begin():
            db = AlchemyDatabase(session)
            billing = YookassaBilling(db)
            subscribes = await db.get_subscribers()
            for subscribe in subscribes:
                if subscribe.auto_renewal:
                    await billing.auto_payment(subscribe)
                else:
                    # TODO: send  all id to kafka
                    pass


@scheduler.scheduled_job("cron", hour=config.pending_hour, minute=config.pending_minute)
async def hourly_check_pending_payments():
    # TODO: check pending payments
    pass


async def main():
    try:
        scheduler.start()
    except KeyboardInterrupt:
        scheduler.shutdown()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
