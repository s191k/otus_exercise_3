import functools
import unittest

import api
import scoring
# from api import ClientIDsField, DateField, CharField, PhoneField, GenderField, BirthDayField, EmailField, ArgumentsField
from api import *##рекурсия ??

# empty_values = ('', [], (), None, {})
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

    @cases([{"param": "123"}])
    def test_client_ids_cant_be_str(self, param):
        with self.assertRaises(Exception) as ex:
            self.client_ids = param

    @cases([{"param": 123}])
    def test_client_ids_cant_be_int(self, param):
        with self.assertRaises(Exception):
            self.client_ids = param

    @cases([{"param": ['1', '2', '3']}])
    def test_client_ids_cant_be_not_empty_array(self, param):
        with self.assertRaises(Exception):
            self.client_ids = param

    @cases([{"param": '2000.01.01'}])
    def test_date_field_cant_format_yymmdd(self, param):
        with self.assertRaises(Exception):
            self.date = param

    @cases([{"param": '01.01.2000'}])
    def test_date_field_can_format_ddmmyy(self,param):
        self.date = param

class OnlineScoreRequest(unittest.TestCase):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=True, nullable=True)

    @cases([{"param": 123}])
    def test_first_name_cant_be_int(self, param):
        with self.assertRaises(Exception):
            self.first_name = param

    @cases([{"param": 'tests'}])
    def test_first_name_can_be_str(self,param):
        self.first_name = param

    @cases([{"param": 123}])
    def test_last_name_cant_be_int(self, param):
        with self.assertRaises(Exception):
            self.last_name = param

    @cases([{"param": 'tests'}])
    def test_last_name_can_be_str(self,param):
        self.last_name = param

    @cases([{"param": 'tests@t@mail.ru'}])
    def test_email_can_have_only_one_at_symbol(self, param):
        with self.assertRaises(Exception):
            self.email = param

    def test_email_simple_example(self):
        self.email = 'tests@tmail.ru'

    def test_phone_len_cant_be_rather_than_11(self):
        with self.assertRaises(Exception):
            self.phone = '899'

    def test_phone_simple_example(self):
        self.phone = '79991231231'

    def test_birthday_bad_date_format(self):
        with self.assertRaises(Exception):
            self.birthday = '10/10/2000'

    def test_birthday_good_date_format(self):
        self.birthday = '10.10.2000'

    def test_gender_cant_be_rather_than_0_or_1(self):
        with self.assertRaises(Exception):
            self.gender = 4

    def test_gender_field_simple_example(self):
        self.gender = 1

class MethodRequest(unittest.TestCase):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    def test_account_cant_be_int(self):
        with self.assertRaises(Exception):
            self.account = 123

    def test_account_can_be_str(self):
        self.account = '123'

    def test_login_cant_be_int(self):
        with self.assertRaises(Exception):
            self.login = 123

    def test_login_can_be_str(self):
        self.login = '123'

    def test_token_field_bad(self):
        with self.assertRaises(Exception):
            self.token = 123

    def test_token_field_empty(self):
        with self.assertRaises(Exception):
            self.token = ''

    def test_token_field_good(self):
        self.token = '123'

    def test_arguments_field_bad(self):
        with self.assertRaises(Exception):
            self.arguments = 123

    def test_arguments_field_good(self):
        self.arguments = {'test1':'1','test2':'2','test3':'3'}

    def test_method_field_bad(self):
        with self.assertRaises(Exception):
            self.token.value_validate(123)

    def test_method_field_good(self):
        self.token = '123'

class OtherMethodsTests(unittest.TestCase):
    def test_online_score_handler_if_admin(self):
        response = api.online_score_handler('not_empty', 'admin','')
        self.assertEqual(({'score': 42}, 200), response)

    def test_is_admin(self):
        self.assertEqual(True, 'admin' == ADMIN_LOGIN)

    # def test_check_auth(self):
    #     pass

if __name__ == '__main__':
    unittest.main()
