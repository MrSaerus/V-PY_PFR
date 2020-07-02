import tkinter as tk
from tkinter import ttk
from tkinter import *

list_area = [
    'Абзелиловский район‎',
    'Альшеевский район‎',
    'Архангельский район‎',
    'Аскинский район‎',
    'Аургазинский район‎',
    'Баймакский район‎',
    'Бакалинский район‎',
    'Балтачевский район',
    'Белебеевский район‎',
    'Белокатайский район‎',
    'Белорецкий район‎',
    'Бижбулякский район‎',
    'Бирский район‎',
    'Благоварский район',
    'Благовещенский район',
    'Буздякский район‎',
    'Гафурийский район',
    'Давлекановский район',
    'Дуванский район',
    'Дюртюлинский район',
    'Ермекеевский район‎',
    'Зианчуринский район',
    'Зилаирский район‎',
    'Иглинский район‎',
    'Илишевский район‎',
    'Ишимбайский район',
    'Калтасинский район‎',
    'Караидельский район',
    'Кармаскалинский район',
    'Кигинский район',
    'Краснокамский район',
    'Кугарчинский район‎',
    'Кушнаренковский район‎',
    'Куюргазинский район',
    'Мелеузовский район',
    'Мечетлинский район',
    'Мишкинский район',
    'Нуримановский район',
    'Салаватский район‎',
    'Стерлибашевский район',
    'Стерлитамакский район‎',
    'Татышлинский район‎',
    'Туймазинский район‎',
    'Уфимский район‎',
    'Учалинский район',
    'Фёдоровский район',
    'Хайбуллинский район',
    'Чекмагушевский район‎',
    'Чишминский район',
    'Шаранский район',
    'Янаульский район‎'
]

class Scrollable(tk.Frame):
    """
      Make a frame scrollable with scrollbar on the right.
      After adding or removing widgets to the scrollable frame,
      call the update() method to refresh the scrollable area.
   """

    def __init__(self, frame, width=64):
        scrollbar = tk.Scrollbar(frame, width=width)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        self.canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.canvas.yview)

        self.canvas.bind('<Configure>', self.__fill_canvas)

        # base class initialization
        tk.Frame.__init__(self, frame)

        # assign this obj (the inner frame) to the windows item of the canvas
        self.windows_item = self.canvas.create_window(0, 0, window=self, anchor=tk.NW)

    def __fill_canvas(self, event):
        "Enlarge the windows item to the canvas width"

        canvas_width = event.width
        self.canvas.itemconfig(self.windows_item, width=canvas_width)

    def update(self):
        "Update the canvas and the scrollregion"

        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))


root = tk.Tk()

root.geometry('1000x700+1+1')
#root.resizable('False', 'False')
#header = Frame(root)
body = Frame(root)
#footer = Frame(root)
#header.pack()
body.pack(expand=1, fill='both')
#footer.pack()
#header.configure(width=200, height=100)

#l1 = Label(header, text="The header")
#l1.grid(column=0, row=0)
#ttk.Label(footer, text="The Footer").pack()

scrollable_body = Scrollable(body, width=16)

#for i in range(30):
#    ttk.Button(scrollable_body, text="I'm a button in the scrollable frame").grid(column=0, row=i)
#    ttk.Button(scrollable_body, text="I'm").grid(column=1, row=i)

style = ttk.Style(scrollable_body)
style.configure('lefttab.TNotebook', tabposition='wn')

tabs = ttk.Notebook(scrollable_body, style='lefttab.TNotebook')

i = 0
for area_name in list_area:
   globals()['tab_%s' % i] = tk.Frame(tabs)
   tabs.add(globals()['tab_%s' % i], text=area_name)
   c = 0
   column = 0
   while c < 4:
      tk.Label(globals()['tab_%s' % i], text="Камера %s" % c).grid(column=column, row=2, padx=3, pady=3)
      tk.Button(globals()['tab_%s' % i], width=20, height=10, bg='#aaaaff').grid(column=column, row=1, padx=3, pady=3)
      column += 1
      c += 1
   i += 1

tabs.pack(expand=1, fill='both')
scrollable_body.update()

root.mainloop()