# Paynow Zimbabwe Python SDK

Python SDK for Paynow Zimbabwe's API

# Prerequisites

This library has a set of prerequisites that must be met for it to work

1.  requests

# Installation

Install the library using pip

```sh
$ pip install paynow
```

and import the Paynow class into your project

```python
	from paynow import Paynow

	# Do stuff
```

---

# Usage example

Create an instance of the Paynow class optionally setting the result and return url(s)

```python
paynow = Paynow(
	'INTEGRATION_ID',
	'INTEGRATION_KEY',
	'http://google.com',
	'http://google.com'
	)
```

Create a new payment passing in the reference for that payment (e.g invoice id, or anything that you can use to identify the transaction and the user's email address

```python
payment = paynow.create_payment('Order #100', 'test@example.com')
```

You can then start adding items to the payment

```python
# Passing in the name of the item and the price of the item
payment.add('Bananas', 2.50)
payment.add('Apples', 3.40)
```

When you're finally ready to send your payment to Paynow, you can use the `send` method in the `paynow` object.

```python
# Save the response from paynow in a variable
response = paynow.send(payment)
```

The response from Paynow will b have some useful information like whether the request was successful or not. If it was, for example, it contains the url to redirect the user so they can make the payment. You can view the full list of data contained in the response in our wiki

If request was successful, you should consider saving the poll url sent from Paynow in the database

```python
if response.success:

    # Get the link to redirect the user to, then use it as you see fit
	link = response.redirect_url

	# Get the poll url (used to check the status of a transaction). You might want to save this in your DB
	pollUrl = response.poll_url
```

---

> Mobile Transactions

If you want to send an express (mobile) checkout request instead, the only thing that differs is the last step. You make a call to the `send_mobile` in the `paynow` object
instead of the `send` method.

The `send_mobile` method unlike the `send` method takes in two additional arguments i.e The phone number to send the payment request to and the mobile money method to use for the request. **Note that currently only ecocash is supported**

```python
# Save the response from paynow in a variable
response = paynow.send_mobile(payment, '0777777777', 'ecocash')
```

The response object is almost identical to the one you get if you send a normal request. With a few differences, firstly, you don't get a url to redirect to. Instead you instructions (which ideally should be shown to the user instructing them how to make payment on their mobile phone)

```python
if(response.success) :
	# Get the poll url (used to check the status of a transaction). You might want to save this in your DB
    poll_url = response.poll_url

    instructions = response.instructions
```

# Checking transaction status

The SDK exposes a handy method that you can use to check the status of a transaction. Once you have instantiated the Paynow class.

```python
# Check the status of the transaction with the specified poll url
# Now you see why you need to save that url ;-)
status = paynow.check_transaction_status(poll_url)

if status.paid() :
	# Yay! Transaction was paid for. Update transaction?
else :
	# Handle that
```

# Full Usage Example

```python
from paynow import Paynow


paynow = Paynow(
	'INTEGRATION_ID',
	'INTEGRATION_KEY',
	'http://google.com',
	'http://google.com'
	)

payment = paynow.create_payment('Order', 'test@example.com')

payment.add('Payment for stuff', 1)

response = paynow.send_mobile(payment, '0777832735', 'ecocash')


if(response.success):
    poll_url = response.poll_url

    print("Poll Url: ", poll_url)

    status = paynow.check_transaction_status(poll_url)

    time.sleep(30)

    print("Payment Status: ", status.status)
```
