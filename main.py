import tkinter as tk
from tkinter import ttk
from tkinter import *

import cv2

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
list_area2 = [
    'Абзелиловский район‎',
    'Альшеевский район‎',
    'Архангельский район‎',
    'Аскинский район‎'
]
class Scrollable(tk.Frame):
    """
      Make a frame scrollable with scrollbar on the right.
      After adding or removing widgets to the scrollable frame,
      call the update() method to refresh the scrollable area.
   """

    def __init__(self, frame, width=64):
        scrollbar = tk.Scrollbar(frame, width=width)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y)  # , expand=False)

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

class Main(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.init_main()
        #self.tabs()
        self.left_tabs()
        #self.rtsp_stream()

    def tabs(self):
        tabs = ttk.Notebook(root)

        i = 0
        for area_name in list_area:
            globals()['tab_%s' % i] = ttk.Frame(tabs)
            tabs.add(globals()['tab_%s' % i], text=area_name)
            c = 0
            column = 0
            while c < 4:
                tk.Label(globals()['tab_%s' % i], text="Камера %s" % c).grid(column=column, row=2, padx=3, pady=3)
                tabs.button = tk.Button(globals()['tab_%s' % i], command=self.open_dialog, width=20, height=10, bg='#aaaaff').grid(column=column, row=1, padx=3, pady=3)
                column += 1
                c += 1

            i += 1
        tabs.pack(expand=1, fill='both')


    def left_tabs(self):
        body = Frame(root)
        body.pack(expand=1, fill='both')
        scrollable_body = Scrollable(body, width=16)

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
                tabs.button = tk.Button(globals()['tab_%s' % i], command=self.open_dialog, width=20, height=10, bg='#aaaaff').grid(column=column, row=1, padx=3, pady=3)
                column += 1
                c += 1
            i += 1

        tabs.pack(expand=1, fill='both')
        scrollable_body.update()


    def rtsp_cam(self, rtsp_url, name):
        cam_stream_0 = cv2.VideoCapture(rtsp_url)
        while True:
            cam_0, frame_0 = cam_stream_0.read()
            cv2.imshow(name, frame_0)

            if cv2.waitKey(1) == ord('q'):
                break
        cam_stream_0.release()
        cv2.destroyAllWindows()

    def rtsp_stream(self):
        cam_stream_0 = cv2.VideoCapture('rtsp://upf834:5896ae@10.2.29.190:554/cam/realmonitor?channel=1&subtype=1')
        cam_stream_1 = cv2.VideoCapture('rtsp://upf834:5896ae@10.2.29.190:554/cam/realmonitor?channel=2&subtype=1')
        cam_stream_2 = cv2.VideoCapture('rtsp://upf834:5896ae@10.2.29.190:554/cam/realmonitor?channel=3&subtype=1')
        while True:
            cam_0, frame_0 = cam_stream_0.read()
            cam_1, frame_1 = cam_stream_1.read()
            cam_2, frame_2 = cam_stream_2.read()
            cv2.imshow("Cam 1", frame_0)
            cv2.imshow("Cam 2", frame_1)
            cv2.imshow("Cam 3", frame_2)

            if cv2.waitKey(1) == ord('q'):
                break
        cam_stream_0.release()
        cam_stream_1.release()
        cam_stream_2.release()
        cv2.destroyAllWindows()

    def init_main(self):
        toolbar = tk.Frame(bg='#f5ad42', bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        btn_open_dialog = tk.Button(toolbar, text="Камера", command=self.open_dialog, bg='#4287f5', bd=0, compound=tk.TOP)
        btn_open_dialog.pack(side=tk.LEFT)

    def open_dialog(self):
        Main.rtsp_cam(self, 'rtsp://upf834:5896ae@10.2.29.190:554/cam/realmonitor?channel=1&subtype=1', 'Абзелиловский район‎')
        #child()


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
    root.geometry("1200x720+1+1")
    # root.resizable(False, False)
    root.mainloop()
#print(globals())
