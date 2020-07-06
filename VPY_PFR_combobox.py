import tkinter as tk
from tkinter import ttk
import sqlite3

app = tk.Tk()
app.title("V-PY ПФР")
app.geometry("1200x720+1+1")

conn = sqlite3.connect('base.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS area (id integer primary key, area_title text)''')
conn.commit()


def add_to_base(area):
    c.execute('''INSERT INTO area(area_title) VALUES (?)''', [area])
    conn.commit()


def callbackFunc(event):
    def ret_cams(area):
        return area + ('@')
    cam = 0
    c = 0
    r = 0
    while cam < 6:
        ttk.Frame(app, width=200, height=200, style='TNotebook').grid(column=c, row=2 + r, padx=3, pady=3)
        tk.Button(app, text="Камера %s %s" % (cam, comboExample.get()), bg='#aaaaff').grid(column=c, row=3 + r, padx=3, pady=3)
        # tk.Label(app, text="Камера %s %s" % (cam, ret_cams(comboExample.get()))).grid(column=c, row=4 + r, padx=3, pady=3)
        if c == 2:
            r += 3
            c = 0
        else:
            c += 1
        cam += 1


def view_from_base():
    list_area = []
    c.execute('''SELECT area_title FROM area''')
    rows = c.fetchall()
    for row in rows:
        list_area.append(row[0])
    return list_area

list_area = view_from_base()
labelTop = tk.Label(app, text="Выберите район").grid(column=0, row=0)

comboExample = ttk.Combobox(app, values= list_area, state="readonly")
comboExample.grid(column=0, row=1)
comboExample.current(0)
comboExample.bind("<<ComboboxSelected>>", callbackFunc)
#print(comboExample.current(), comboExample.get())
app.mainloop()