from decimal import *
import requests
import hashlib
import json


# define the constants these are for debuging only
URL_INITIATE_TRANSACTION = 'http://127.0.0.1:5000/web'
URL_INITIATE_MOBILE_TRANSACTION = 'http://127.0.0.1:5000/mobile'


# URL_INITIATE_TRANSACTION = "https://www.paynow.co.zw/interface/initiatetransaction"
# URL_INITIATE_MOBILE_TRANSACTION = "https://www.paynow.co.zw/interface/remotetransaction"


class Paynow:

    def __init__(self, integration_id, integration_key,return_url=None,
                       result_url=None,
                       authemail=None,
                       phone=None):
        self.integration_id = integration_id
        self.integration_key = integration_key
        self.return_url = return_url
        self.result_url = result_url
        self.authemail = authemail
        self.phone = phone
        self.products = {}

    def __set_reference(self, reference):
    	self.__reference = reference if reference else None
    	return self.__reference


    def __set_response_from_paynow(self, response):
    	self.__from_paynow = self.__decrypt(response) if response else None
    	return self.__from_paynow

    def cart(self, products:dict):
        if type(products) != dict:
            raise AttributeError('Enter products as a dict')
        for desc, amount in products.items():
            if type(desc) != str and type(amount) != float:
                raise (TypeError('Enter valid description and amount'))
            self.products[desc] = amount
        return self.products

    def total(self):
        """ Returns total cost of all items in the transaction as float """
        with localcontext() as ctx:
            ctx.prec = 2 # convert to two decimal places
        amount =  sum(self.products[key] for key in self.products.keys())
        if amount <= 1:
        	raise ValueError('Totals must not be less than $1US')
        return float(Decimal(amount).quantize(Decimal('.01'), rounding=ROUND_UP))

    def send_payment(self, reference):
    	self.__set_reference(reference)
    	data = self.__build_request() # send tha data to Paynow
    	if all([data['authemail'], data['phone']]):
            # TODO put try except 
    		return self.__set_response_from_paynow(
                requests.post(URL_INITIATE_MOBILE_TRANSACTION, data=data))
    	# URL that handles web payments
    	return self.__set_response_from_paynow(requests.post(
    		                       URL_INITIATE_TRANSACTION, data=data))

    def display_cart(self):
        """Generate json representation of items in cart"""
        return json.dumps(self.products,sort_keys=True, indent=4)

    def poll_status_update(self):
    	if self.__from_paynow:
    		pollurl = self.__from_paynow.get('pollurl', False)
    		if pollurl:
    			resp = requests.post(URL_INITIATE_TRANSACTION, data=data)
    		return resp

    def check_payment_status(self):
    	if self.__from_paynow:
            if self.__from_paynow['Status']:
                return self.__from_paynow['Status']

    def __encrypt(self, data):
    	msg = ''
    	for key, value in data.items():
    		msg += str(value)
    	msg += self.integration_key.lower()
    	return hashlib.sha512(msg.encode('utf-8')).hexdigest().upper()

    def __decrypt(self, response):
        msg = dict(parse_qs(response.text))
        if not ('hash' in msg or 'HASH' in msg):
            raise ValueError('Message from Paynow must have a hash')
        for key, value in msg.items():
            msg[key] = value
        return msg

    def __build_request(self):
    	body = {
    		'id':self.integration_id,
    		'reference':self.__reference,
    		'amount':self.total(),
    		'additionalinfo':None,
    		'return_url':self.return_url,
    		'result_url':self.result_url,
    		'authemail':self.authemail,
    		'phone':self.phone,
    		'status':'Message',
    	}
    	body['hash'] = self.__encrypt(body)
    	return body
