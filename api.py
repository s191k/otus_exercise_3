import abc
import collections
import json
import datetime
import logging
import hashlib
import re
import uuid
from optparse import OptionParser
# from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
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


class MetaClassField():
    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        print('zdarova')
        if not isinstance(value, str):
            print('ne')
            return
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


# class Field(abc.ABC):
class Field():
    """A descriptor that forbids negative values"""
    def __init__(self, required=False, nullable=False):
        self.required = required
        self.nullable = nullable

    def validate(self, value):
        if self.required is True and value in empty_values:
            raise Exception('This value must be filled')
        if self.nullable is True and value in empty_values:
            raise Exception('This value must be not empty')

    # @abc.abstractmethod
    def value_validate(self, value):
        self.validate(value)
        # pass


class CharField(Field):
    def value_validate(self, value):
        print('charfield', value)
        super().validate(value)
        if isinstance(value, str) is False:
            raise Exception('CharField must be str type')
        return value


class ArgumentsField(Field):
    def value_validate(self, value):
        super().validate(value)
        if isinstance(value, dict) is False:
            raise Exception('ArgumentsField must be dict type')
        return value


class EmailField(CharField):

    def __set__(self, instance, value):
        print('hereEmailEfield')
        if isinstance(value, str) is False:
            raise Exception('EmailField must be str type')
        if value.count('@') != 1:
            raise Exception('wrong email address')
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name

    # def value_validate(self, value):
    #     super().validate(value)
    #     if isinstance(value, str) is False:
    #         raise Exception('EmailField must be str type')
    #     if value.count('@') != 1:
    #         raise Exception('wrong email address')
    #     return value


class PhoneField(Field):
    def value_validate(self, value):
        super().validate(value)
        phone = str(value)
        if phone.startswith('7') is False or len(phone) != 11:
            raise Exception('wrong type of phone')
        return value


class DateField(Field):
    def value_validate(self, value):
        super().validate(value)
        assert isinstance(value, str)
        try:
            datetime.datetime.strptime(value, '%d.%m.%Y')  ##need_cast to str?
        except Exception as ex:
            raise Exception('wrong date format')
        return value


class BirthDayField(DateField):
    def value_validate(self, value):
        super().validate(value)
        try:
            birthday_date = datetime.datetime.strptime(value, '%d.%m.%Y')  ##double of parent method???
            assert (datetime.datetime.now() - birthday_date).days < 70 * 365
        except Exception as ex:
            raise Exception('wrong birthday_date format')
        return value


class GenderField(Field):
    def value_validate(self, value):
        super().validate(value)
        try:
            assert value in [UNKNOWN, MALE, FEMALE]
        except Exception as ex:
            raise Exception('gender can be only 0 or 1 or 2')
        return value


class ClientIDsField(Field):
    def value_validate(self, value):
        super().validate(value)
        try:
            assert isinstance(value, list)
            for x in value:
                assert isinstance(x, int)
        except Exception as ex:
            raise Exception('Wrong type of client ids')
        return value

class DictAttrMetaclass(type):
    """ Метаклса для добавления всех полей класса, в словарь only_attr"""
    def __new__(cls, clsname, bases, dct):
        only_attr = {}
        for name, val in dct.items():
            if not name.startswith('__'):
                # print(name, val)
                only_attr[name] = val

        dct['only_attr'] = only_attr
        return type.__new__(cls, clsname, bases, dct)



class Request(metaclass=DictAttrMetaclass):

    def __init__(self, **kwargs):
        for _ in kwargs:
            self.__dict__[_] = kwargs[_]

    @abc.abstractmethod ##? Можно ли использовать без прямого наследования от abc.ABC
    def values_validate(self):
        pass


def validate_class_fields(class_object):
    errors = {} ## Или в Request хранить ?
    object_dict = class_object.__dict__
    object_class_dict = class_object.__class__.__dict__
    for cur_field in object_dict:

        if cur_field == 'email':
            print(cur_field)
            # print(class_object.__class__().__dict__)
            print(class_object.__class__().email)
            print(object_dict[cur_field])

            print(class_object.__class__().__dict__)
            class_object.__class__().email = object_dict[cur_field]
            print(class_object.__class__().__dict__)

        if cur_field == 'errors': pass
        if cur_field not in empty_values:
            try:
                pass
                # object_class_dict[cur_field].value_validate(object_dict[cur_field])
            except Exception as ex:
                errors[cur_field] = "Wasn't validate"
    return errors

class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    def values_validate(self):
        errors = validate_class_fields(self)
        return errors

class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def values_validate(self):
        errors = validate_class_fields(self)
        if (self.first_name and self.last_name) is False or \
                    (self.email and self.phone) is False or \
                (self.birthday and self.gender) is False:
            errors['main_error_OnlineScoreRequest'] = 'not_validate_pars'
        return errors


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    def values_validate(self):
        errors = validate_class_fields(self)
        return errors

# @property
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
    method_request = MethodRequest()
    online_score_request = None
    clients_interests_request = None
    errors = []

    # if isinstance(json_response, str): ###?
    #     json_response = json.loads(method_request)

    cur_request = Request(**json_response['body'])

    if cur_request.arguments not in empty_values:
        method_request.arguments = cur_request.arguments
        method_request_arg_keys = list(method_request.arguments.keys())
        errors.append(method_request.values_validate()) ## Validate
        online_score_keys = ['birthday', 'phone', 'first_name', 'last_name', 'gender', 'email']
        clients_interests_keys = ['date', 'client_ids']

        # fill online_score_request
        if method_request_arg_keys[0] in online_score_keys:
            online_score_request = OnlineScoreRequest(**cur_request.arguments) ## birthday -- phone -- first_name -- last_name -- gender -- email
            errors.append(online_score_request.values_validate())

        # fill clients_interests_request
        if method_request_arg_keys[0] in clients_interests_keys:
            clients_interests_request = ClientsInterestsRequest(**cur_request.arguments) ## date -- client_ids
            errors.append(clients_interests_request.values_validate()) ## Validate

    return method_request, online_score_request, clients_interests_request, errors


def online_score_handler(online_score_request, user_login, store):

    ##TODO
    ## Пеереписать чтобы обрабатывало корректно поля.
    if online_score_request not in empty_values:
        if user_login == "admin":
            return {"score": 42}, OK
        result = scoring.get_score(store, online_score_request)
        return {"score": result}, OK

def clients_interests_handler(clients_interests_request, store):

    ##TODO
    ## Пеереписать чтобы обрабатывало корректно поля.
    result_map_answer = {}
    for x in clients_interests_request.client_ids:
        result_map_answer[x] = scoring.get_interests(store, x)
    return result_map_answer, OK


def method_handler(request, ctx, store):  ## это и есть обработчик?

    method_req, online_score_req, clients_interests_request, errors = parse_response_json(request)
    # if check_auth(method_req) is False:  ## Не понимаю куда бьется и почему не проходит авторизация
    #     return ERRORS['FORBIDDEN'], FORBIDDEN

    res_errors_dict = errors[0]
    for _ in errors: res_errors_dict.update(_)

    if res_errors_dict not in empty_values:
        return [_ + errors[_] for _ in errors.keys()], INVALID_REQUEST

    if online_score_req not in empty_values:
        return online_score_handler(online_score_req, method_req.login, store)

    if clients_interests_request not in empty_values:
        return clients_interests_handler(clients_interests_request, store)

    if method_req in empty_values:
        return ERRORS['INVALID_REQUEST'], INVALID_REQUEST


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None
    print(str(method_handler))

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
