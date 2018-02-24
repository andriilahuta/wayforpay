from collections import MutableMapping
from itertools import chain

from wayforpay.constants import TransactionType, SIGNATURE_FIELDS, REQUIRED_FIELDS, ChargeTransactionType, \
    SUPPORTED_LANGUAGES, PAYMENT_SYSTEMS
from wayforpay.utils import generate_signature


class ParamRequired(Exception):
    pass


class ParamValidationError(Exception):
    pass


class ParamsBase(MutableMapping):
    def __init__(self, *args, **kwargs):
        self._store = {}
        self.update(dict(*args, **kwargs))

    def __getitem__(self, key):
        return self._store[key]

    def __setitem__(self, key, value):
        self._store[key] = value

    def __delitem__(self, key):
        del self._store[key]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def __contains__(self, key):
        return key in self._store

    def __str__(self):
        return str(self._store)

    def __repr__(self):
        return repr(self._store)


def _val_not_empty_validator(val):
    return bool(val)


def _transaction_type_validator(val):
    try:
        TransactionType(val)
        return True
    except ValueError:
        return False


class Params(ParamsBase):
    validators = {
        **{field: _val_not_empty_validator for field in set(chain.from_iterable(REQUIRED_FIELDS.values()))},
        'transactionType': _transaction_type_validator,
        'language': lambda x: x in SUPPORTED_LANGUAGES,
        'paymentSystems': lambda x: set(x).issubset(PAYMENT_SYSTEMS),
    }
    post_processors = {
        'paymentSystems': lambda x: ';'.join(x)
    }

    def prepare(self, merchant_key: str):
        required_fields = self.get_required_fields()
        required_fields -= {'merchantSignature'}
        self._require_fields(required_fields)
        self['merchantSignature'] = self._generate_signature(merchant_key)

    def get_required_fields(self) -> set:
        self._require_fields({'transactionType'})
        key = TransactionType(self['transactionType'])
        if key is TransactionType.CHARGE:
            key = ChargeTransactionType.REC_TOKEN if self.get('recToken') else ChargeTransactionType.NO_REC_TOKEN
        return set(REQUIRED_FIELDS[key] + self._get_signature_fields())

    def _get_signature_fields(self) -> list:
        self._require_fields({'transactionType'})
        transaction_type = TransactionType(self['transactionType'])
        return SIGNATURE_FIELDS[transaction_type]

    def _generate_signature(self, merchant_key: str):
        signature_fields = self._get_signature_fields()
        self._require_fields(signature_fields)
        return generate_signature(merchant_key, [self[field] for field in signature_fields])

    def _require_fields(self, fields):
        if not isinstance(fields, set):
            fields = set(fields)
        if not fields.issubset(self.keys()):
            raise ParamRequired("Required param(s) not found: '{}'".format(
                ', '.join(fields - self.keys())
            ))

    def _validate_field(self, field, val):
        validator = self.validators.get(field)
        if callable(validator) and not validator(val):
            raise ParamValidationError(f"Invalid param: '{field}'")

    def _post_process(self, key, val):
        post_processor = self.post_processors.get(key)
        return post_processor(val) if callable(post_processor) else val

    def __setitem__(self, key, value):
        self._validate_field(key, value)
        value = self._post_process(key, value)
        super().__setitem__(key, value)


class FrozenParams(ParamsBase):
    def __init__(self, merchant_account, merchant_key: str, transaction_type: TransactionType, params: dict):
        super().__init__()
        self._store = Params(transactionType=transaction_type.value, merchantAccount=merchant_account, **params)
        self._store.prepare(merchant_key)

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError
