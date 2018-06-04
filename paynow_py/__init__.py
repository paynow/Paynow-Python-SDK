import requests
import hashlib
from urllib.parse import quote_plus, parse_qs


# TODO: Verify hashes at all interactions with server
# TODO: Update status response class to support dictionary

class StatusResponse:
    paid: bool

    amount: float

    reference: any

    def __status_update(self, data):
        print('Not implemented')  # TODO: Implement

    def __init__(self, data, update):
        if update:
            self.__status_update(data)
        else:
            self.paid = data['status'][0].lower() == 'paid'

            if 'amount' in data:
                self.amount = float(data['amount'][0])
            if 'reference' in data:
                self.amount = data['reference'][0]


class InitResponse:
    """
    Boolean indicating whether initiate request was successful or not
    """
    success: bool

    """
    Boolean indicating whether the response contains a url to redirect to
    """
    has_redirect: bool

    """
    The url the user should be taken to so they can make a payment
    """
    redirect_url: bool

    """
    The error message from Paynow, if any
    """
    error: str

    """
    The poll URL sent from Paynow
    """
    poll_url: str

    def __init__(self, data):
        self.success = data['status'][0].lower() != 'error'
        self.has_redirect = 'browserurl' in data != 'error'

        if not self.success:
            self.error = data['error'][0]

        if self.has_redirect:
            self.redirect_url = data['browserurl'][0]
            self.poll_url = data['pollurl'][0]


class Payment:
    reference: str = ""

    items: [] = []

    def __init__(self, reference: str):
        self.reference = reference

    def add(self, title: str, amount: float):
        # TODO: Validate
        self.items.append([title, amount])
        return self

    """
    Get the total of the items in the transaction
    :returns int
    """

    def total(self):
        total = 0.0
        for item in self.items:
            total += float(item[1])
        return total

    def info(self):
        out = ""
        for item in self.items:
            print(item)
            out += (item[0] + ", ")
        return out


class Paynow:
    URL_INITIATE_TRANSACTION = "https://paynow.webdevworld.com/interface/initiatetransaction"
    """
    :var Merchant's integration id:
    """
    integrationId: str = ""

    """
    :var Merchant's integration key:
    """
    integrationKey: str = ""

    """
    :var Merchant's return url:
    """
    returnUrl = ""

    """
    :var Merchant's result url:
    """
    resultUrl = ""

    """
    Default constructor
    """

    def __init__(self, integration_id, integration_key):
        self.integrationId = integration_id
        self.integrationKey = integration_key

    """
    Sets the url where the status of the transasction will be sent wo
    """

    def set_result_url(self, url: str):
        self.resultUrl = url

    def set_return_url(self, url: str):
        self.returnUrl = url

    def create_payment(self, reference: str):
        return Payment(reference)

    def send(self, payment: Payment):
        return self.__init(payment)

    def process_status_update(self, data):
        return StatusResponse(data, True)

    def __init(self, payment: Payment):
        if payment.total() <= 0:
            raise ValueError('Transaction total cannot be less than 1')

        data = self.__build(payment)

        response = requests.post(self.URL_INITIATE_TRANSACTION, data=data)

        return InitResponse(
            parse_qs(response.text
                     ))

    def check_transaction_status(self, poll_url):
        response = requests.post(self.URL_INITIATE_TRANSACTION, data={})

        return StatusResponse(
            parse_qs(response.text
                     ))

    def __build(self, payment: Payment):
        body = {
            "resulturl": self.resultUrl,
            "returnurl": self.returnUrl,
            "reference": payment.reference,
            "amount": payment.total(),
            "id": self.integrationId,
            "additionalinfo": payment.info(),
            "authemail": "",
            "status": "Message"
        }
        body['hash'] = self.__hash(body, self.integrationKey)

        for key, value in body.items():
            body[key] = quote_plus(str(value))

        return body



    """
    Generates a SHA512 hash of the transaction
    """
    def __hash(self, items: {}, integrationKey):
        out = ""
        for key, value in items.items():
            out += quote_plus(str(value))
        out += integrationKey

        return hashlib.sha512(out.encode('utf-8')).hexdigest().upper()
