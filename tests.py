import functools
import unittest

import api
from api import ClientIDsField, DateField, CharField, PhoneField, GenderField, BirthDayField, EmailField, ArgumentsField

def cases(cases):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args):
            for c in cases:
                new_args = args + (c if isinstance(c, tuple) else (c,))
                f(*new_args)
        return wrapper
    return decorator

class ClientsInterestsRequestTests(unittest.TestCase):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    @cases({"param": "123"})
    def test_client_ids_filed_bad(self, param):
        with self.assertRaises(Exception):
            self.client_ids = param

    @cases({"param": ""})
    def test_client_ids_filed_empty(self, param):
        with self.assertRaises(Exception):
            self.client_ids = param

    @cases({"param": [1, 2, 3]})
    def test_client_ids_filed_good(self, param):
        with self.assertRaises(Exception):
            self.client_ids = param

    ##should delete ?
    @cases([{"param": "123"},
            {"param": ""},
            {"param": [1, 2, 3]}])
    def test_client_ids_field(self, param):
        with self.assertRaises(Exception):
            print(param)

            self.client_ids = param
            print(param)
            # print(ex)


    @cases({"param": '2000.01.01'})
    def test_date_field_field_bad(self, param):
        with self.assertRaises(Exception):
            self.date = param

    @cases({"param": '01.01.2000'})
    def test_date_field_field_good(self, param):
        self.date = param

class OnlineScoreRequest(unittest.TestCase):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=True, nullable=True)

    @unittest.expectedFailure
    @cases({"param": 123})
    def test_first_name_field_bad(self):
        self.first_name = 123

    @cases({"param": 'tests'})
    def test_first_name_field_good(self, param):
        self.first_name = param

    @unittest.expectedFailure
    @cases({"param": 123})
    def test_last_name_field_bad(self, param):
        self.last_name = param

    @cases({"param": 'tests'})
    def test_last_name_field_good(self, param):
        self.last_name = param

    @unittest.expectedFailure
    @cases({"param": 'tests@t@mail.ru'})
    def test_email_field_bad(self, param):
        self.email = param

    @cases({"param": 'tests@tmail.ru'})
    def test_email_field_good(self, param):
        self.email = param

    @unittest.expectedFailure
    def test_phone_field_bad(self):
        self.phone = '899'

    def test_phone_field_good(self):
        self.phone = '79991231231'

    @unittest.expectedFailure
    def test_birthday_field_bad(self):
        self.birthday = '10/10/2000'

    def test_birthday_field_good(self):
        self.birthday = '10.10.2000'

    @unittest.expectedFailure
    def test_gender_field_bad(self):
        self.gender = 4

    def test_gender_field_good(self):
        self.gender = 1

class MethodRequest(unittest.TestCase):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @unittest.expectedFailure
    def test_account_field_bad(self):
        self.account = 123

    def test_account_field_good(self):
        self.account = '123'

    @unittest.expectedFailure
    def test_login_field_bad(self):
        self.login = 123

    def test_login_field_good(self):
        self.login = '123'

    @unittest.expectedFailure
    def test_token_field_bad(self):
        self.token = 123

    @unittest.expectedFailure
    def test_token_field_empty(self):
        self.token = ''

    def test_token_field_good(self):
        self.token = '123'

    @unittest.expectedFailure
    def test_arguments_field_bad(self):
        self.arguments = 123

    def test_arguments_field_good(self):
        self.arguments = {'test1':'1','test2':'2','test3':'3'}

    @unittest.expectedFailure
    def test_method_field_bad(self):
        # self.token = b''
        self.token.value_validate(123)

    def test_method_field_good(self):
        self.token = '123'

if __name__ == '__main__':
    unittest.main()
