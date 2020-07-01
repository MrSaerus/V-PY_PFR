import tkinter as tk
from tkinter import ttk

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


class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        #self.init_main()
        #self.tabs()
        self.left_tabs()

    def tabs(self):
        FunTab = ttk.Notebook(root)

        i = 0
        for area_name in list_area:
            globals()['tab_%s' % i] = ttk.Frame(FunTab)
            FunTab.add(globals()['tab_%s' % i], text=area_name)
            ttk.Label(globals()['tab_%s' % i], text=area_name).grid(column=0, row=0, padx=30, pady=30)
            i += 1
        FunTab.pack(expand=1, fill='both')

        #olds

        #tab_2 = ttk.Frame(FunTab)
        #FunTab.add(tab_2, text='Ленинский район')
        #FunTab.pack(expand=1, fill='both')
        #ttk.Label(tab_2, text="Lets dive into the world of computers").grid(column=0, row=0, padx=30, pady=30)

    def left_tabs(self):
        style = ttk.Style(root)
        style.configure('lefttab.TNotebook', tabposition='ws')

        notebook = ttk.Notebook(root, style='lefttab.TNotebook')
        i = 0
        for area_name in list_area:
            globals()['tab_%s' % i] = tk.Frame(notebook, width=200, height=200)
            notebook.add(globals()['tab_%s' % i], text=area_name)
            i += 1
        notebook.pack()

    def init_main(self):
        toolbar = tk.Frame(bg='#f5ad42', bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        btn_open_dialog = tk.Button(toolbar, text="Камера", command=self.open_dialog, bg='#4287f5', bd=0, compound=tk.TOP)
        btn_open_dialog.pack(side=tk.LEFT)

    def open_dialog(self):
        child()


class child(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        self.init_child()

    def init_child(self):
        self.title("V-PY ПФР")
        self.geometry("300x300")
        self.grab_set()
        self.focus_set()


if __name__ == "__main__":
    root = tk.Tk()
    app = Main(root)
    app.pack()
    root.title("V-PY ПФР")
    root.geometry("1280x720+300+200")
    # root.resizable(False, False)
    root.mainloop()
#print(globals())
