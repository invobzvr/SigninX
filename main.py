from util import BaseSignin
from sqlite3 import connect
from json import loads, dumps
from threading import Thread
from time import time, sleep, strptime, strftime, mktime


def dayRange():
    st = strptime(strftime('%Y-%m-%d'), '%Y-%m-%d')
    ts = int(mktime(st))
    return ts, ts + 86399


class SigninX:
    def __init__(self, database='data.db', custom=None):
        self.custom = custom and __import__(custom)
        self.conn = connect(database, check_same_thread=False)
        self.conn.execute('CREATE TABLE IF NOT EXISTS sites(name TEXT PRIMARY KEY,data TEXT)')
        self.conn.execute('CREATE TABLE IF NOT EXISTS results(ts INTEGER,name TEXT,result TEXT)')
        self.tasks = {name: loads(raw) for name, raw in self.conn.execute('SELECT * FROM sites')}
        self.schedule = {name: result for name, result in self.conn.execute('SELECT name,result FROM results WHERE ts>=? AND ts<=?', dayRange())}

    def add(self, name, args):
        if not self.tasks.get(name):
            self.tasks[name] = args
            self.conn.execute('INSERT INTO sites VALUES(?,?)', (name, dumps(args)))
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
            self.conn.execute('DELETE FROM sites WHERE name=?', name)
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
        if all(self.schedule.values()):
            self.close()
            return True
        else:
            sleep(30 * 60)
            self.start()

    def close(self):
        self.conn.close()

    def run(self, name):
        rzt = (eval('self.custom.SX_%s' % name) if 'SX_%s' % name in dir(self.custom) else BaseSignin)(name, self.tasks[name], self.conn).signin()
        if rzt:
            if isinstance(rzt, dict):
                rzt = dumps(rzt, ensure_ascii=0)
            self.conn.execute('INSERT INTO results VALUES(?,?,?)', (int(time()), name, rzt))
            self.conn.commit()
            self.schedule[name] = rzt
