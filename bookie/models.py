import logging

from premo import Model, ModelError, Observer, StateMachine
import sume

from . import Rules, clients, settings


logger = logging.getLogger(__name__)


Model.engine = Model.engines.mysql.configure(settings.mysql)


class Order(Model):

    timestamp = Model.datetime()

    annotation = Model.unicode()

    source = Model.relation(PaymentInstrument)

    destination = Model.relation(PaymentInstrument)

    items = Model.relation(Item).many()

    payments = Model.relation(Payment).many()

    states = StateMachine('OPEN', 'CLOSED', 'INVALID')

    state = Model.enum(states)

    states.on_transition(states.any, states.OPEN, 'order.opened')
    states.on_transition(states.OPEN, states.CLOSED, 'order.closed')
    states.on_transition(states.any, states.INVALID, 'order.invalidated')

    meta = Model.dict()

    CurrencyIssue = ModelError.bequeth()

    CheckoutError = ModelError.bequeth()

    NoPaymentSource = ModelError.bequeth()

    def checkout(self):
        if not self.source:
            raise self.NoPaymentSource()
        try:
            payment = self.source.debit(self.required_balance, order=self)
        except Payment.errors.PaymentError as exc:
            raise self.CheckoutError(exc)
        return self

    def refund(self):
        balance = self.balance
        if balance > 0:
            try:
                payment = self.source.refund(balance, order=self)
            except Payment.errors.PaymentError as exc:
                raise self.CheckoutError(exc)
        return self


    def supported_currencies(self):
        event = clients.event.Event.get(self.meta['event_url'])
        options = Rules.supported_currencies(locale=event.locale)
        return options


    def supported_payment_methods(self):
        event = clients.event.Event.get(self.meta['event_url'])
        options = Rules.supported_payment_options(
            locale=event.locale, processor=event.processor
        )
        return options

    def invalidate(self):
        self.state.transition(self.state.INVALID)
        return self

    def balance(self):
        return self.destination.balance()

    @property
    def required_balance(self):
        currencies = set(item.unit_price.currency for item in self.items)
        if len(currencies) > 1:
            raise self.CurrencyIssue()
        return sum(item.unit_price for item in self.items)


class Item(Model):

    order = Model.relation(Order)

    timestamp = Model.datetime()

    annotation = Model.unicode()

    states = StateMachine('AVAILABLE', 'RESERVED', 'LOCKED')

    state = Model.enum(states)

    url = Model.url()

    quantity = Model.integer()

    unit_price = Model.money()

    tags = Model.list()

    states.on_transition(states.AVAILABLE, states.RESERVED, 'item.reserved')
    states.on_transition(states.RESERVED, states.LOCKED, 'item.locked')
    states.on_transition(states.LOCKED, states.AVAILABLE, 'item.freed')
    states.on_transition(states.RESERVED, states.AVAILABLE, 'item.freed')

    InventoryNotFound = ModelError.bequeth()

    InventoryNotAvailable = ModelError.bequeth()

    def reserve(self, *args, **kwargs):
        try:
            inventory = clients.inventory.Inventory.get(self.uri)
        except self.InventoryNotFound as exc:
            raise
        not_available = (
            inventory.holder != self.guid and
            inventory.state != self.states.AVAILABLE
        )
        if not_available:
            raise self.InventoryNotAvailable()
        try:
            inventory = inventory.reserve(
                quantity=kwargs['quantity'],
                holder=self.guid
            )
        except self.InventoryNotAvailable:
            raise
        self.sync(inventory)
        return self

    def sync(self, inventory):
        self.state = inventory.state
        self.unit_price = inventory.unit_price
        return self


class PaymentInstrument(sume.Instrument):

    def debit(self, value, order=None):
        payment = Payment.stage(value=value, order=order)
        return payment.submit()


class Payment(sume.Payment):

    order = Model.relation(Order)

    states = sume.Payment.states

    states.on_transition(states.any, states.SUCCEEDED, 'payment.succeeded')
    states.on_transition(states.any, states.FAILED, 'payment.failed')
    states.on_transition(states.any, states.PENDING, 'payment.pending')


class ModelObserver(Observer):

    registry = Observer.configure(Rules.event_reactions)
