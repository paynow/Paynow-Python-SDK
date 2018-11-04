from decimal import *
import json
import requests
import hashlib
from urllib.parse import quote_plus, parse_qs

# define the constants 
URL_INITIATE_TRANSACTION = "https://www.paynow.co.zw/interface/initiatetransaction"
URL_INITIATE_MOBILE_TRANSACTION = "https://www.paynow.co.zw/interface/remotetransaction"

class HashMismatchException(Exception):
    """Exception thrown if Paynow's hash  doesnt match merchant hash"""
    def __init__(self, message):
        super(HashMismatchException, self).__init__(message)


# TODO: Update status response class to support dictionary
class StatusResponse(dict):
    """docstring for StatusResponse"""

    paid: bool
    """
    bool: Boolean value indication whether the transaction was paid or not
    """

    status: str
    """
    str: The status of the transaction in Paynow
    """

    amount: float
    """
    float: The total amount of the transaction
    """

    reference: any
    """
    any: The unique identifier for the transaction
    """

    paynow_reference: any
    """
    any: Paynow's unique identifier for the transaction
    """
    hash: str
    """
    any: Hash of the transaction in paynow
    """

    def __init__(self, data, update, **kw):
        self.__dict__.update(kw)

        if update:
            self.data = data

        self.data['status'] = data['status'].lower()
        self.data['paid'] = data['status'] == 'paid'

        if 'amount' in data:
            self.data['amount'] = float(data['amount'])
        if 'reference' in data:
            self.data['reference'] = data['reference']
        if 'paynowreference' in data:
            self.data['paynow_reference'] = data['paynowreference']
        if 'hash' in data:
            self.data['hash'] = data['hash']


class InitResponse:
    """Wrapper class for response from Paynow during transaction initiation

    """

    success: bool
    """
    bool: Boolean indicating whether initiate request was successful or not
    """

    instructions: str
    """
    bool: Boolean indicating whether the response contains a url to redirect to
    """

    has_redirect: bool
    """
    bool: Boolean indicating whether the response contains a url to redirect to
    """

    hash: str
    """
    str: Hashed transaction returned from Paynow
    """

    redirect_url: str
    """
    str: The url the user should be taken to so they can make a payment
    """

    error: str
    """
    str: he error message from Paynow, if any
    """

    poll_url: str
    """
    str: The poll URL sent from Paynow
    """

    def __init__(self, data):
        self.status = data['status']
        self.success = data['status'].lower() != 'error'
        self.has_redirect = 'browserurl' in data
        self.hash = 'hash' in data

        if not self.success:
            return

        self.poll_url = data['pollurl']

        if not self.success:
            self.error = data['error']

        if self.has_redirect:
            self.redirect_url = data['browserurl']

        if 'instructions' in data:
            self.instruction = data['instructions']

class Payment:
    """Helper class for building up a transaction before sending it off to Paynow

    Attributes:
        reference (str): Unique identifier for the transaction
        items ([]): Array of items in the 'cart'
        auth_email (str): The user's email address.
    """

    def __init__(self, reference: str, auth_email: str=None, phone=None):
        self.reference = reference
        self.auth_email = auth_email
        self.phone = phone
        self.items = {} # to store cart items


    def add(self, title: str, amount: float):
        """ Add an item to the 'cart'

        Args:
            title (str): The name of the item 
            amount (float): The cost of the item
        """
        if type(title) == str and type(amount) == float:
            self.items[title] = amount
            return self.items
        else:
            raise ValueError('title must be a string, amount a float')


    def total(self):
        """ Returns total cost of all items in the transaction as float """

        with localcontext() as ctx:
            ctx.prec = 2 # convert to two decimal places
        amount =  sum(self.items[key] for key in self.items.keys())
        return Decimal(amount).quantize(Decimal('.01'), rounding=ROUND_UP)

    def info(self):
        """Generate json which represents the items in cart"""
        return json.dumps(self.items,sort_keys=True, indent=4)




class Paynow:

    def __init__(self, integration_id, integration_key,return_url=None,
                       result_url=None,
                       auth_email=None,
                       phone=None):
        self.integration_id = integration_id
        self.integration_key = integration_key
        self.return_url = return_url
        self.result_url = result_url
        self.auth_email = auth_email
        self.phone = phone

    def create_payment(self, reference: str):
        if all([self.auth_email, self.phone]):
            return Payment(reference, auth_email=self.auth_email,
                           phone=self.phone)
        
        return Payment(reference)

    def send(self, payment: Payment):
        """Send a transaction to Paynow

        Args:
            payment (Payment): The payment object with details about transaction

        Returns:
            StatusResponse: An object with information about the status of the transaction
        """

        return self.__init(payment)

    def process_status_update(self, data: object) -> StatusResponse:
        """This method parses the status update data from Paynow into an easier to use format

        Args:
            data (dict): A dictionary with the data from Paynow. This is the POST data sent by Paynow 
                to your result url after the status of a transaction has changed (see Django usage example)

        Returns: 
            StatusResponse: An object with information about the status of the transaction

        """
        return StatusResponse(data, True)

    def __init(self, payment: Payment):
        """Initiate the given transaction with Paynow

        Args:
            payment (Payment): The payment object with details about transaction

        Returns:
            InitResponse: An object with misc information about the initiated transaction i.e
            redirect url (if available), status of initiation etc (see `InitResponse` declaration above)
        """
        if payment.total() <= 0:
            raise ValueError('Transaction total cannot be less than 1')
        # Build up the object
        data = self.__build(payment)

        #check if its mobile
        if (data['phone'] and data['method']):
            if not data['auth_email'] or len(data['auth_email']) <= 0:
                raise ValueError('Auth email is required for mobile transactions. You can pass the auth email as the '
                                 'second parameter in the create_payment method call')
            # Save response from Paynow
            response = requests.post(self.URL_INITIATE_MOBILE_TRANSACTION, data=data)

        # Save response from Paynow
        response = requests.post(self.URL_INITIATE_TRANSACTION, data=data)


        # Reconstruct the response into key-value pairs
        response_object = self.__rebuild_response(parse_qs(response.text))

        # If an error was encountered return a new InitResponse object without validating hash since hash is not
        # generated for error responses
        if str(response_object['status']).lower() == 'error':
            return InitResponse(response_object)

        # Verify the hash from Paynow with the locally generated one
        if not self.__verify_hash(response_object, self.integration_key):
            raise HashMismatchException("Hashes do not match")

        # Create a new InitResponse object object passing in the data from Paynow
        return InitResponse(response_object)

    def check_transaction_status(self, poll_url):
        """Check the status transaction of the transaction with the given poll url

        Args:
            poll_url (str): Poll url of the transaction 

        Returns:
            StatusResponse: An object with information about the status of the transaction

        """
        response = requests.post(poll_url, data={})

        response_object = self.__rebuild_response(parse_qs(response.text))

        return StatusResponse(
            response_object, False)


    def __build(self, payment: Payment):
        """Build up a payment into the format required by Paynow

        Args:
            payment (Payment): The payment object to format

        Returns:
            dict: A dictionary properly formatted in the format required by Paynow

        """
        body = {
            "resulturl": self.result_url,
            "returnurl": self.return_url,
            "reference": payment.reference,
            "amount": payment.total(),
            "id": self.integration_id,
            "additionalinfo": payment.info(),
            "authemail": payment.auth_email,
            "phone": payment.phone,
            "method": payment.method,
            "status": "Message"
        }

        # check if they contain anything else delete them
        if not (body['phone'] and body['method']):
            del body['phone'] #delete these fields in body
            del body['method'] #delete these fields in body

        for key, value in body.items():
            try:
                body[key] = quote_plus(str(value))
            except Exception as e:
                pass


        body['hash'] = self.__hash(body, self.integration_key)

        return body


    def __hash(self, items: {}, integration_key: str):
        """Generates a SHA512 hash of the transaction

        Args:
            items (dict): The transaction dictionary to hash
            integration_key (str): Merchant integration key to use during hashing

        Returns:
            str: The hashed transaction
        """
        out = ""
        for key, value in items.items():
            if(str(key).lower() == 'hash'):
                continue

            out += str(value)

        out += integration_key.lower()
        # using decode method from python docs ignore if already utf-8
        return hashlib.sha512(out.decode('utf-8', 'ignore')).hexdigest().upper()

    def __verify_hash(self, response: {}, integration_key: str):
        """Verify the hash coming from Paynow

        Args:
            response (dict): The response from Paynow
            integration_key (str): Merchant integration key to use during hashing

        """
        if('hash' not in response):
            raise ValueError("Response from Paynow does not contain a hash")

        old_hash = response['hash']
        new_hash = self.__hash(response, integration_key)

        return new_hash == new_hash

    def __rebuild_response(self, response: {}):
        """
        Rebuild a response into key value pairs (as opposed to nested array returned from parse_qs)

        Args:
            response (dict): The response from Paynow

        Returns:
            dict: Key value pairs of the data from Paynow
        """
        res = {}

        for key, value in response.items():
            res[key] = str(value[0])

        return res


