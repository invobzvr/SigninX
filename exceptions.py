from json.decoder import JSONDecodeError
from requests.exceptions import SSLError


class NotLogin(Exception):
    pass


class NotTimeYet(Exception):
    pass


class TryAgain(Exception):
    pass
