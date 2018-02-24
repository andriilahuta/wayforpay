from urllib.parse import urljoin, urlencode

from wayforpay.api import Api
from wayforpay.constants import TransactionType, PURCHASE_URL
from wayforpay.forms import Form
from wayforpay.params import FrozenParams


__all__ = ['WayForPay']


class WayForPay:
    def __init__(self, merchant_account, merchant_key):
        self.merchant_account = merchant_account
        self.merchant_key = merchant_key
        self.api = Api(self.merchant_account, self.merchant_key)

    def get_form(self, params: dict):
        return Form(self.merchant_account, self.merchant_key, params)

    def generate_purchase_url(self, params: dict):
        params = FrozenParams(self.merchant_account, self.merchant_key, TransactionType.PURCHASE, params)
        return urljoin(PURCHASE_URL, 'get') + '?' + urlencode(params)
