from requests import get, post
from exceptions import *


API = {
    'get': get,
    'post': post
}


class BaseSignin:
    def __init__(self, args, maxRetry=10):
        self.args = args
        self.maxRetry = maxRetry

    def req(self, args):
        res = API[args['method']](
            args['url'],
            params=args.get('params'),
            headers=args.get('headers'),
            data=args.get('data')
        )
        return eval(args.get('result', 'None')) or res

    def login(self):
        res = self.req(self.args['login'])
        self.args['headers'] = res.headers
        self.save()

    def sginin(self):
        for i in range(self.maxRetry):
            try:
                rzt = req(self.args)
                if rzt:
                    return rzt
                else:
                    raise NotLogin
            except NotLogin:
                self.login()

    def save(self):
        pass
