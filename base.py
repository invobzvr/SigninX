from requests import request

from exceptions import *


class BaseSignin:
    def __init__(self, name, args, sx=None, maxRetry=10):
        self.name = name
        self.args = args
        self.sx = sx
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

    def setCookies(self, res):
        self.args['cookies'] = {cki.name: cki.value for cki in res.cookies}

    def login(self):
        res = self.req(self.args['login'])
        self.setCookies(res)
        self.save()

    def beforeSI(self):
        pass

    def signin(self):
        for i in range(self.maxRetry):
            try:
                self.beforeSI()
                rzt = self.req(self.args)
                if rzt:
                    self.verify(rzt)
                    return rzt
                else:
                    raise NotLogin
            except (NotLogin, JSONDecodeError):
                self.login()
            except NotTimeYet:
                break

    def verify(self, rzt):
        pass

    def save(self):
        self.sx and self.sx.update(self.name, self.args)
