from urllib.parse import quote_plus
import base64


class ButtonGenerator(object):
    """Paynow Button Generator"""

    BUTTONS = {
        'paynow' : 'https://www.paynow.co.zw/Content/Buttons/Medium_buttons/button_pay-now_medium.png',
        'buynow' : 'https://www.paynow.co.zw/Content/Buttons/Medium_buttons/button_buy-now_medium.png',
        'donate' : 'https://www.paynow.co.zw/Content/Buttons/Medium_buttons/button_donate_medium.png'
    }



    def __encode_payment(self,email, reference, amount, lock, **extra) -> str:
        """
        Build base64 encoded payment payload

        Args:
            email (str) : Merchant's Paynow email address
            reference (any): The unique identifier for the transaction
            amount (float): Amount to charge
            lock (bool): Lock form

        Returns:
            str: Base64 encoded payload
        """

        strresult = f"search={email}&amount={amount}&reference={reference}&l={('2', '1')[lock]}"
        return quote_plus(base64.b64encode(bytes(strresult, "utf8")))

    def __image(self,data):
        """
        Generate Image Button

        Args:
            data (dict): Payload

        Returns:
            str: HTML code for Paynow Button
        """
        payment = self.__encode_payment(**data)

        return f"""<a href='https://www.paynow.co.zw/Payment/Link/?q={payment}' target='_blank'>
                <img src='{self.BUTTONS[data.get("text", "paynow")]}' style='border:0' /></a>"""

    def __text(self, data):
        """
        Generate Paynow HTML Text

        Args:
            data (dict): Payload

        Returns:
            str: HTML code for Paynow Text
        """
        payment = self.__encode_payment(**data)
        return f"<a href='https://www.paynow.co.zw/Payment/Link/?q={payment}' target='_blank'>{data.get('text', 'paynow').capitalize()}</a>"

    def __url(self, data):
        """
        Generate Paynow Url

        Args:
            data (dict): Payload

        Returns:
            str: Paynow payment URL
        """
        payment = self.__encode_payment(**data)
        return f"https://www.paynow.co.zw/Payment/Link/?q={payment}"


    def button_generator(self, data):
        """
        Paynow Button Generator

        Args:
            data (dict): Payload

        Returns:
            str: Paynow Button
        """
        BUTTON_TYPE = {
        'image' : self.__image,
        'text' : self.__text,
        'url' : self.__url
        }

        return BUTTON_TYPE[data['type']](data)
