import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from http.server import BaseHTTPRequestHandler, HTTPServer

import scoring

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}

empty_values = ('', [], (), None, {})


class Field:
    """A descriptor that forbids negative values"""
    def __init__(self, required=False, nullable=False):
        self.required = required
        self.nullable = nullable

    def __set_name__(self, owner, name):
        self.name = name

    def validate(self, value):
        if self.required is True and value in empty_values:
            raise Exception('This value must be filled')
        if self.nullable is True and value in empty_values:
            raise Exception('This value must be not empty')

    def __set__(self, instance, value):
        instance_dict = instance.__class__.__dict__
        for key in instance_dict:
            if instance_dict[key] == self:
                cur_argumnet_name = key
        try:
            self.validate(value)
            self.validate_value(instance,value)
        except Exception as ex:
            instance.__dict__['errors'][cur_argumnet_name] = "wasn't pass" ## ass на имя


class CharField(Field):
    def validate_value(self, instance, value):
        super().validate(value)
        if isinstance(value, str) is False:
            raise Exception('CharField must be str type')
        instance.__dict__[self.name] = value


class ArgumentsField(Field):
    def validate_value(self, instance, value):
        super().validate(value)
        if isinstance(value, dict) is False:
            raise Exception('ArgumentsField must be dict type')
        instance.__dict__[self.name] = value


class EmailField(CharField):
    def validate_value(self, instance, value):
        if isinstance(value, str) is False:
            raise Exception('EmailField must be str type')
        if value.count('@') != 1:
            raise Exception('wrong email address')
        instance.__dict__[self.name] = value


class PhoneField(Field):
    def validate_value(self, instance, value):
        super().validate(value)
        phone = str(value)
        if phone.startswith('7') is False or len(phone) != 11:
            raise Exception('wrong type of phone')
        instance.__dict__[self.name] = value

class DateField(Field):
    def validate_value(self, instance, value):
        super().validate(value)
        assert isinstance(value, str)
        try:
            datetime.datetime.strptime(value, '%d.%m.%Y')  ##need_cast to str?
        except Exception as ex:
            raise Exception('wrong date format')
        instance.__dict__[self.name] = value


class BirthDayField(DateField):
    def validate_value(self, instance, value):
        super().validate(value)
        try:
            birthday_date = datetime.datetime.strptime(value, '%d.%m.%Y')  ##double of parent method???
            assert (datetime.datetime.now() - birthday_date).days < 70 * 365
        except Exception as ex:
            raise Exception('wrong birthday_date format')
        instance.__dict__[self.name] = value


class GenderField(Field):
    def validate_value(self, instance, value):
        super().validate(value)
        try:
            assert value in [UNKNOWN, MALE, FEMALE]
        except Exception as ex:
            raise Exception('gender can be only 0 or 1 or 2')
        instance.__dict__[self.name] = value


class ClientIDsField(Field):
    def validate_value(self, instance, value):
        super().validate(value)
        try:
            assert isinstance(value, list)
            for x in value:
                assert isinstance(x, int)
        except Exception as ex:
            raise Exception('Wrong type of client ids')
        instance.__dict__[self.name] = value


class Request():
    def __init__(self, **kwargs):
        self.errors = {}

        class_fields = []
        for cur_class_feild in self.__class__.__dict__:
            if not cur_class_feild.startswith('__'):
                class_fields.append(cur_class_feild)

        for cur_key in class_fields:
            try:
                setattr(self, cur_key, kwargs[cur_key]) ##setattr | getattr | get| set| setattribute | getattribute
            except Exception:
                self.errors[cur_key] = "wasn't pass"


class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)


def is_admin(self):
    return self.login == ADMIN_LOGIN


def check_auth(request):  ### Распаршенный Method_request
    if is_admin(request):
        digest = hashlib.sha512(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).hexdigest()
    else:
        digest = hashlib.sha512(request.account + request.login + SALT).hexdigest()
    if digest == request.token:
        return True
    return False


def parse_response_json(json_response):
    errors = {}
    result_dict = {}
    json_response_body = json_response['body']
    if isinstance(json_response_body, str):
        json_response_body = json.loads(json_response_body)
    method_request = MethodRequest(**json_response_body)
    errors.update(method_request.errors)
    result_dict['method_request'] = method_request

    if method_request.arguments and method_request.arguments not in empty_values:
        method_request_arg_keys = list(method_request.arguments.keys())
        online_score_keys = ['birthday', 'phone', 'first_name', 'last_name', 'gender', 'email']
        clients_interests_keys = ['date', 'client_ids']

        if method_request_arg_keys[0] in online_score_keys:
            online_score_request = OnlineScoreRequest(**method_request.arguments) ## birthday -- phone -- first_name -- last_name -- gender -- email
            errors.update(online_score_request.errors)
            result_dict['online_score_request'] = online_score_request

        if method_request_arg_keys[0] in clients_interests_keys:
            clients_interests_request = ClientsInterestsRequest(**method_request.arguments) ## date -- client_ids
            errors.update(clients_interests_request.errors)
            result_dict['clients_interests_request'] = clients_interests_request

    result_dict['errors'] = errors
    return result_dict


def online_score_handler(online_score_request, user_login, store):
    if online_score_request not in empty_values:
        if user_login == "admin":
            return {"score": 42}, OK
        result = scoring.get_score(store, online_score_request)
        return {"score": result}, OK

def clients_interests_handler(clients_interests_request, store):
    result_map_answer = {}
    for x in clients_interests_request.client_ids:
        result_map_answer[x] = scoring.get_interests(store, x)
    return result_map_answer, OK


def method_handler(request, ctx, store):  ## это и есть обработчик?
    response_dict = parse_response_json(request)
    response_dict_keys = response_dict.keys()
    # if check_auth(method_req) is False:  ## Не понимаю куда бьется и почему не проходит авторизация
    #     return ERRORS['FORBIDDEN'], FORBIDDEN

    for element in response_dict_keys:
        if element == 'errors' and response_dict['errors'] not in empty_values:
            return [_ + ' ' + response_dict['errors'][_] for _ in response_dict['errors'].keys()], INVALID_REQUEST
        elif element == 'online_score_request' and response_dict['online_score_request'] not in empty_values:
            return online_score_handler(response_dict['online_score_request'], response_dict['method_request']['login'], store)
        elif element == 'clients_interests_request' and response_dict['clients_interests_request'] not in empty_values:
            return clients_interests_handler(response_dict['clients_interests_request'], store)
        elif element == 'method_request' in empty_values:
            return ERRORS['INVALID_REQUEST'], INVALID_REQUEST


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        print(r)
        logging.info(context)
        self.wfile.write(bytes(str(r), "utf-8"))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8555)
    op.add_option("-l", "--log", action="store", default=None)

    (opts, args) = op.parse_args()

    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
