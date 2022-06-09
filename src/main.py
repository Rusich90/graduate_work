import aioredis
import sentry_sdk
import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi_pagination import add_pagination
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from api.v1 import subscriptions
from api.v1 import transactions
from core.logger import LOGGING
from core.logger import config
from db import cache

app = FastAPI(
    title="Billing API для онлайн-кинотеатра",
    description="Оплата, подписка и возврат средств",
    version="1.0.0",
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

if config.sentry_dsn:
    sentry_sdk.init(dsn=config.sentry_dsn)
    app.add_middleware(SentryAsgiMiddleware)


@app.on_event('startup')
async def startup():
    cache.cache = await aioredis.create_redis_pool((cache.config.host, cache.config.port), minsize=10, maxsize=20)


@app.on_event('shutdown')
async def shutdown():
    await cache.cache.close()

app.include_router(transactions.router, prefix='/api/v1/transactions')
app.include_router(subscriptions.router, prefix='/api/v1/subscriptions')

add_pagination(app)

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        reload=True,
    )
