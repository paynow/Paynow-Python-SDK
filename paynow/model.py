import requests
import hashlib
from six.moves.urllib_parse import quote_plus, parse_qs


class HashMismatchException(Exception):
    """
    Exception thrown when hash from Paynow does not match locally generated hash
    """
    def __init__(self, message):
        super(HashMismatchException, self).__init__(message)

# TODO: Update status response class to support dictionary


class StatusResponse:
    paid=bool
    """
    bool: Boolean value indication whether the transaction was paid or not
    """

    status=str
    """
    str: The status of the transaction in Paynow
    """

    amount=float
    """
    float: The total amount of the transaction
    """

    reference=str
    """
    any: The unique identifier for the transaction
    """

    paynow_reference=str
    """
    any: Paynow's unique identifier for the transaction
    """
    hash=str
    """
    any: Hash of the transaction in paynow
    """

    def __status_update(self, data):
        """Parses the incoming status update from Paynow
        Args:
            data (any): The data from paynow
        """
        print('Not implemented')
        # TODO: Implement method

    def __init__(self, data, update):
        if update:
            self.__status_update(data)
        else:
            self.status = data['status'].lower()
            self.paid = self.status == 'paid'

            if 'amount' in data:
                self.amount = float(data['amount'])
            if 'reference' in data:
                self.reference = data['reference']
            if 'paynowreference' in data:
                self.paynow_reference = data['paynowreference']
            if 'hash' in data:
                self.hash = data['hash']


class InitResponse:
    """Wrapper class for response from Paynow during transaction initiation
    """

    success=bool
    """
    bool: Boolean indicating whether initiate request was successful or not
    """

    instructions=str
    """
    bool: Boolean indicating whether the response contains a url to redirect to
    """

    has_redirect=bool
    """
    bool: Boolean indicating whether the response contains a url to redirect to
    """

    hash=str
    """
    str: Hashed transaction returned from Paynow
    """

    redirect_url=str
    """
    str: The url the user should be taken to so they can make a payment
    """

    error=str
    """
    str: the error message from Paynow, if any
    """

    poll_url=str
    """
    str: The poll URL sent from Paynow
    """

    def __init__(self, data):
        # TODO return dict of kwargs

        self.status = data['status']
        self.success = data['status'].lower() != 'error'
        self.has_redirect = 'browserurl' in data
        self.hash = 'hash' in data

        if not self.success:
            self.error = data['error']
            return

        self.poll_url = data['pollurl']

        if self.has_redirect:
            
            self.redirect_url = data['browserurl']

        if 'instructions' in data:
            self.instruction = data['instructions']

    def __repr__(self):
        '''Print friendly message, especially on errors'''

        return self.status


class Payment:
    """Helper class for building up a transaction before sending it off to Paynow
    Attributes:
        reference (str): Unique identifier for the transaction
        items ([]): Array of items in the 'cart'
    """

    reference=str
    """
    str: Unique identifier for the transaction
    """

    items=[]
    """
    []: Array of items in the 'cart'
    """

    auth_email=str
    """
    str: The user's email address.
    """

    def __init__(self, reference, auth_email):
        self.reference = reference
        self.auth_email = auth_email
        # auto-check to ensure clear list
        #self.clearCart()

    def add(self, title: str, amount: float):
        """ Add an item to the 'cart'
        Args:
            title (str): The name of the item
            amount (float): The cost of the item
        """
        # FIXME: Dont do this
        self.items.clear()
        self.items.append([title, amount])
        return self

    def clearCart(self):
        '''
            clear all added items
        '''
        self.items.clear()

    def total(self):
        """Get the total cost of the items in the transaction
        Returns:
            float: The total
        """
        total = 0.0
        for item in self.items:
            total += float(item[1])

        return total

    def info(self):
        """Generate text which represents the items in cart
        Returns:
            str: The text representation of the cart
        """
        out = ""
        for item in self.items:
            out += (item[0] + ", ")
        return out

    def __repr__(self):
        # TODO: how woll this be presented when printed
        # information is too vague
        pass


class Paynow:
    """Contains helper methods to interact with the Paynow API
    Attributes:
        integration_id (str): Merchant's integration id.
        integration_key (str):  Merchant's integration key.
        return_url (str):  Merchant's return url
        result_url (str):  Merchant's result url
    Args:
        integration_id (str): Merchant's integration id. (You can generate this in your merchant dashboard)
        integration_key (str):  Merchant's integration key.
        return_url (str):  Merchant's return url
        result_url (str):  Merchant's result url
    """

    URL_INITIATE_TRANSACTION = "https://www.paynow.co.zw/interface/initiatetransaction"
    """
    str: Transaction initation url (constant)
    """

    URL_INITIATE_MOBILE_TRANSACTION = "https://www.paynow.co.zw/interface/remotetransaction"
    """
    str: Transaction initation url (constant)
    """

    integration_id=str
    """
    str: Merchant's integration id
    """

    integration_key=str
    """
    str: Merchant's integration key
    """

    return_url = ""
    """
    str: Merchant's return url
    """

    result_url = ""
    """
    str: Merchant's result url
    """
    # is it necessary to have return and results url ?
    # why not just combine these two; kill two birds with one stone
    # Leave the autonomy to the merchant ie merchant knows what to do with
    # a successful payment else its an error, merchant will debug, paynow
    # provides information about error

    def __init__(self, integration_id, integration_key,
                 return_url='https://www.google.com', result_url='https://www.google.com'):
        self.integration_id = integration_id
        self.integration_key = integration_key
        self.return_url = return_url
        self.result_url = result_url

    def set_result_url(self, url):
        """Sets the url where the status of the transaction will be sent when payment status is updated within Paynow
        Args:
            url (str): The url where the status of the transaction will be sent when
                payment status is updated within Paynow
        """
        self.result_url = url

    def set_return_url(self, url):
        """Sets the url where the user will be redirected to after they are done on Paynow
        Args:
            url (str): The url to redirect user to once they are done on Paynow's side
        """
        self.return_url = url

    def create_payment(self, reference, auth_email):
        """Create a new payment
        Args:
            reference (str): Unique identifier for the transaction.
            auth_email (str): The phone number to send to Paynow. This is required for mobile transactions
        Note:
            Auth email is required for mobile transactions.
        Returns:
            Payment: An object which provides an easy to use API to add items to Payment
        """
        return Payment(reference, auth_email)

    def send(self, payment):
        """Send a transaction to Paynow
        Args:
            payment (Payment): The payment object with details about transaction
        Returns:
            StatusResponse: An object with information about the status of the transaction
        """
        return self.__init(payment)

    def send_mobile(self, payment, phone, method):
        """Send a mobile transaction to Paynow
        Args:
            payment (Payment): The payment object with details about transaction
            phone (str): The phone number to send to Paynow
            method (str): The mobile money method being employed
        Returns:
            StatusResponse: An object with information about the status of the transaction
        """
        return self.__init_mobile(payment, phone, method)

    def process_status_update(self, data):
        """This method parses the status update data from Paynow into an easier to use format
        Args:
            data (dict): A dictionary with the data from Paynow. This is the POST data sent by Paynow
                to your result url after the status of a transaction has changed (see Django usage example)
        Returns:
            StatusResponse: An object with information about the status of the transaction
        """
        return StatusResponse(data, True)

    def __init(self, payment):
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

    def __init_mobile(self, payment, phone, method):
        """Initiate a mobile transaction
        Args:
            payment (Payment): The payment object with details about transaction
            phone (str): The phone number to send to Paynow
            method (str): The mobile money method being employed
        Returns:
            InitResponse: An object with misc information about the initiated transaction i.e
            redirect url (if available), status of initiation etc (see `InitResponse` declaration above)
        """
        if payment.total() <= 0:
            raise ValueError('Transaction total cannot be less than 1')

        if not payment.auth_email or len(payment.auth_email) <= 0:
            raise ValueError('Auth email is required for mobile transactions. You can pass the auth email as the '
                             'second parameter in the create_payment method call')

        # Build up the object
        data = self.__build_mobile(payment, phone, method)

        # Save response from Paynow
        response = requests.post(
            self.URL_INITIATE_MOBILE_TRANSACTION, data=data)

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

        _parsed = parse_qs(response.text)

        response_object = self.__rebuild_response(_parsed)

        return StatusResponse(
            response_object, False)

    def __build(self, payment):
        """Build up a payment into the format required by Paynow
        Args:
            payment (Payment): The payment object to format
        Returns:
            dict: A dictionary properly formatted in the format required by Paynow
        """
        body = {
            "reference": payment.reference,
            "amount": payment.total(),
            "id": self.integration_id,
            "additionalinfo": payment.info(),
            "authemail": payment.auth_email or "",
            "status": "Message"
        }

        for key, value in body.items():
            body[key] = quote_plus(str(value))
        
        body['resulturl'] = self.result_url
        body['returnurl'] = self.return_url
        body['hash'] = self.__hash(body, self.integration_key)

        return body

    def __build_mobile(self, payment, phone, method):
        """Build up a mobile payment into the format required by Paynow
        Args:
            payment (Payment): The payment object to format
            phone (str): The phone number to send to Paynow
            method (str): The mobile money method being employed
        Note:
            Currently supported methods are `ecocash` and `onemoney`
        Returns:
            dict: A dictionary properly formatted in the format required by Paynow
        """
        body = {
            "reference": payment.reference,
            "amount": payment.total(),
            "id": self.integration_id,
            "additionalinfo": payment.info(),
            "authemail":  payment.auth_email,
            "phone": phone,
            "method": method,
            "status": "Message"
        }

        for key, value in body.items():
            if(key == 'authemail'):
                continue

            body[key] = quote_plus(str(value))  # Url encode the

        body['resulturl'] = self.result_url
        body['returnurl'] = self.return_url
        body['hash'] = self.__hash(body, self.integration_key)

        return body

    def __hash(self, items, integration_key):
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

        return hashlib.sha512(out.encode('utf-8')).hexdigest().upper()

    def __verify_hash(self, response, integration_key):
        """Verify the hash coming from Paynow
        Args:
            response (dict): The response from Paynow
            integration_key (str): Merchant integration key to use during hashing
        """
        if('hash' not in response):
            raise ValueError("Response from Paynow does not contain a hash")

        old_hash = response['hash']
        new_hash = self.__hash(response, integration_key)

        return old_hash == new_hash

    def __rebuild_response(self, response):
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
