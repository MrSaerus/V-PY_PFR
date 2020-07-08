import tkinter as tk
from tkinter import ttk
import sqlite3
import cv2


class DBInOu:
    def __init__(self):
        self.connect = sqlite3.connect('base.db')
        self.c = self.connect.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS area (id integer primary key, code text, area_title text)''')
        self.c.execute('''CREATE TABLE IF NOT EXISTS cams (
                                                        id integer primary key,
                                                        code text, 
                                                        ip text, 
                                                        port integer, 
                                                        login text, 
                                                        password text,
                                                        num_cams integer,
                                                        type_conn text,
                                                        id_area integer, 
                                                        FOREIGN  KEY (id_area) REFERENCES area(id))
                ''')
        self.connect.commit()

    def get_cams(self, id_area):
        if id_area == '*':
            self.c.execute("SELECT * FROM cams")
        else:
            self.c.execute("SELECT * FROM cams WHERE id_area = (?)", [id_area])
        rows = self.c.fetchall()
        return rows

    def get_area(self):
        dict_areas = {}
        self.c.execute('''SELECT * FROM area''')
        rows = self.c.fetchall()
        for row in rows:
            dict_areas[row[0]] = '%s' % row[2]
        return dict_areas

    def add_area(self, code, area_title):
        self.c.execute('''INSERT INTO area(code, area_title) VALUES (?, ?)''', [code, area_title])
        self.connect.commit()

    def add_cams(self, code, ip, port, login, password, num_cams, type_conn, id_area):
        self.c.execute('''INSERT INTO cams(code, ip, port, login, password, num_cams, type_conn, id_area) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                            [code, ip, port, login, password, num_cams, type_conn, id_area])
        self.connect.commit()


class Scrollable(tk.Frame):
    def __init__(self, frame, width=16):
        scrollbar = tk.Scrollbar(frame, width=width)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # , expand=False)

        self.canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar.config(command=self.canvas.yview)

        self.canvas.bind('<Configure>', self.__fill_canvas)

        # base class initialization
        tk.Frame.__init__(self, frame)

        # assign this obj (the inner frame) to the windows item of the canvas
        self.windows_item = self.canvas.create_window(0, 0, window=self, anchor=tk.NW)

    def __fill_canvas(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.windows_item, width=canvas_width)

    def update(self):
        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))


class MainFrame(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.db = db
        self.top_frame()
        self.main_frame()

    def top_frame(self):
        toolbar = tk.Frame(bd=2)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        btn_open_dialog = tk.Button(toolbar, text="Добавить камеры", command=self.open_modal, bd=0, compound=tk.TOP)
        btn_open_dialog.pack(side=tk.LEFT)

    def open_modal(self):
        TopFrame()

    def rtsp_url(self, ip, port, login, password, type_conn, num_cams):
        if type_conn == 'NetSurveillance':
            url = f'rtsp://{ip}:{port}/user={login}&password={password}&channel={num_cams}&stream=1.sdp?real_stream--rtp-caching=100'
        elif type_conn == 'WebService':
            url = f'rtsp://{login}:{password}@{ip}:{port}/cam/realmonitor?channel={num_cams}&subtype=1'
        else:
            url = 'none'
        print(url)
        return url

    def rtsp_cam(self, title_cams, url_cams):
        cam_stream_0 = cv2.VideoCapture(url_cams)
        while True:
            cam_0, frame_0 = cam_stream_0.read()
            cv2.imshow(title_cams, frame_0)
            if cv2.waitKey(1) == ord('q'):
                break
        cam_stream_0.release()
        cv2.destroyAllWindows()

    def return_cams(self, event):
        app = tk.Frame(root, name='app')
        app.pack(expand=1, fill=tk.BOTH)
        scrollable_body = Scrollable(app, width=16)
        tabs = tk.Frame(scrollable_body)
        area_name = event.widget.get()
        list_area = self.db.get_area()
        id_area = list(list_area.keys())[list(list_area.values()).index(area_name)]
        cam = 1
        step = 0
        col = 0
        row = 0
        row_area = self.db.get_cams(id_area)
        for rows in row_area:
            id = rows[0]
            code = rows[1]
            ip = rows[2]
            port = rows[3]
            login = rows[4]
            password = rows[5]
            num_cams = rows[6]
            type_conn = rows[7]
            if self.rtsp_url(ip, port, login, password, type_conn, num_cams) != 'none':
                while cam < num_cams + 1:
                    frame = ttk.Frame(tabs, width=200, height=200, style='TNotebook', name="frame_%s_%s" % (cam, step))
                    frame.grid(column=col, row=2 + row, padx=3, pady=3)
                    url = self.rtsp_url(ip, port, login, password, type_conn, cam)
                    button = tk.Button(tabs,
                                       command=lambda area_name=area_name, url=url: self.rtsp_cam(area_name, url),
                                       text="Камера %s_%s" % (cam, step),
                                       bg='#aaaaff', name="button_%s_%s" % (cam, step))
                    button.grid(column=col, row=3 + row, padx=3, pady=3)
                    if col == 4:
                        row += 3
                        col = 0
                    else:
                        col += 1
                    cam += 1
                step += 1
                cam = 1
                tk.Label(tabs, text="Cams supported", name="ror").grid(column=0, row=0, padx=3, pady=3)
            else:
                tk.Label(tabs, text="Cams not supported", name="ror").grid(column=0, row=0, padx=3, pady=3)
        tabs.pack(expand=1, fill=tk.Y)
        scrollable_body.update()

    def main_frame(self):
        app = tk.Frame(root, width=50)
        list_area = self.db.get_area()
        tk.Label(app, text="Выберите район").grid(column=0, row=0)
        comboExample = ttk.Combobox(app, values=list(list_area.values()), state="readonly", name="box")
        comboExample.grid(column=0, row=1, padx=3, pady=3)
        comboExample.current(0)
        comboExample.bind("<<ComboboxSelected>>", self.return_cams)
        app.pack(fill=tk.BOTH)


class TopFrame(tk.Toplevel):
    def __init__(self):
        super().__init__(root)
        self.db = db
        self.add_cams()

    def add_cams(self):
        app = tk.Frame(self, name='app')
        app.pack(expand=1, fill=tk.BOTH)
        scrollable_body = Scrollable(app, width=16)
        cam = tk.Frame(scrollable_body)

        list_cams = self.db.get_cams('*')
        r = 1
        c = 0
        tk.Label(cam, text='id').grid(column=0, row=0)
        tk.Label(cam, text='code').grid(column=1, row=0)
        tk.Label(cam, text='ip').grid(column=2, row=0)
        tk.Label(cam, text='port').grid(column=3, row=0)
        tk.Label(cam, text='login').grid(column=4, row=0)
        tk.Label(cam, text='pass').grid(column=5, row=0)
        tk.Label(cam, text='cams').grid(column=6, row=0)
        tk.Label(cam, text='method').grid(column=7, row=0)
        tk.Label(cam, text='id_area').grid(column=8, row=0)
        for rows in list_cams:
            for row in rows:
                tk.Label(cam, text=row).grid(column=c, row=r)
                c += 1
            c = 0
            r += 1
        cam.pack(fill=tk.BOTH)
        scrollable_body.update()
        self.title("AddCams ПФР")
        self.geometry("460x800+300+50")
        self.grab_set()
        self.focus_set()


if __name__ == "__main__":
    root = tk.Tk()
    db = DBInOu()
    app = MainFrame(root)
    root.title("ViewCam ПФР")
    root.geometry("1200x720+1+1")
    root.mainloop()
