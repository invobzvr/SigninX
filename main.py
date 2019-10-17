from util import BaseSignin
import costum
from sqlite3 import connect
from json import loads


class SigninX:
    def __init__(self):
        self.schedule = {}
        self.conn = connect('data.db')
        self.cur = self.conn.cursor()
        self.cur.execute('CREATE TABLE IF NOT EXISTS sites(name TEXT,data TEXT)')
        self.cur.execute('SELECT * FROM sites')
        self.tasks = {name: loads(raw) for name, raw in self.cur}

    def start(self):
        for name in self.tasks:
            self.schedule[name] = (eval('costum.SX_%s' % name) if 'SX_%s' % name in dir(costum) else BaseSignin)(name, self.tasks[name], self.conn).signin()
        self.check()

    def check(self):
        if all(self.schedule.values()):
            self.close()

    def close(self):
        self.cur.close()
        self.conn.close()
