import unittest
import api
from api import ClientIDsField, DateField, CharField, PhoneField, GenderField, BirthDayField, EmailField, ArgumentsField

class IntegrationTest(unittest.TestCase):
    def test_parse_response_json(self):
        method_request, online_score_request, clients_interests_request, errors = api.parse_response_json(
            {'body': {'account': 'horns&hoofs', 'login': 'h&f', 'method': 'online_score',
             'token': '55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af3',
             'arguments': {'phone': '79175002040', 'email': 'stupnikov@otus.ru', 'first_name': '11',
             'last_name': 'Ступников', 'birthday': '01.01.1990', 'gender': 1}}})
        self.assertTrue(method_request is not None)
        self.assertTrue(online_score_request is not None)
        self.assertTrue(clients_interests_request is None)
        self.assertEqual({},errors)

    def test_method_handler_good(self):
        result_good = api.method_handler({'body': {'account': 'horns&hoofs', 'login': 'h&f', 'method': 'online_score', 'token': '55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af3', 'arguments': {'phone': '79175002040', 'email': 'stupnikov@otus.ru', 'first_name': '11', 'last_name': 'Ступников', 'birthday': '01.01.1990', 'gender': 1}}} ,{'request_id': '8b1aac327f4f4aa59d895f0a67818fee'}, None)
        self.assertEqual(({'score': 5.0}, 200), result_good)

    def test_method_handler_bad(self):
        result_bad = api.method_handler({'body': {'account': 'horns&hoofs', 'login': 'h&f', 'method': 'online_score', 'token': '55cc9ce545bcd144300fe9efc28e65d415b923ebb6be1e19d2750a2c03e80dd209a27954dca045e5bb12418e7d89b6d718a9e35af3', 'arguments': {'phone': '79175002040', 'email': 'stupnikov@@@otus.ru', 'first_name': 123, 'last_name': 123, 'birthday': '01.01.1990', 'gender': 1}}} ,{'request_id': '8b1aac327f4f4aa59d895f0a67818fee'}, None)
        self.assertEqual((["email wasn't pass", "first_name wasn't pass", "last_name wasn't pass"], 422), result_bad)