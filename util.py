from requests import get, post
from exceptions import *
from json import dumps
from json.decoder import JSONDecodeError


API = {
    'get': get,
    'post': post
}


class BaseSignin:
    def __init__(self, name, args, conn=None, maxRetry=10):
        self.name = name
        self.args = args
        self.conn = conn
        self.maxRetry = maxRetry

    def req(self, args):
        res = API[args['method']](
            args['url'],
            params=args.get('params'),
            headers=args.get('headers'),
            cookies=args.get('cookies'),
            data=args.get('data')
        )
        return eval(args.get('result', 'None')) or res

    def login(self):
        res = self.req(self.args['login'])
        self.args['cookies'] = dict(res.cookies)
        if self.args.get('headers'):
            del self.args['headers']
        self.save()

    def signin(self):
        for i in range(self.maxRetry):
            try:
                rzt = self.req(self.args)
                if rzt:
                    self.result = rzt
                    return rzt
                else:
                    raise NotLogin
            except (NotLogin, JSONDecodeError):
                self.login()

    def save(self):
        if self.conn:
            self.conn.cursor().execute("UPDATE sites SET data='%s' WHERE name='%s'" % (dumps(self.args), self.name))
            self.conn.commit()
