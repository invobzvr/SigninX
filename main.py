from util import BaseSignin
import costum
from sqlite3 import connect
from json import loads, dumps
from threading import Thread
from time import time, sleep


class SigninX:
    def __init__(self):
        self.schedule = {}
        self.conn = connect('data.db')
        self.cur = self.conn.cursor()
        self.cur.execute('CREATE TABLE IF NOT EXISTS sites(name TEXT PRIMARY KEY,data TEXT)')
        self.cur.execute('CREATE TABLE IF NOT EXISTS results(ts INTEGER PRIMARY KEY,name TEXT,result TEXT)')
        self.cur.execute('SELECT * FROM sites')
        self.tasks = {name: loads(raw) for name, raw in self.cur}

    def add(self, name, args):
        self.tasks[name] = args
        self.cur.execute('INSERT INTO sites VALUES(%s,%s)' % (name, dumps(args)))
        self.conn.commit()

    def start(self):
        ts = []
        for name in self.tasks:
            if not self.schedule.get(name):
                t = Thread(target=self.task, args=(name,))
                t.start()
                ts.append(t)
        for t in ts:
            t.join()
        self.check()

    def check(self):
        if all(self.schedule.values()):
            self.close()
        else:
            sleep(30 * 60)
            self.start()

    def close(self):
        self.cur.close()
        self.conn.close()

    def task(self, name):
        rzt = (eval('costum.SX_%s' % name) if 'SX_%s' % name in dir(costum) else BaseSignin)(name, self.tasks[name], self.conn).signin()
        self.cur.execute('INSERT INTO results VALUES(%s,%s,%s)' % (int(time()), name, rzt))
        self.conn.commit()
        self.schedule[name] = rzt
