from sqlite3 import connect
from json import loads, dumps
from threading import Thread
from time import sleep
from datetime import date, datetime

from base import *
from util import *


class SigninX:
    def __init__(self, database='data.db', custom=None):
        self.custom = parseModule(custom) if custom else {}
        self.conn = connect(database, check_same_thread=False)
        self.conn.execute('CREATE TABLE IF NOT EXISTS sites(name TEXT PRIMARY KEY,data TEXT,skip INT)')
        self.conn.execute('CREATE TABLE IF NOT EXISTS results(time TEXT,name TEXT,result TEXT)')
        self.tasks = {name: loads(raw) for name, raw in self.conn.execute('SELECT name,data FROM sites WHERE skip ISNULL')}
        self.schedule = {name: result for name, result in self.conn.execute(f'SELECT name,result FROM results WHERE "time" LIKE "%{date.today()}%"')}

    def add(self, name, args):
        if not self.tasks.get(name):
            self.tasks[name] = args
            self.conn.execute('INSERT INTO sites (name,data) VALUES(?,?)', (name, dumps(args)))
            self.conn.commit()
            return True

    def update(self, name, args):
        if self.tasks.get(name):
            self.tasks[name] = args
            self.conn.execute('UPDATE sites SET data=? WHERE name=?', (dumps(args), name))
            self.conn.commit()
            return True

    def remove(self, name):
        if self.tasks.get(name):
            self.conn.execute('DELETE FROM sites WHERE name=?', (name,))
            self.conn.commit()
            del self.tasks[name]
            return True

    def setSkip(self, name, skip=True):
        if self.tasks.get(name):
            self.conn.execute('UPDATE sites SET skip=? WHERE name=?', (1 if skip else None, name))
            self.conn.commit()
            del self.tasks[name]
            return True

    def start(self):
        ts = []
        for name in self.tasks:
            if not self.schedule.get(name):
                t = Thread(target=self.run, args=(name,))
                t.start()
                ts.append(t)
        for t in ts:
            t.join()
        self.check()

    def check(self):
        if len(self.schedule) == len(self.tasks):
            self.close()
            return True
        else:
            sleep(30 * 60)
            self.start()

    def close(self):
        self.conn.close()

    def run(self, name):
        rzt = self.custom.get(f'SX_{name}', BaseSignin)(name, self.tasks[name], self).signin()
        if rzt:
            if isinstance(rzt, dict):
                rzt = dumps(rzt, ensure_ascii=0)
            self.conn.execute('INSERT INTO results VALUES(?,?,?)', (datetime.now(), name, rzt))
            self.conn.commit()
            self.schedule[name] = rzt
