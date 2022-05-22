from abc import ABC, abstractmethod
from typing import Dict, Optional
from functools import lru_cache
from core import settings
from yookassa import Payment, Configuration
from core.settings import BillingSettings
import json

config = BillingSettings()

class AbstractBilling(ABC):

    @abstractmethod
    async def payment(self):
        pass


class YookassaBilling(AbstractBilling):

    def payment(self):
        Configuration.account_id = config.id
        Configuration.secret_key = config.token.get_secret_value()
        payment = Payment.create({
            "amount": {
                "value": "100.00",
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "http://localhost/api/v1/billing/redirect"
            },
            "capture": True,
            "description": "Заказ №1"
        })
        return json.loads(payment.json())


@lru_cache()
def get_billing_service() -> YookassaBilling:
    return YookassaBilling()
