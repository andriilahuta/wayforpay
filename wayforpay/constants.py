from enum import Enum, auto


API_URL = 'https://api.wayforpay.com/api'
PURCHASE_URL = 'https://secure.wayforpay.com/pay'

SUPPORTED_LANGUAGES = ['AUTO', 'RU', 'UA', 'EN']
PAYMENT_SYSTEMS = ['card', 'privat24', 'lpTerminal', 'btc', 'credit', 'payParts', 'qrCode',
                   'masterPass', 'visaCheckout', 'googlePay', 'applePay']


class TransactionType(str, Enum):
    PURCHASE = 'PURCHASE'
    SETTLE = 'SETTLE'
    CHARGE = 'CHARGE'
    REFUND = 'REFUND'
    CHECK_STATUS = 'CHECK_STATUS'
    P2P_CREDIT = 'P2P_CREDIT'
    CREATE_INVOICE = 'CREATE_INVOICE'
    P2_PHONE = 'P2_PHONE'
    TRANSACTION_LIST = 'TRANSACTION_LIST'


class ChargeTransactionType(Enum):
    REC_TOKEN = auto()
    NO_REC_TOKEN = auto()


SIGNATURE_FIELDS = {
    TransactionType.PURCHASE: [
        'merchantAccount',
        'merchantDomainName',
        'orderReference',
        'orderDate',
        'amount',
        'currency',
        'productName',
        'productCount',
        'productPrice',
    ],
    TransactionType.REFUND: [
        'merchantAccount',
        'orderReference',
        'amount',
        'currency',
    ],
    TransactionType.CHECK_STATUS: [
        'merchantAccount',
        'orderReference',
    ],
    TransactionType.SETTLE: [
        'merchantAccount',
        'orderReference',
        'amount',
        'currency',
    ],
    TransactionType.P2P_CREDIT: [
        'merchantAccount',
        'orderReference',
        'amount',
        'currency',
        'cardBeneficiary',
        'rec2Token',
    ],
    TransactionType.P2_PHONE: [
        'merchantAccount',
        'orderReference',
        'amount',
        'currency',
        'phone',
    ],
    TransactionType.TRANSACTION_LIST: [
        'merchantAccount',
        'dateBegin',
        'dateEnd',
    ],
}
SIGNATURE_FIELDS[TransactionType.CHARGE] = SIGNATURE_FIELDS[TransactionType.CREATE_INVOICE] = SIGNATURE_FIELDS[TransactionType.PURCHASE]


REQUIRED_FIELDS = {
    TransactionType.PURCHASE: [
        'merchantAccount',
        'merchantDomainName',
        'merchantTransactionSecureType',
        'orderReference',
        'orderDate',
        'amount',
        'currency',
        'productName',
        'productCount',
        'productPrice',
    ],
    TransactionType.REFUND: [
        'merchantAccount',
        'transactionType',
        'orderReference',
        'amount',
        'currency',
        'comment',
        'apiVersion',
    ],
    TransactionType.CHECK_STATUS: [
        'merchantAccount',
        'transactionType',
        'orderReference',
        'apiVersion',
    ],
    TransactionType.SETTLE: [
        'merchantAccount',
        'transactionType',
        'orderReference',
        'amount',
        'currency',
        'apiVersion'
    ],
    TransactionType.CHARGE: [
        'merchantAccount',
        'transactionType',
        'merchantDomainName',
        'orderReference',
        'apiVersion',
        'orderDate',
        'amount',
        'currency',
        'productName',
        'productCount',
        'productPrice',
        'clientFirstName',
        'clientLastName',
        'clientEmail',
        'clientPhone',
        'clientCountry',
        'clientIpAddress',
    ],
    TransactionType.P2P_CREDIT: [
        'merchantAccount',
        'transactionType',
        'orderReference',
        'amount',
        'currency',
        'cardBeneficiary',
        'merchantSignature',
    ],
    TransactionType.P2_PHONE: [
        'merchantAccount',
        'orderReference',
        'orderDate',
        'currency',
        'amount',
        'phone',
    ],
    TransactionType.TRANSACTION_LIST: [
        'merchantAccount',
        'dateBegin',
        'dateEnd',
    ],
    TransactionType.CREATE_INVOICE: [
        'merchantAccount',
        'transactionType',
        'merchantDomainName',
        'orderReference',
        'amount',
        'currency',
        'productName',
        'productCount',
        'productPrice',
    ],
}
REQUIRED_FIELDS[ChargeTransactionType.REC_TOKEN] = REQUIRED_FIELDS[TransactionType.CHARGE] + ['recToken']
REQUIRED_FIELDS[ChargeTransactionType.NO_REC_TOKEN] = REQUIRED_FIELDS[TransactionType.CHARGE] + \
                                                      ['card', 'expMonth', 'expYear', 'cardCvv', 'cardHolder']
