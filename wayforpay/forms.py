import html

from wayforpay.constants import PURCHASE_URL, TransactionType
from wayforpay.params import FrozenParams


class Form:
    ACTION_URL = PURCHASE_URL

    TEMPLATE = (
        '<form method="post" action="{action}" accept-charset="utf-8">\n'
        '    {param_inputs}\n'
        '    <input type="submit" value="Submit purchase form">\n'
        '</form>'
    )
    INPUT_TEMPLATE = '<input type="hidden" name="{name}" value="{value}" />'

    def __init__(self, merchant_account, merchant_key, params: dict):
        self.merchant_account = merchant_account
        self.merchant_key = merchant_key
        self.params = FrozenParams(self.merchant_account, self.merchant_key, TransactionType.PURCHASE, params)

    def get_inputs(self):
        inputs = []
        for param_name, param_value in self.params.items():
            if isinstance(param_value, (list, tuple)):
                for item in param_value:
                    inputs.append(self.render_input(f'{param_name}[]', item))
            else:
                inputs.append(self.render_input(param_name, param_value))
        return inputs

    def render(self):
        return self.TEMPLATE.format(
            action=self.ACTION_URL,
            param_inputs='\n    '.join(self.get_inputs())
        )

    def render_input(self, name, value):
        return self.INPUT_TEMPLATE.format(name=name, value=html.escape(str(value)))
