import unittest
from paynow.core import Payment, InitResponse, StatusResponse, Paynow


class PaynowTestCase(unittest.TestCase):


    def setUp(self):
    	self.paynow = Paynow('id1234', 'key1234',
    		            return_url='www.test.com/payments',
    		            result_url='www.test.com/paymenturl')
    	self.paynow.create_payment('reference')
    	self.payment_web = Payment('reference')
    	self.payment_mobile = Payment('reference', auth_email='test@test.com',
    		                     phone='1234567')

    def tearDown(self):
        print(self.paynow.send(self.payment_web))

    def test_create_payment(self):
    	pass

    def test_send(self):
    	pass

    def test_process_update(self):
    	pass

    def test_transaction_status(self):
    	pass

    def test_add(self):
    	self.assertEqual(self.payment_web.add('honey', 12.24234), {'honey': 12.24234})

    def test_total(self):
    	pass

    def test_info(self):
    	pass


if __name__ == '__main__':
    unittest.main()