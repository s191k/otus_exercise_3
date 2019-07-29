import unittest

import api
from api import ClientIDsField, DateField, CharField, PhoneField, GenderField, BirthDayField, EmailField, ArgumentsField

class ClientsInterestsRequestTests(unittest.TestCase):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    @unittest.expectedFailure
    def test_client_ids_filed_bad(self):
        self.client_ids = '123'

    @unittest.expectedFailure
    def test_client_ids_filed_empty(self):
        self.client_ids = '123'

    def test_client_ids_filed_good(self):
        with self.assertRaises(AssertionError) as ex:
            self.client_ids = ['1', '2', '3']
            print(ex)
        print('end')

    @unittest.expectedFailure
    def test_date_field_field_bad(self):
        self.date = '2000.01.01'

    def test_date_field_field_good(self):
        self.date = '01.01.2000'

class OnlineScoreRequest(unittest.TestCase):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=True, nullable=True)

    @unittest.expectedFailure
    def test_first_name_field_bad(self):
        self.first_name = 123

    def test_first_name_field_good(self):
        self.first_name = 'tests'

    @unittest.expectedFailure
    def test_last_name_field_bad(self):
        self.last_name = 123

    def test_last_name_field_good(self):
        self.last_name = 'tests'

    @unittest.expectedFailure
    def test_email_field_bad(self):
        self.email = 'tests@t@mail.ru'

    def test_email_field_good(self):
        self.email = 'tests@tmail.ru'

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

    # def test_parse_response_json(self):
    #     method_request, online_score_request, clients_interests_request, errors = api.parse_response_json(
    #         {'body': {'account': 'horns&hoofs', 'login': 'h&f', 'method': 'online_score',
    #          'token': '55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af3',
    #          'arguments': {'phone': '79175002040', 'email': 'stupnikov@otus.ru', 'first_name': '11',
    #          'last_name': 'Ступников', 'birthday': '01.01.1990', 'gender': 1}}})
    #     self.assertTrue(method_request is not None)
    #     self.assertTrue(online_score_request is not None)
    #     self.assertTrue(clients_interests_request is None)
    #     self.assertEqual([],errors)
    #
    # def test_method_handler(self):
    #     result_good = api.method_handler({'body': {'account': 'horns&hoofs', 'login': 'h&f', 'method': 'online_score', 'token': '55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af3', 'arguments': {'phone': '79175002040', 'email': 'stupnikov@otus.ru', 'first_name': '11', 'last_name': 'Ступников', 'birthday': '01.01.1990', 'gender': 1}}} ,{'request_id': '8b1aac327f4f4aa59d895f0a67818fee'}, None)
    #     self.assertEqual(({'score': 5.0}, 200), result_good)
    #     result_bad = api.method_handler({'body': {'account': 'horns&hoofs', 'login': 'h&f', 'method': 'online_score', 'token': '55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af3', 'arguments': {'phone': '79175002040', 'email': 'stupnikov@@@otus.ru', 'first_name': 123, 'last_name': 123, 'birthday': '01.01.1990', 'gender': 1}}} ,{'request_id': '8b1aac327f4f4aa59d895f0a67818fee'}, None)
    #     self.assertEqual((['Inccorect email.'], 422), result_bad)

if __name__ == '__main__':
    unittest.main()
