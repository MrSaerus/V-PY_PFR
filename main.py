import sqlite3
import cv2
import tkinter as tk
from tkinter import ttk
from tkinter import *


list_area = [
    'Баймак и район',
    'Октябрьский',
    'Абзелиловский',
    'Альшеевский',
    'Архангельский',
    'Аскинский',
    'Аургазинский',
    'Бакалинский',
    'Балтачевский',
    'Белокатайский',
    'Бижбулякский',
    'Благоварский',
    'Благовещенск и р-н',
    'Буздякский',
    'Бураевский',
    'Бурзянский',
    'Гафурийский',
    'Зилаирский',
    'Дуванский',
    'Дюртюли и район',
    'Дюртюли и район',
    'Ермекеевский',
    'Зианчуринский',
    'Калтасинский',
    'Иглинский',
    'Илишевский',
    'Кармаскалинский',
    'Караидельский',
    'Краснокамский',
    'Кигинский',
    'Куюргазинский',
    'Кугарчинский',
    'Кушнаренковский',
    'Мишкинский',
    'Мечетлинский',
    'Миякинский',
    'Нуримановский',
    'Салаватский',
    'Стерлибашевский',
    'Стерлитамакский',
    'Татышлинский',
    'Уфимский',
    'Давлеканово и р-н',
    'Федоровский',
    'Хайбуллинский',
    'Чекмагушевский',
    'Чишминский',
    'Шаранский',
    'Янаул и район',
    'Белебей и район',
    'Белебей и район',
    'Белорецк и район',
    'Белорецк и район',
    'Бирск и район',
    'Ишимбай и район',
    'Кумертау',
    'Мелеуз и район',
    'Нефтекамск',
    'Октябрьский',
    'Салават',
    'Стерлитамак',
    'Стерлитамак',
    'Стерлитамак',
    'Туймазы и район',
    'Сибай',
    'Учалы и район',
    'Учалы и район',
    'Калининский',
    'Кировский',
    'Кировский',
    'Ленинский',
    'Орджоникидзевский',
    'Демский',
    'Агидель',
    'Советский',
    'Межгорье'
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

    def __init__(self, frame, width=16):
        scrollbar = tk.Scrollbar(frame, width=width)
        scrollbar.pack(side=tk.LEFT, fill=tk.Y, expand=False)

        self.canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set, width=900)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

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
        #self.init_main()
        self.combobox_list()
        #self.tabs()
        #self.left_frame()
        #self.left_frame_tabs()
        #self.middle_frame()
        #self.rtsp_stream()

    def combobox_list(self):
        app = Frame(root)
        labelTop = tk.Label(app, text="Выберите район")
        labelTop.grid(column=0, row=0)

        comboExample = ttk.Combobox(app, value = list_area, state="readonly")
        #print(dict(comboExample))
        comboExample.grid(column=0, row=1)
        comboExample.current(1)

        #print(comboExample.current(), comboExample.get())


        def callbackFunc(event):
            def ret_cams(area):
                return area + ('@')
            cam = 0
            c = 0
            r = 0
            while cam < 6:
                ttk.Frame(app, width=200, height=200, style='TNotebook').grid(column=c, row=2 + r, padx=3, pady=3)
                tk.Label(app, text="Камера %s %s" % (cam, ret_cams(comboExample.get()))).grid(column=c, row=3 + r, padx=3, pady=3)
                if c == 2:
                    r += 2
                    c = 0
                else:
                    c += 1
                cam += 1
            #print(comboExample.get())
        comboExample.bind("<<ComboboxSelected>>", callbackFunc)
        app.pack(expand=1, fill='both')


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
        tabs.pack(expand=1, fill=Y)

    def left_frame_tabs(self):
        body = Frame(root)
        body.pack(expand=1, fill='both')
        scrollable_body = Scrollable(body, width=16)

        style = ttk.Style(scrollable_body)
        style.configure('lefttab.TNotebook', tabposition='wn')

        tabs = ttk.Notebook(scrollable_body, style='lefttab.TNotebook')
        cams = ttk.Frame(body)
        i = 0
        for area_name in list_area:
             globals()['tab_%s' % i] = tk.Frame(tabs)
             tabs.add(globals()['tab_%s' % i], text=area_name)
             c = 0
             column = 0
             while c < 4:
                tk.Label(globals()['tab_%s' % i], text="Камера %s %s" % (c, area_name)).grid(column=column, row=2, padx=3, pady=3)
                tk.Button(globals()['tab_%s' % i], command=self.open_dialog, width=20, height=10, bg='#aaaaff').grid(column=column, row=1, padx=3, pady=3)
                column += 1
                c += 1
             i += 1

        tabs.pack(expand=1, fill='both')
        scrollable_body.update()

    def left_frame(self):
        body = Frame(root)
        body.pack(expand=1, fill='both')
        scrollable_body = Scrollable(body, width=16)
        area_list = ttk.Frame(scrollable_body)#, style='TNotebook')
        cams = ttk.Frame(body, style='TNotebook')

        i = 0
        for area_name in list_area:
            area_list.button = tk.Button(area_list, command=self.rtsp_cam, text=area_name, width=20, height=2, bg='#cccccc').grid(row=i, padx=20, pady=3)
            i += 1
        cam = 0
        c = 0
        r = 0
        while cam < 6:
            ttk.Frame(cams, width=200, height=200, style='TNotebook').grid(column=c, row=1+r, padx=3, pady=3)
            #stream_Image = cv2.VideoCapture('rtsp://upf834:5896ae@10.2.29.190:554/cam/realmonitor?channel=1&subtype=1')

            tk.Label(cams, text="Камера %s" % cam).grid(column=c, row=2+r, padx=3, pady=3)
            if c == 2:
                r += 2
                c = 0
            else:
                c += 1
            cam += 1

        area_list.pack(expand=1, fill=Y)
        cams.pack(expand=1, fill='both')
        scrollable_body.update()


    def middle_frame(self):
        body = Frame(root)
        middle = ttk.Notebook(body, style='lefttab.TNotebook')
        c = 0
        column = 0
        while c < 4:
            tk.Label(middle, text="Камера %s" % c).grid(column=column, row=2, padx=3, pady=3)
            tk.Button(middle, command=self.open_dialog, width=20, height=10, bg='#aaaaff').grid(column=column, row=1, padx=3, pady=3)
            column += 1
            c += 1
        middle.pack(expand=1, fill='both')

    def rtsp_cam(self):
        #cam_stream_0 = cv2.VideoCapture('rtsp://upf834:5896ae@10.2.29.190:554/cam/realmonitor?channel=1&subtype=1')
        cam_stream_0 = cv2.VideoCapture('rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov')
        while True:
            cam_0, frame_0 = cam_stream_0.read()
            cv2.imshow('Абзелиловский район‎', frame_0)
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
        self.rtsp_cam()
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
