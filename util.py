from requests import request
from exceptions import *
from json import dumps
from json.decoder import JSONDecodeError


class BaseSignin:
    def __init__(self, name, args, conn=None, maxRetry=10):
        self.name = name
        self.args = args
        self.conn = conn
        self.maxRetry = maxRetry

    def req(self, args):
        res = request(
            args['method'],
            args['url'],
            params=args.get('params'),
            headers=args.get('headers'),
            cookies=args.get('cookies'),
            data=args.get('data'),
            allow_redirects=args.get('allow_redirects', True)
        )
        return eval(args.get('result', 'None')) or res

    def login(self):
        res = self.req(self.args['login'])
        self.args['cookies'] = {cki.name: cki.value for cki in res.cookies}
        self.save()

    def signin(self):
        for i in range(self.maxRetry):
            try:
                rzt = self.req(self.args)
                if rzt:
                    self.verify(rzt)
                    return rzt
                else:
                    raise NotLogin
            except (NotLogin, JSONDecodeError):
                self.login()

    def verify(self, rzt):
        pass

    def save(self):
        if self.conn:
            self.conn.execute('UPDATE sites SET data=? WHERE name=?', (dumps(self.args), self.name))
            self.conn.commit()
