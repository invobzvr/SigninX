from util import BaseSignin
from sqlite3 import connect
from json import loads, dumps
from threading import Thread
from time import time, sleep, strptime, strftime, mktime


def dayRange():
    st = strptime(strftime('%Y-%m-%d'), '%Y-%m-%d')
    ts = int(mktime(st)) + 28800
    return ts, ts + 86399


class SigninX:
    def __init__(self, database='data.db', custom=None):
        if custom:
            self.custom = __import__(custom)
        self.conn = connect(database, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.cur.execute('CREATE TABLE IF NOT EXISTS sites(name TEXT PRIMARY KEY,data TEXT)')
        self.cur.execute('CREATE TABLE IF NOT EXISTS results(ts INTEGER,name TEXT,result TEXT)')
        self.cur.execute('SELECT * FROM sites')
        self.tasks = {name: loads(raw) for name, raw in self.cur}
        self.cur.execute('SELECT name,result FROM results WHERE ts>=%s AND ts<=%s' % dayRange())
        self.schedule = {name: result for name, result in self.cur}

    def add(self, name, args):
        self.tasks[name] = args
        self.cur.execute('INSERT INTO sites VALUES(?,?)', (name, dumps(args)))
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
        rzt = (eval('self.custom.SX_%s' % name) if 'SX_%s' % name in dir(self.custom) else BaseSignin)(name, self.tasks[name], self.conn).signin()
        self.cur.execute("INSERT INTO results VALUES(?,?,?)", (int(time()), name, rzt))
        self.conn.commit()
        self.schedule[name] = rzt
