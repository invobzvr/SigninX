import tkinter as tk
import tkinter.ttk as ttk
from datetime import timedelta

from main import *


class SX_TkGUI(tk.Tk):
    def __init__(self, database='data.db', custom=None):
        super(SX_TkGUI, self).__init__()
        self.title('SigninX TkGUI')
        self.sx = SigninX(database, custom)
        self.day = date.today()

        m_frm = ttk.Frame(self)
        m_frm.pack(expand=True, fill='both', padx=5, pady=5)

        nb = ttk.Notebook(m_frm)
        nb.pack(expand=True, fill='both', side='left', padx=5, pady=5)

        tplt = {
            'sites': {'Name': [120, 'center'], 'data': [360, 'w'], 'skip': [60, 'center']},
            'results': {'Date': [120, 'center'], 'Name': [120, 'center'], 'Result': [300, 'w']}
        }
        for name in tplt:
            X = name[0]
            cols = tplt[name]
            exec(f'''
{X}_frm = ttk.Frame(nb)
nb.add({X}_frm, text=name.title(), padding=5)
{X}_tv = ttk.Treeview({X}_frm, columns=list(cols), show='headings', height=20)
{X}_tv.pack(expand=True, fill='both', side='left')
{X}_tv.bind('<<TreeviewSelect>>', self.updateView)
for col in cols:
    {X}_tv.heading(col, text=col, command=lambda self=self, tv={X}_tv, col=col: self.sortColumn(tv, col, False))
    {X}_tv.column(col, width=cols[col][0], minwidth=cols[col][0], anchor=cols[col][1])
self.setScrollbar({X}_frm, {X}_tv)
self.{X}_tv = {X}_tv
''')

        v_frm = ttk.LabelFrame(m_frm, text='View')
        v_frm.pack(expand=True, fill='both', side='right', padx=5, pady=5)
        v_txt = tk.Text(v_frm, width=50)
        v_txt.pack(expand=True, fill='both', side='left')
        self.setScrollbar(v_frm, v_txt)

        o_frm = ttk.Frame(self)
        o_frm.pack()

        sx_lf = ttk.LabelFrame(o_frm, text='SigninXOpt')
        sx_lf.pack(side='left', padx=5, pady=5)
        ttk.Button(sx_lf, text='Start', command=self.start).pack(side='left', padx=5, pady=5)
        ttk.Button(sx_lf, text='Refresh', command=self.refresh).pack(side='left', padx=5, pady=5)
        ttk.Button(sx_lf, text='Skip', command=self.setSkip).pack(side='left', padx=5, pady=5)
        ttk.Button(sx_lf, text='Before', command=self.dayBefore).pack(side='left', padx=5, pady=5)
        ttk.Button(sx_lf, text='After', command=self.dayAfter).pack(side='left', padx=5, pady=5)

        self.v_txt = v_txt
        self.geometry('+320+180')
        self.load()

    def updateView(self, evt):
        tv = evt.widget
        val = tv.item(tv.selection()[-1])['values'][1 if tv == self.s_tv else 2]
        if val.startswith('{'):
            val = dumps(loads(val), indent=4, ensure_ascii=False)
        self.v_txt.delete(1.0, 'end')
        self.v_txt.insert(1.0, val)

    def sortColumn(self, tv, col, asc):
        items = [(tv.set(var, col), var) for var in tv.get_children()]
        items.sort(reverse=asc)
        for idx, (val, var) in enumerate(items):
            tv.move(var, '', idx)
        tv.heading(col, command=lambda: self.sortColumn(tv, col, not asc))

    def setScrollbar(self, par, tar):
        sby = ttk.Scrollbar(par, orient='vertical', command=tar.yview)
        sby.pack(fill='y', side='right')
        tar.config(yscrollcommand=sby.set)

    def load(self):
        for i in self.sx.conn.execute('SELECT * FROM sites'):
            self.s_tv.insert('', 'end', values=i)
        for i in self.sx.conn.execute(f'SELECT * FROM results WHERE "time" LIKE "%{self.day}%"'):
            self.r_tv.insert('', 'end', values=i)

    def empty(self, s=True):
        s and self.s_tv.delete(*self.s_tv.get_children())
        self.r_tv.delete(*self.r_tv.get_children())

    def start(self):
        Thread(target=self.sx.start).start()

    def refresh(self):
        self.empty()
        self.load()

    def setSkip(self):
        var = self.s_tv.selection()[-1]
        values = self.s_tv.item(var)['values']
        skip = values[-1] != 1
        if self.sx.setSkip(values[0], skip):
            values[-1] = 1 if skip else None
            self.s_tv.item(var, values=values)

    def dayBefore(self):
        self.day -= timedelta(1)
        self.refresh()

    def dayAfter(self):
        self.day += timedelta(1)
        self.refresh()


if __name__ == '__main__':
    st = SX_TkGUI(custom='custom')
    st.mainloop()
