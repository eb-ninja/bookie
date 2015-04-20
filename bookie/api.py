from premo import JsonApplication, JsonResource, Registry
from bookie import models


class BookieApplication(JsonApplication):
    pass


app = BookieApplication()


class Resource(JsonResource):

    registry = Registry(app)


class Order(Resource):
    url = '/orders'
    model = models.Order


@Resource.nest_under(Order)
class Item(Resource):
    url = '/items'
    model = models.Item


@Resource.nest_under(Order)
class Payment(Resource):
    url = '/payments'
    model = models.Payment
