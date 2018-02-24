from functools import partialmethod

import requests

from wayforpay.constants import TransactionType, API_URL
from wayforpay.params import FrozenParams


class Api:
    def __init__(self, merchant_account, merchant_key):
        self.merchant_account = merchant_account
        self.merchant_key = merchant_key

    def _query(self, transaction_type: TransactionType, params: dict):
        params = FrozenParams(self.merchant_account, self.merchant_key, transaction_type, params)
        response = requests.post(API_URL, json=params)
        return response.json()

    settle = partialmethod(_query, TransactionType.SETTLE)
    charge = partialmethod(_query, TransactionType.CHARGE)
    refund = partialmethod(_query, TransactionType.REFUND)
    check_status = partialmethod(_query, TransactionType.CHECK_STATUS)
    account2card = partialmethod(_query, TransactionType.P2P_CREDIT)
    create_invoice = partialmethod(_query, TransactionType.CREATE_INVOICE)
    account2phone = partialmethod(_query, TransactionType.P2_PHONE)
    transaction_list = partialmethod(_query, TransactionType.TRANSACTION_LIST)
