# bookie

sell stuff on the internet

## Installation

Set up the service:
```bash
python setup.py install
bookie serve
```

## Interface

### Create a order
#### (render nested objects by adding '?render_depth=2')

Request:
```
    POST /orders
```
```javascript
    {
        "items": {
            "uri": "/inventory/IN7a33e0b3326e1bc"
        }
    }
```

Response:
```
    HTTP 201 CREATED
```
```javascript
    {
        "id": "ORD545173f4b7d9a",
        "type": "order",
        "status": "OPEN",
        "payment_instrument": null,
        "meta": {},
        "links": {
            "self": "/orders/ORD3pu1234",
            "items": "/orders/ORD3pu1234/items",
            "payments": "/orders/ORD3pu1234/payments",
            "balance": "/orders/ORD3pu1234/balance",
            "supported_currencies": "/orders/ORD3pu1234/supported_currencies",
            "supported_payment_methods": "/orders/ORD3pu1234/supported_payment_methods",
            "checkout": "/orders/ORD3pu1234/checkout",
            "refund": "/orders/ORD3pu1234/refund",
            "invalidate": "/orders/ORD3pu1234/invalidate"
        }
    }
```

Request:
```
    POST /orders?render_depth=2
```
```javascript
    {
        "items": {
            "uri": "/inventory/IN7a33e0b3326e1bc"
        }
    }
```

Response:
```
    HTTP 201 CREATED
```
```javascript
    {
        "id": "ORD545173f4b7d9a",
        "type": "order",
        "status": "OPEN",
        "payment_instrument": null,
        "supported_payment_methods": [
            "VISA",
            "MASTERCARD",
            "AMEX",
            "PAYPAL",
            "ACH"
        ],
        "supported_currencies": [
            "USD",
            "EUR"
        ],
        "meta": {},
        "items": [
            {
                "id": "IT29aa943d5",
                "type": "item",
                "meta": {},
                "uri": "/inventory/IN7a33e0b3326e1bc",
                "status": "RESERVED",
                "unit_price": 4353,
                "currency": "USD",
                "quantity": 1
            }
        ],
        "balance": {
            "currency": "USD",
            "amount": 0
        }
        "payments": [],
        "links": {
            "self": "/orders/ORD3pu1234",
            "items": "/orders/ORD3pu1234/items",
            "payments": "/orders/ORD3pu1234/payments",
            "balance": "/orders/ORD3pu1234/balance",
            "supported_currencies": "/orders/ORD3pu1234/supported_currencies",
            "supported_payment_methods": "/orders/ORD3pu1234/supported_payment_methods",
            "checkout": "/orders/ORD3pu1234/checkout",
            "refund": "/orders/ORD3pu1234/refund",
            "invalidate": "/orders/ORD3pu1234/invalidate"
        }
    }
```

### Add an item to the cart
#### (not idempotent, note the quantity in the response):

Request:
```
    POST /orders/ORD545173f4b7d9a/items
```
```javascript
    {
        "uri": "/inventory/IN7a33e0b3326e1bc",
        "quantity": 2
    }
```

Request:
```
    POST /orders/ORD545173f4b7d9a/items
```
```javascript
    [
        {
            "uri": "/inventory/IN7a33e0b3326e1bc",
            "quantity": 1
        },
        {
            "uri": "/inventory/IN7a33e0b3326e1bc",
            "quantity": 1
        }
   ]
```

Response:
```
    HTTP 201 CREATED
```
```javascript
    {
        "links": {
            "self": "/orders/ORD545173f4b7d9a/items",
            "order": "/orders/ORD545173f4b7d9a"
        },
        "items": [
            {
                "id": "IT29aa943d5",
                "type": "item",
                "meta": {},
                "uri": "/inventory/IN7a33e0b3326e1bc",
                "status": "RESERVED",
                "unit_price": 4353,
                "currency": "USD",
                "quantity": 3
            }
        ]
    }
```

### Checkout

Request:
```
    POST /orders/ORD545173f4b7d9a/checkout
```

Response:
```
    HTTP 402 PAYMENT REQUIRED
```
```javascript
    {
        "type": "error",
        "status_code": 402,
        "description": "No payment instrument is associated with the order"
    }
```

### Tokenize a card

Request:
```
    POST /cards
```
```javascript
    {
        "number": 378282246310005,
        "expiration_month": 12,
        "expiration_year": 2020,
        "postal_code": 58102
    }
```

Response:
```
    HTTP 201 CREATED
```
```javascript
    {
        "id": "CC105b1275010dab2"
        "type": "card",
        "meta": {},
        "hash": "a5d172d46fc909f47e337374892330e8",
        "links": {
            "self": "/cards/CC105b1275010dab2"
        }
    }
```

### Set the payment instrument on the order:

Request:
```
    PATCH /orders/ORD545173f4b7d9a
```
```javascript
    {
        "payment_instrument_uri": "/cards/CC105b1275010dab2"
    }
```

Response:
```
    HTTP 200 OK
```
```javascript
    {
        "id": "ORD545173f4b7d9a",
        "type": "order",
        "status": "OPEN",
        "payment_instrument_uri": "/cards/CC105b1275010dab2",
        "meta": {},
        "links": {
            "self": "/orders/ORD3pu1234",
            "items": "/orders/ORD3pu1234/items",
            "payments": "/orders/ORD3pu1234/payments",
            "balance": "/orders/ORD3pu1234/balance",
            "supported_currencies": "/orders/ORD3pu1234/supported_currencies",
            "supported_payment_methods": "/orders/ORD3pu1234/supported_payment_methods",
            "checkout": "/orders/ORD3pu1234/checkout",
            "refund": "/orders/ORD3pu1234/refund",
            "invalidate": "/orders/ORD3pu1234/invalidate"
        }
    }
```

### Remove the payment instrument from the order

Request:
```
    PATCH /orders/ORD545173f4b7d9a
```
```javascript
    {
        "payment_instrument_uri": null
    }
```

Response:
```
    HTTP 200 OK
```
```javascript
    {
        "id": "ORD545173f4b7d9a",
        "type": "order",
        "status": "OPEN",
        "payment_instrument": null,
        "meta": {},
        "links": {
            "self": "/orders/ORD3pu1234",
            "items": "/orders/ORD3pu1234/items",
            "payments": "/orders/ORD3pu1234/payments",
            "balance": "/orders/ORD3pu1234/balance",
            "supported_currencies": "/orders/ORD3pu1234/supported_currencies",
            "supported_payment_methods": "/orders/ORD3pu1234/supported_payment_methods",
            "checkout": "/orders/ORD3pu1234/checkout",
            "refund": "/orders/ORD3pu1234/refund",
            "invalidate": "/orders/ORD3pu1234/invalidate"
        }
    }
```

### Checkout
#### (if present, the body of the POST is applied as a PATCH prior to performing the operation):

Request:
```
    POST /orders/ORD545173f4b7d9a/checkout
```

Request:
```
    POST /orders/ORD545173f4b7d9a/checkout
```
```javascript
    {
        "payment_instrument_uri": "/cards/CC105b1275010dab2"
    }
```

Request:
```
    POST /orders/ORD545173f4b7d9a/checkout
```
```javascript
    {
        "payment_instrument": {
            {
                "type": "card",
                "number": 378282246310005,
                "expiration_month": 12,
                "expiration_year": 2020,
                "postal_code": 58102
            }
        }
    }
```

Response:
```
    HTTP 200 OK
```
```javascript
    {
        "id": "ORD545173f4b7d9a",
        "type": "order",
        "status": "CLOSED",
        "payment_instrument": "/cards/CC105b1275010dab2",
        "meta": {},
        "links": {
            "self": "/orders/ORD3pu1234",
            "items": "/orders/ORD3pu1234/items",
            "payments": "/orders/ORD3pu1234/payments",
            "balance": "/orders/ORD3pu1234/balance",
            "supported_currencies": "/orders/ORD3pu1234/supported_currencies",
            "supported_payment_methods": "/orders/ORD3pu1234/supported_payment_methods",
            "checkout": "/orders/ORD3pu1234/checkout",
            "refund": "/orders/ORD3pu1234/refund",
            "invalidate": "/orders/ORD3pu1234/invalidate"
        }
    }
```

Response (render_depth=2):
```
    HTTP 200 OK
```
```javascript
    {
        "id": "ORD545173f4b7d9a",
        "type": "order",
        "meta": {},
        "status": "CLOSED",
        "payment_instrument": "/cards/CC105b1275010dab2",
        "supported_payment_methods": [
            "VISA",
            "MASTERCARD",
            "AMEX",
            "PAYPAL",
            "ACH"
        ],
        "supported_currencies": [
            "USD",
            "EUR"
        ],
        "items": [
            {
                "id": "IT29aa943d5",
                "type": "item",
                "meta": {},
                "uri": "/inventory/IN7a33e0b3326e1bc",
                "status": "LOCKED",
                "unit_price": 4353,
                "currency": "USD",
                "quantity": 3
            }
        ],
        "balance": {
            "currency": "USD",
            "amount": 13059
        },
        "payments": [
            {
                "id": "CD2c62b80106f3",
                "type": "DEBIT",
                "payment_instrument_uri": "/cards/CC105b1275010dab2",
                "uri": "/debits/CD2c62b80106f3",
                "status": "SUCCEEDED",
                "amount": 13059
            }
        ],
        "links": {
            "self": "/orders/ORD3pu1234",
            "items": "/orders/ORD3pu1234/items",
            "payments": "/orders/ORD3pu1234/payments",
            "balance": "/orders/ORD3pu1234/balance",
            "supported_currencies": "/orders/ORD3pu1234/supported_currencies",
            "supported_payment_methods": "/orders/ORD3pu1234/supported_payment_methods",
            "checkout": "/orders/ORD3pu1234/checkout",
            "refund": "/orders/ORD3pu1234/refund",
            "invalidate": "/orders/ORD3pu1234/invalidate"
        }
    }
```


## Development and Testing

Getting set up:
```bash
# preferably in a virtualenv if developing locally
python setup.py develop
bin/bookie engine initialize
```

Run the tests:
```bash
nostests tests
```
