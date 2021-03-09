# test new lib
from paynow import Paynow
import time
import uuid
from random import randint
import requests
from six.moves.urllib_parse import quote_plus, parse_qs

TEST = False

def build_response(response):
    res = {}

    for key, value in response.items():
        res[key] = str(value[0])

    return res

def test():
    print(' ------------------- testing --------------------')
    PAYNOW_ID    = ''
    PAYNOW_KEY   = ''
    PAYNOW_EMAIL = ''

    result_url = ""

    print('=== tesing poll url ====')

    # test poll url for known url
    # for a paid transaction: poll url
    paid =''

    # cancelled
    cancelled = ''


    response = requests.post(paid, data={})

    print(response.text)

    parsed_data = parse_qs(response.text)
    print(parsed_data)

    resp = build_response(parsed_data)
    print(resp)

    print('==== done polling =====')

    api = Paynow(
                PAYNOW_ID,
                PAYNOW_KEY,
                result_url,
                result_url,
            )

    amount = 1

    add_details = f'testing-{randint(5, 100)}'

    createPayment = api.create_payment(str(uuid.uuid4()), PAYNOW_EMAIL)
                    
    createPayment.add(add_details, float(amount))

    # 0771111111 paynow mobile checkout test #
    num = '0771111111'
    num2 = '0772222222'
    num3 = '0773333333'
    num4 = '0774444444'
    
    mynum = '07xxxxxxx'

    response = api.send_mobile(createPayment, mynum, 'ecocash')

    print(response.status)

    print(response.success)

    print(response)

    if response.success:
        poll_url = response.poll_url

        print("=== poll url: ", poll_url)
        
        status = api.check_transaction_status(poll_url)
        print('[INFO-BEFORE-WAITING] Status returned. Has paid? : ', status.paid, status.status)

        print('=== waiting for 60 sec ====')
        time.sleep(60)

        resp = requests.get(poll_url)
        print('=== get response on poll_url: ', resp.text)

        status = api.check_transaction_status(poll_url)
        print('[INFO] Status returned. Has paid? : ', status.paid, status.status)

        print('=== status: ', status)


    print(' ------------------- finished testing --------------------')

if TEST:
    test()

else:
    pass