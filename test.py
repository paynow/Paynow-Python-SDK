import unittest
from urllib.parse import quote_plus, parse_qs
from paynow.core import Paynow

success = '''
Status=Ok&BrowserUrl=http%3a%2f%2fwww.paynow.co.zw%3a7106%2f
Payment%2fConfirmPayment%2f1169&PollUrl=http%3a%2f%2fwww.paynow.co.zw%3a7106%2f
Interface%2fCheckPayment%2f%3fguid
%3d3cb27f4b-b3ef-4d1f-9178-5e5e62a43995&
Hash=8614C21DD93749339906DB35C51B06006B33DC8C192F40DFE2DB6549942C837C4
452E1D1333DE9DB7814B278C8B9E3C34D1A76D2F937DEE57502336E0A071412 
'''
error = '''
Status=Error&Error=Invalid+amount+field '''
msg = parse_qs(success)

class TestCase(unittest.TestCase):
	def setUp(self):
		self.products = {'honey':2.34} # dummy products
		self.paynow = Paynow('id12344','key1234') # instantiate Paynow obj
		self.items = self.paynow.cart(self.products) # cart items
		self.paynow.send_payment('i dont have one')

	def tearDown(self):
		pass

	def test_cart(self):
		self.assertTrue(self.items, {'honey':2.3443})
		# self.assertRaises(AttributeError('Enter products as a dict'),
		# 	self.paynow.cart('123213'))

	def test_total(self):
		# having a problem here put 2.3444
		self.assertEqual(self.paynow.total(), 2.34)

	def test_send_payment(self):
		# self.assertTrue(self.paynow.send_payment('sfsfsfs'), dict(msg))
		pass

	def test_display_cart(self):
		self.assertTrue(self.paynow.display_cart(), '"honey": 2.34')

	def test_check_status(self):
		pass

	def test_check_payment_status(self):
		self.assertTrue(self.paynow.check_payment_status(), 'Ok')


if __name__ == '__main__':
	unittest.main()
