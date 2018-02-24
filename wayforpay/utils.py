import hashlib
import hmac
from functools import reduce


def generate_signature(merchant_key: str, fields: list) -> str:
    # flatten fields
    fields = reduce(lambda x, y: x + (list(y) if isinstance(y, (list, tuple)) else [y]), fields, [])
    signature_str = ';'.join(map(str, fields))
    return hmac.new(merchant_key.encode(), signature_str.encode(), hashlib.md5).hexdigest()
