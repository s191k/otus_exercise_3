import json
import os
import unittest
import api

class IntegrationTest(unittest.TestCase):

    def _fixture_load_helper(self,fixture_file_name):
        with open(os.path.join(os.path.abspath(os.path.curdir) + "\\fixtures\\" + fixture_file_name), "r") as read_file:
            json_result_dict = json.load(read_file)
        return json_result_dict

    def test_parse_response_json(self):
        method_request, online_score_request,\
        clients_interests_request, errors = api.parse_response_json(self._fixture_load_helper('api_request_good.json'))
        self.assertTrue(method_request is not None)
        self.assertTrue(online_score_request is not None)
        self.assertTrue(clients_interests_request is None)
        self.assertEqual({},errors)

    def test_method_handler_good(self):
        json_dict = self._fixture_load_helper('api_request_good.json')
        result_good = api.method_handler(json_dict, {'request_id': '8b1aac327f4f4aa59d895f0a67818fee'}, None)
        self.assertEqual(({'score': 5.0}, 200), result_good)

    def test_method_handler_bad(self):
        json_dict = self._fixture_load_helper('api_request_bad.json')
        result_bad = api.method_handler(json_dict ,{'request_id': '8b1aac327f4f4aa59d895f0a67818fee'}, None)
        self.assertEqual((["email wasn't pass", "first_name wasn't pass", "last_name wasn't pass"], 422), result_bad)

