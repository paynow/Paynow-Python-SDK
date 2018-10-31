from decimal import *
import unittest



class PaynowTestCase(unittest.TestCase):
	def setUp():
		pass

	def tearDown():
		pass



def total():
	items = [['a',1.03],['b',2],['b',2],['b',2],['b',2]]


	with localcontext() as ctx:
	    ctx.prec = 2 # convert to two decimal places
	amount =  sum([items[index][1] for index in range(len(items))])
	return Decimal(amount).quantize(Decimal('.01'), rounding=ROUND_UP)

s = total()
print(s)
print(type(s))

if __name__ == '__main__':
	unittest.main()