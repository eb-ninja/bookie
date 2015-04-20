from premo import RulesEngine


Rule = RulesEngine.Rule


class Rules(RulesEngine):

    event_reactions = [
        ('payment.failed', None),
        ('payment.succeeded', None),
        ('payment.pending', None),

        ('order.opened', None),
        ('order.closed', None),
        ('order.invalidated', None),

        ('item.reserved', None),
        ('item.locked', None),
        ('item.freed', None),
    ]

    supported_currencies = Rule(
        (
            'locale',
            {
                'USA': ['USD'],
                'EU': ['EUR'],
                None: [],
            }
        )
    )

    supported_payment_options = Rule(
        (
            'locale',
            {
                'USA': [],
                'EU': [],
                None: [],
            }
        ),
        (
            'processor',
            {
                None: []
            }
        )
    )
