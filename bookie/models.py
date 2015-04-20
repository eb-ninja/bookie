import logging

from premo import Model, ModelError, Observer, PhysicalModel, StateMachine
import sume

from . import Rules, clients, settings


logger = logging.getLogger(__name__)


PhysicalModel.engine = PhysicalModel.engines.mysql.configure(settings.mysql)


class OrderSchema(PhysicalModel):

    timestamp = PhysicalModel.datetime()

    annotation = PhysicalModel.unicode()

    source = PhysicalModel.relation(PaymentInstrument)

    destination = PhysicalModel.relation(PaymentInstrument)

    state = PhysicalModel.enum(Order.states)

    meta = PhysicalModel.dict()


class ItemSchema(PhysicalModel):

    order = PhysicalModel.relation(Order)

    timestamp = PhysicalModel.datetime()

    annotation = PhysicalModel.unicode()

    state = PhysicalModel.enum(Item.states)

    url = PhysicalModel.url()

    quantity = PhysicalModel.integer()

    unit_price = PhysicalModel.money()

    tags = PhysicalModel.list()


class PaymentSchema(sume.PaymentSchema):

    order = PhysicalModel.relation(Order)


class Order(Model):

    __physical__ = OrderSchema

    payments = Model.relation(Payment).many()

    items = Model.relation(Item).many()

    states = StateMachine('OPEN', 'CLOSED', 'INVALID')
    states.on_transition(states.any, states.OPEN, 'order.opened')
    states.on_transition(states.OPEN, states.CLOSED, 'order.closed')
    states.on_transition(states.any, states.INVALID, 'order.invalidated')

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

    CurrencyIssue = ModelError.bequeth()

    CheckoutError = ModelError.bequeth()

    NoPaymentSource = ModelError.bequeth()


class Item(Model):

    __physical__ = ItemSchema

    states = StateMachine('AVAILABLE', 'RESERVED', 'LOCKED')

    states.on_transition(states.AVAILABLE, states.RESERVED, 'item.reserved')
    states.on_transition(states.RESERVED, states.LOCKED, 'item.locked')
    states.on_transition(states.LOCKED, states.AVAILABLE, 'item.freed')
    states.on_transition(states.RESERVED, states.AVAILABLE, 'item.freed')


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

    InventoryNotFound = ModelError.bequeth()

    InventoryNotAvailable = ModelError.bequeth()


class Payment(sume.Payment):

    __physical__ = PaymentSchema

    states = sume.Payment.states

    states.on_transition(states.any, states.SUCCEEDED, 'payment.succeeded')
    states.on_transition(states.any, states.FAILED, 'payment.failed')
    states.on_transition(states.any, states.PENDING, 'payment.pending')


class PaymentInstrument(sume.Instrument):

    def debit(self, value, order=None):
        payment = Payment.stage(value=value, order=order)
        return payment.submit()


class ModelObserver(Observer):

    registry = Observer.configure(Rules.event_reactions)
