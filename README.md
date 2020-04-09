# SigninX
An automatic sign in system.

## Guide
Clone to local directory, and create a new file `app.py` in it.
```py
from main import SigninX

sx = SigninX(database='data.db')
```

### Add a site
```py
sx.add('siteName', {
    'method': 'get',
    'url': 'https://example.com/signin',
    'result': 'res.json()',
    'data': {
        'data1': 'value1',
        'data2': 'value2',
        ...
    },
    'params': {
        'param1': 'value1',
        'param2': 'value2',
        ...
    },
    'login': {
        'method': 'post',
        'url': 'https://example.com/login',
        'data': {
            ...
        },
        'params': {
            ...
        }
    }
})
```

### Start to sign in
```py
sx.start()
print(sx.schedule)
```

### Use custom
Create a new file `custom.py` in the same directory.
```py
from base import *


class SX_siteName(BaseSignin):
    def __init__(self, name, args, sx=None, maxRetry=10):
        super().__init__(name, args, sx, maxRetry)

    def beforeSI(self):
        # Do something before signin
        self.args['data']['param3'] = 'value3'

    def login():
        # M1
        from requests import post
        res = post(...)
        # M2
        self.args['login']['data3'] = 'value3'
        res = self.req(self.args['login'])
        # After login successfully, call these to save cookies
        self.setCookies(res)
        self.save()

        # Or
        self.args['login']['data3'] = 'value3'
        super().login()

    def verify(self, rzt):
        from time import localtime
        if localtime().tm_hour < 8:
            raise NotTimeYet
        if isinstance(rzt, str):
            raise NotLogin
```
and in `app.py`, add parameter *custom*:
```py
sx = SigninX(database='data.db', custom='custom')
```