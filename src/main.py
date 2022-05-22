import logging

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import billing, subscription
from core import settings
from core.logger import LOGGING


# tags_metadata = [
#     {"name": "Полнотекстовый поиск"},
#     {"name": "Фильмы"},
#     {"name": "Персоны"},
#     {"name": "Жанры"}
# ]

app = FastAPI(
    title="Billing API для онлайн-кинотеатра",
    description="Оплата, подписка и возврат средств",
    version="1.0.0",
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    # openapi_tags=tags_metadata,
)


# @app.on_event('startup')
# def startup():
#     db.init()
#
#
# @app.on_event('shutdown')
# def shutdown():
#     db.close()


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
