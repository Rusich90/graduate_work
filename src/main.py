import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import aioredis
from api.v1 import billing
from api.v1 import subscription
from core.logger import LOGGING
from db import cache

app = FastAPI(
    title="Billing API для онлайн-кинотеатра",
    description="Оплата, подписка и возврат средств",
    version="1.0.0",
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    cache.cache = await aioredis.create_redis_pool((cache.config.host, cache.config.port), minsize=10, maxsize=20)


@app.on_event('shutdown')
async def shutdown():
    await cache.cache.close()

app.include_router(billing.router, prefix='/api/v1/billing')
app.include_router(subscription.router, prefix='/api/v1/subscriptions')


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        reload=True,
    )
