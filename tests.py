from textwrap import dedent
from unittest import TestCase
from unittest.mock import patch

import requests

from wayforpay import WayForPay
from wayforpay.api import Api
from wayforpay.constants import TransactionType, ChargeTransactionType, SUPPORTED_LANGUAGES, PAYMENT_SYSTEMS
from wayforpay.forms import Form
from wayforpay.params import Params, ParamValidationError, ParamRequired, FrozenParams
from wayforpay.utils import generate_signature


class UtilsTestCase(TestCase):
    def test_generate_signature(self):
        signature = generate_signature('test', [1, '<test>', [1, 'val"', 2.2]])
        self.assertEqual(signature, 'a0f9b354678c4b66e3a95f6c63841d18')
        signature = generate_signature('test', [1, '<test>', (1, 'val"', 2.2)])
        self.assertEqual(signature, 'a0f9b354678c4b66e3a95f6c63841d18')


class ParamsTestCase(TestCase):
    def test_transaction_type_validation(self):
        self.assertRaises(ParamValidationError, Params, transactionType='')
        self.assertRaises(ParamValidationError, Params, transactionType='test')
        self.assertEqual(Params(transactionType='PURCHASE')['transactionType'], 'PURCHASE')
        self.assertEqual(Params(transactionType=TransactionType.PURCHASE)['transactionType'], 'PURCHASE')

    def test_required_field_validation(self):
        self.assertRaises(ParamValidationError, Params, merchantAccount='')
        self.assertEqual(Params(merchantAccount='test')['merchantAccount'], 'test')

    def test_lang_validation(self):
        for lang in ['', 'test', 'auto', 'en', 'ru', 'ua', 'uk', 'UK']:
            self.assertRaises(ParamValidationError, Params, language=lang)
        for lang in SUPPORTED_LANGUAGES:
            self.assertEqual(Params(language=lang)['language'], lang)

    def test_payment_systems_validation(self):
        for val in [['test'], ['card', 'test'], ['QRCODE']]:
            self.assertRaises(ParamValidationError, Params, paymentSystems=val)
        for val in [['card'], ['lpTerminal', 'btc', 'credit'], PAYMENT_SYSTEMS]:
            self.assertEqual(Params(paymentSystems=val)['paymentSystems'], ';'.join(val))

    def test_signature(self):
        params = Params()
        self.assertRaises(ParamRequired, params._generate_signature, 'key')
        params['transactionType'] = TransactionType.CHECK_STATUS
        self.assertRaises(ParamRequired, params._generate_signature, 'key')
        params.update(merchantAccount='acc', orderReference='new_order')
        signature = params._generate_signature('key')
        self.assertEqual(signature, '128bc357970b1dc6dd55c23f6f6c2b4a')

    def test_prepare(self):
        params = Params(transactionType=TransactionType.CHECK_STATUS, merchantAccount='acc', orderReference='new_order')
        self.assertRaises(ParamRequired, params.prepare, 'key')
        params['apiVersion'] = 1
        params.prepare('key')


class FrozenParamsTestCase(TestCase):
    def test_init(self):
        self.assertRaises(ParamValidationError, FrozenParams, 'acc', 'key', ChargeTransactionType.NO_REC_TOKEN, {})
        self.assertRaises(ParamRequired, FrozenParams, 'acc', 'key', TransactionType.CHECK_STATUS, {})
        params = FrozenParams('acc', 'key', TransactionType.CHECK_STATUS, dict(orderReference='new_order', apiVersion=1))
        self.assertEqual(params['merchantSignature'], '128bc357970b1dc6dd55c23f6f6c2b4a')

    def test_immutability(self):
        params = FrozenParams('acc', 'key', TransactionType.CHECK_STATUS, dict(orderReference='new_order', apiVersion=1))
        with self.assertRaises(NotImplementedError):
            params['test'] = 1
        with self.assertRaises(NotImplementedError):
            params.update(test=1)
        with self.assertRaises(NotImplementedError):
            del params['test']
        with self.assertRaises(NotImplementedError):
            params.pop('apiVersion')


@patch.object(requests, 'post')
class ApiTestCase(TestCase):
    def setUp(self):
        self.api = Api('acc', 'key')

    def test_query(self, post_mock):
        self.assertRaises(ParamRequired, self.api._query, TransactionType.CHECK_STATUS, {})
        post_mock.assert_not_called()

        self.api._query(TransactionType.CHECK_STATUS, dict(orderReference='new_order', apiVersion=1))
        post_mock.assert_called_once()

    def test_shortcuts(self, post_mock):
        self.api.check_status(dict(orderReference='new_order', apiVersion=1))
        post_mock.assert_called_once()
        self.assertEqual(post_mock.call_args[1]['json']['transactionType'], TransactionType.CHECK_STATUS.value)


class FormTestCase(TestCase):
    def test_rendering(self):
        form = Form(
            'acc', 'key',
            dict(orderReference='new order"', amount=1, productName='<Prod>', productCount=2, currency='UAH',
                 orderDate='dummy', merchantDomainName='example.com', productPrice=1, merchantTransactionSecureType='dummy')
        )
        self.assertEqual(form.render(), dedent('''\
            <form method="post" action="https://secure.wayforpay.com/pay" accept-charset="utf-8">
                <input type="hidden" name="transactionType" value="PURCHASE" />
                <input type="hidden" name="merchantAccount" value="acc" />
                <input type="hidden" name="orderReference" value="new order&quot;" />
                <input type="hidden" name="amount" value="1" />
                <input type="hidden" name="productName" value="&lt;Prod&gt;" />
                <input type="hidden" name="productCount" value="2" />
                <input type="hidden" name="currency" value="UAH" />
                <input type="hidden" name="orderDate" value="dummy" />
                <input type="hidden" name="merchantDomainName" value="example.com" />
                <input type="hidden" name="productPrice" value="1" />
                <input type="hidden" name="merchantTransactionSecureType" value="dummy" />
                <input type="hidden" name="merchantSignature" value="10ed98888624ab4aff668bdda555ef2c" />
                <input type="submit" value="Submit purchase form">
            </form>'''))


class WayForPayTestCase(TestCase):
    def setUp(self):
        self.wayforpay = WayForPay('acc', 'key')

    def test_purchase_url(self):
        url = self.wayforpay.generate_purchase_url(
            dict(orderReference='new_order', amount=1, productName='<Prod>', productCount=2, currency='UAH',
                 orderDate='dummy', merchantDomainName='example.com', productPrice=1, merchantTransactionSecureType='dummy')
        )
        self.assertEqual(
            url,
            ('https://secure.wayforpay.com/get?transactionType=PURCHASE&merchantAccount=acc&orderReference=new_order&'
             'amount=1&productName=%3CProd%3E&productCount=2&currency=UAH&orderDate=dummy&merchantDomainName=example.com&'
             'productPrice=1&merchantTransactionSecureType=dummy&merchantSignature=f4437ced558c82182cc33c5b8c9160d2')
        )
