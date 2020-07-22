import os, sys, subprocess, cv2, sqlite3, configparser, math
import tkinter as tk
import numpy as np
from tkinter import ttk, Menu
from PIL import ImageTk, Image, ImageDraw, ImageFont


class Configurations:
    def __init__(self):
        config_file = configparser.ConfigParser()
        patch_cfg = 'config.cfg'
        if os.path.exists(patch_cfg):
            config_file.read(patch_cfg)
            globals()['always_debug_mode_cfg'] = config_file['Base']['always_debug_mode']
            globals()['default_font_overlay_cfg'] = config_file['Advanced']['default_font_overlay']
        else:
            config_file['Base'] = {'always_debug_mode': 'False'}
            config_file['Advanced'] = {'default_font_overlay': 'RussoOne-Regular.ttf'}
            with open(patch_cfg, 'w') as configfile:
                config_file.write(configfile)

    def write_config(self, param_1, param_2):
        config_file = configparser.ConfigParser()
        patch_cfg = 'config.cfg'
        config_file.read(patch_cfg)
        config_file['Base'] = {'always_debug_mode': param_1}
        config_file['Advanced'] = {'default_font_overlay': param_2}
        with open(patch_cfg, 'w') as configfile:
            config_file.write(configfile)
        config_file.read(patch_cfg)
        globals()['always_debug_mode_cfg'] = config_file['Base']['always_debug_mode']
        globals()['default_font_overlay_cfg'] = config_file['Advanced']['default_font_overlay']
        TestConnect.config_frame(self)


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
            self.c.execute("SELECT * FROM cams ORDER BY id DESC")
        elif id_area == 'Self':
            self.c.execute("SELECT ip, port FROM cams ORDER BY id DESC")
        else:
            self.c.execute("SELECT * FROM cams WHERE id_area = (?)", [id_area])
        rows = self.c.fetchall()
        return rows

    def get_area(self, switch):
        if switch == 'dict':
            dict_areas = {}
            self.c.execute('''SELECT * FROM area''')
            rows = self.c.fetchall()
            for row in rows:
                dict_areas[row[0]] = '%s' % row[2]
            return dict_areas
        elif switch == 'all':
            self.c.execute('''SELECT * FROM area ORDER BY id DESC''')
            return self.c.fetchall()
        else:
            self.c.execute('''SELECT * FROM area where id like (?)''', [switch])
            return self.c.fetchall()

    def add_area(self, code, area_title):
        self.c.execute('''INSERT INTO area(code, area_title) VALUES (?, ?)''', [code, area_title])
        self.connect.commit()

    def add_cams(self, code, ip, port, login, password, num_cams, type_conn, id_area):
        self.c.execute('''INSERT INTO cams(code, ip, port, login, password, num_cams, type_conn, id_area) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                            [code, ip, port, login, password, num_cams, type_conn, id_area])
        self.connect.commit()

    def delete_area(self, id):
        self.c.execute('''DELETE FROM area WHERE id = ?''', [id])
        self.connect.commit()

    def delete_cams(self, id):
        self.c.execute('''DELETE FROM cams WHERE id = ?''', [id])
        self.connect.commit()


class StdoutRedirector(object):
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert('end', string)
        self.text_space.see('end')


class Scrollable(tk.Frame):
    def __init__(self, frame, width=16):
        scrollbar = tk.Scrollbar(frame, width=width)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # , expand=False)
        self.canvas = tk.Canvas(frame, yscrollcommand=scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.canvas.yview)
        self.canvas.bind('<Configure>', self.__fill_canvas)
        tk.Frame.__init__(self, frame)
        self.windows_item = self.canvas.create_window(0, 0, window=self, anchor=tk.NW)

    def __fill_canvas(self, event):
        canvas_width = event.width
        self.canvas.itemconfig(self.windows_item, width=canvas_width)

    def update(self):
        self.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox(self.windows_item))


class GetSnap:
    def get_images(self, rtsp_url, cam):
        ffmpeg_patch = 'ffmpeg/bin/ffmpeg.exe'
        if os.path.exists(ffmpeg_patch):
            if not os.path.exists('SnapShot'):
                os.makedirs('SnapShot')
            img = f'SnapShot/{cam}'
            ffmpeg = ['ffmpeg/bin/ffmpeg.exe', '-y', '-i', rtsp_url, '-frames', '2', '-f', 'image2', img]
            subprocess.Popen(ffmpeg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            app_ffprobe = tk.Frame(tk.Tk(), name='add_edit')
            app_ffprobe.pack(expand=1, fill=tk.BOTH)
            out_text = ttk.Label(app_ffprobe, text='Ошибка, ffmpeg не установлен')
            out_text.pack(side=tk.BOTTOM, fill=tk.BOTH)
            app_ffprobe.pack(expand=1, fill=tk.Y)
            return 'stop'


class TopMenu(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.menu()

    def menu(self):
        menubar = Menu(root)
        cfgmenu = Menu(menubar, tearoff=0)
        cfgmenu.add_command(label="Редактировать/добавить районы",
                            command=self.add_edit_area)
        cfgmenu.add_command(label="Редактировать/добавить регистраторы/камеры",
                            command=self.add_edit_cams)
        cfgmenu.add_command(label="Настрока программы", command=self.cfg)
        cfgmenu.add_separator()
        cfgmenu.add_command(label="Exit", command=root.quit)

        menubar.add_cascade(label="Настройки", menu=cfgmenu)

        testmenu = Menu(menubar, tearoff=0)
        #testmenu.add_command(label="Вывод всех регистраторов", command=lambda: print('0'))
        testmenu.add_command(label="Проверка доступности регистраторов", command=self.regs)
        testmenu.add_separator()
        testmenu.add_command(label="Проверка потока видеорегистарора", command=self.check)
        testmenu.add_command(label="Тестирование левого потока", command=self.check_another)

        menubar.add_cascade(label="Тестирование", menu=testmenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="О программе", command=self.about_frame)

        menubar.add_cascade(label="Помощь", menu=helpmenu)

        root.config(menu=menubar)

    def regs(self):
        TestConnect('regs')

    def about_frame(self):
        TestConnect('about')

    def add_edit_area(self):
        TestConnect('edit_area')

    def add_edit_cams(self):
        TestConnect('edit_cams')

    def check(self):
        TestConnect('check')

    def check_another(self):
        TestConnect('check_another')

    def cfg(self):
        TestConnect('config_frame')


class MainFrame(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.db = db
        self.snap = snap
        self.main_frame()
        
        if always_debug_mode_cfg == 'True':
            self.bottom_frame()
        else:
            try:
                if sys.argv[1] == '-debug_console':
                    self.bottom_frame()
            except IndexError:
                print('IndexError')

    def update_area_cams(self):
        taskkill = ['taskkill', '/IM', 'ffmpeg.exe', '/F']
        subprocess.Popen(taskkill, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print('Info: taskkill executed')

    def rtsp_url(self, ip, port, login, password, type_conn, num_cams):
        if type_conn == 'NetSurveillance':
            url = f'rtsp://{ip}:{port}/user={login}&password={password}&' \
                  f'channel={num_cams}&stream=1.sdp?real_stream--rtp-caching=100'
        elif type_conn == 'WebService':
            url = f'rtsp://{login}:{password}@{ip}:{port}/cam/realmonitor?channel={num_cams}&subtype=1'
        elif type_conn == 'Self':
            url = ip
        else:
            url = 'NotSupport'
        return url

    def put_text_pil(self, img: np.array, txt: str):
        '''
            Not my function
        '''

        im = Image.fromarray(img)

        font_size = 24
        font = ImageFont.truetype('RussoOne-Regular.ttf', size=font_size)

        draw = ImageDraw.Draw(im)
        # здесь узнаем размеры сгенерированного блока текста
        w, h = draw.textsize(txt, font=font)

        y_pos = 10
        im = Image.fromarray(img)
        draw = ImageDraw.Draw(im)

        # теперь можно центрировать текст
        draw.text((int((img.shape[1] - w) / 2), y_pos), txt, fill='rgb(0, 0, 0)', font=font)

        img = np.asarray(im)

        return img

    def rtsp_cam(self, title_cams, url_cams):
        try:
            cam_stream_0 = cv2.VideoCapture(url_cams)
            while True:
                cam_0, frame_0 = cam_stream_0.read()

                cv2.imshow('ViewCam PFR', self.put_text_pil(frame_0, title_cams))
                if cv2.waitKey(1) == ord('q'):
                    break
            cam_stream_0.release()
            cv2.destroyAllWindows()
        except cv2.error:
            print('Error: connection timeout')

    def return_cams(self, event):
        app = tk.Frame(root, name='app')
        app.pack(expand=1, fill=tk.BOTH)
        scrollable_body = Scrollable(app, width=16)
        tabs = tk.Frame(scrollable_body)
        informing = tk.Frame(scrollable_body)

        try:
            if type(event) == str:
                area_name = globals()['AreaNameTempest']
            else:
                area_name = event.widget.get()
                globals()['AreaNameTempest'] = area_name
            list_area = self.db.get_area('dict')
            id_area = list(list_area.keys())[list(list_area.values()).index(area_name)]
        except KeyError:
            id_area = '0'
            area_name = ''

        cam = 1
        step = 0
        col = 0
        row = 0

        if self.db.get_cams(id_area):
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

                if ip.split('/')[0][0:4] == 'rtsp':
                    ip_is_url = True
                    ip_to_url = ip
                    ip = ip.split('/')[2]
                    cam = 1
                    num_cams = 1
                else:
                    ip_to_url = ip
                    ip_is_url = False

                if os.system("ping -n 1 " + ip) == 0:
                    print('Info: connected to ' + ip)
                    if self.rtsp_url(ip, port, login, password, type_conn, cam) != 'NotSupport':
                        while cam < num_cams + 1:
                            if ip_is_url == True:
                                url = ip_to_url
                            else:
                                url = self.rtsp_url(ip, port, login, password, type_conn, cam)
                            img = f'{code}_{cam}_{step}.jpg'
                            if snap.get_images(url, img) == 'stop':
                                break
                            snap.get_images(url, img)

                            frame = ttk.Frame(tabs, width=200, height=200, style='TNotebook',
                                              name="frame_%s_%s" % (cam, step))
                            frame.grid(column=col, row=2 + row, padx=3, pady=3)
                            try:
                                pill_image = Image.open(os.getcwd() + '\\SnapShot\\%s_%s_%s.jpg' % (code, cam, step))
                                pill_image = pill_image.resize((200, 200), Image.ANTIALIAS)
                                globals()['pill_image_%s_%s_%s' % (code, cam, step)] = ImageTk.PhotoImage(pill_image)

                                globals()['lable_%s_%s_%s' % (code, cam, step)] = tk.Label(frame, width=200, height=200,
                                                                                           image=globals()[
                                                                                               'pill_image_%s_%s_%s' %
                                                                                               (code, cam, step)])
                                globals()['lable_%s_%s_%s' % (code, cam, step)].pack(fill=tk.BOTH)
                            except FileNotFoundError:
                                print(f'Error: {code} Image Not Found')
                                print(f'Stream: {url}')
                                pass
                            tit = ' камера %s_%s' % (cam, step)
                            button = ttk.Button(tabs,
                                                command=lambda area_name=area_name + tit, url=url: self.rtsp_cam(
                                                    area_name, url),
                                                text="Камера %s_%s" % (cam, step),
                                                name="button_%s_%s" % (cam, step))
                            button.grid(column=col, row=3 + row, padx=3, pady=3)
                            if col == 4:
                                row += 3
                                col = 0
                            else:
                                col += 1
                            cam += 1
                            tk.Label(informing, text="Loading: cam %s_%s..." % (cam, step), name="ror").grid(column=0, row=0, padx=3, pady=3)
                            informing.pack(expand=1, fill=tk.Y)
                            scrollable_body.update()
                        step += 1
                        cam = 1
                    else:
                        print('Error: Cams not supported')
                        tk.Label(informing, text="Cams not supported", name="ror").grid(column=0, row=0, padx=3, pady=3)
                else:
                    print('Error: connection to ' + ip + ' timeout')
                    tk.Label(informing, text='Ошибка подключения к адресу ' + ip, name="ror").grid(column=0, row=0, padx=3, pady=3)
                tk.Label(informing, text="Loading: cam %s_%s" % (cam, step), name="ror").grid(column=0, row=0, padx=3, pady=3)
                informing.pack(expand=1, fill=tk.Y)
                scrollable_body.update()
        else:
            tk.Label(tabs, text="Камеры отсутствуют в базе данных", name="fl").grid(column=0, row=0, padx=3, pady=3)
        tk.Label(informing, text="All cams loaded", name="ror").grid(column=0, row=0, padx=3, pady=3)
        informing.pack(expand=1, fill=tk.Y)
        tabs.pack(expand=1, fill=tk.Y)
        scrollable_body.update()

    def main_frame(self):
        app = tk.Frame(root, width=50)
        if self.db.get_area('dict'):
            list_area = self.db.get_area('dict')
            tk.Label(app, text="Выберите район").grid(column=0, row=0)
            comboExample = ttk.Combobox(app, values=list(list_area.values()), state="readonly", name="box")
            comboExample.current(0)
            comboExample.bind("<<ComboboxSelected>>", self.return_cams)
            comboExample.grid(column=0, row=1, padx=3, pady=3)

            update = ttk.Button(app, text="Обновить", command=lambda: self.return_cams('yui'), compound=tk.TOP)
            update.grid(column=1, row=1, padx=3, pady=3)

            app.pack(fill=tk.BOTH)
        else:
            tk.Label(app, text="Отсутствуют записи в базе данных").grid(column=0, row=0)
            app.pack(expand=1, fill=tk.Y)

    def bottom_frame(self):
        console = tk.Frame()
        console.pack(side=tk.BOTTOM, fill=tk.X)
        console = tk.Text(console, height=5)
        sys.stdout = StdoutRedirector(console)
        console.pack(side=tk.BOTTOM, fill=tk.X)


class TestConnect(tk.Toplevel):
    def __init__(self, menu):
        super().__init__(root)
        self.db = db
        if menu == 'regs':
            self.registrators()
        elif menu == 'check':
            self.check()
        elif menu == 'check_another':
            self.check_another()
        elif menu == 'about':
            self.about_frame()
        elif menu == 'edit_area':
            self.add_edit_area()
        elif menu == 'edit_cams':
            self.add_edit_cams()
        elif menu == 'config_frame':
            self.config_frame()

    def config_frame(self):
        cfg_frame = tk.Frame(self, name='cfg')
        cfg_frame.pack(expand=1, fill=tk.BOTH)

        title_1 = ttk.Label(cfg_frame, text='Отображать консоль сообщение?')
        title_1.place(x=10, y=10)
        title_2 = ttk.Label(cfg_frame, text='Стиль ширифта наложенного текста')
        title_2.place(x=10, y=50)

        self.combo_1 = ttk.Combobox(cfg_frame, values=[always_debug_mode_cfg, 'True', 'False'], state="readonly")
        self.combo_1.place(x=300, y=10)
        self.combo_1.current(0)

        self.combo_2 = ttk.Combobox(cfg_frame, values=[default_font_overlay_cfg, 'RussoOne-Regular.ttf', 'RussoOne-Regular.ttf'], state="readonly")
        self.combo_2.place(x=300, y=50)
        self.combo_2.current(0)

        button_1 = ttk.Button(cfg_frame, text='Сохранить', command=lambda: Configurations.write_config(
                                                                                self,
                                                                                self.combo_1.get(),
                                                                                self.combo_2.get()))
        button_1.place(x=370, y=350)

        button_2 = ttk.Button(cfg_frame, text='Выход', command=self.destroy)
        button_2.place(x=450, y=350)

        cfg_frame.pack()

        self.title("Настройки")
        self.geometry("550x400+300+50")
        self.resizable(0, 0)
        self.grab_set()
        self.focus_set()

    def registrators(self):
        app = tk.Frame(self, name='app')
        app.pack(expand=1, fill=tk.BOTH)
        scrollable_body = Scrollable(app, width=16)
        cam = tk.Frame(scrollable_body)

        self.title("Проверка регистраторов")
        #self.geometry("350x450+300+50")
        self.resizable(0, 0)
        self.grab_set()
        self.focus_set()

        list_cams = self.db.get_cams('Self')
        r = 1
        cc = 0
        tk.Label(cam, text='Адрес').grid(column=0, row=0)
        tk.Label(cam, text='Порт').grid(column=1, row=0)
        tk.Label(cam, text='Состояние').grid(column=2, row=0)
        rr = math.floor(root.winfo_screenheight()/25)
        height = rr*10
        for rows in list_cams:
            if r > 20:
                tk.Label(cam, text='Адрес').grid(column=3, row=0)
                tk.Label(cam, text='Порт').grid(column=4, row=0)
                tk.Label(cam, text='Состояние').grid(column=5, row=0)
                cc = 3
                r = 1
            if rows[0].split('/')[0] == 'rtsp:':
                addr = rows[0].split('/')[2]
            else:
                addr = rows[0]
            tk.Label(cam, text=addr).grid(column=0 + cc, row=r)
            tk.Label(cam, text=rows[1]).grid(column=1 + cc, row=r)

            if os.system("ping -n 1 " + addr) == 0:
                ttk.Label(cam, text='Good', foreground='green').grid(column=2+cc, row=r)
            else:
                ttk.Label(cam, text='Error', foreground='red').grid(column=2+cc, row=r)
            r += 1

            if len(str(rows[0])) > len('Адрес'): a = len(str(rows[0]))
            else: a = len('Адрес')
            b = len('Порт')
            if len(str(rows[1])) > len('Состояние'): c = len(str(rows[1]))
            else: c = len('Состояние')
            if cc==3: len_width = (a + b + c) * 4
            else: len_width = (a + b + c) * 2

            width = len_width*2
            self.geometry("%dx%d+300+50" % (width, height))

            app.pack(expand=1, fill=tk.BOTH)
            app.update()
            cam.pack(fill=tk.Y)
            scrollable_body.update()

    def probe_file(self, filename):
        app_ffprobe = tk.Frame(self, name='apps')

        scrollbar = tk.Scrollbar(app_ffprobe)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        out_text = tk.Text(app_ffprobe)
        out_text.pack(side=tk.BOTTOM, fill=tk.BOTH)

        ffmpeg_patch = 'ffmpeg/bin/ffprobe.exe'

        if filename.split('/')[0] == 'rtsp:' or filename.split('/')[0] == 'http:' or filename.split('/')[0] == 'https:':
            ip = filename.split('/')[2]
        else:
            ip = filename

        if os.system("ping -n 1 " + ip) == 0:
            if os.path.exists(ffmpeg_patch):

                out_text.insert(tk.END, "Please wait while the stream is checked\n")
                out_text.config(yscrollcommand=scrollbar.set)
                app_ffprobe.pack(expand=1, fill=tk.Y)
                app_ffprobe.update_idletasks()

                ffmpeg = [ffmpeg_patch, '-v', 'error', '-show_format', '-show_streams', filename]
                p = subprocess.Popen(ffmpeg, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                out, err = p.communicate()

                out_text.insert(tk.END, "==========Output==========\n")
                out_text.insert(tk.END, out)
                if err:
                    out_text.insert(tk.END, "========= Error ========\n")
                    out_text.insert(tk.END, err)
            else:
                out_text.insert(tk.END, "==========Не установлен ffprobe=========="
                                        "\n ffprobe необходимо скачать по адресу https://ffmpeg.org/download.html "
                                        "\n и распаковать в папку с программой")
        else:
            out_text.insert(tk.END, "==========Ошибка соединения=========="
                                        "\n Нет доступа к ресурсу")

        out_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=out_text.yview)

        self.title("Проверка потока видеорегистарора")
        self.geometry("650x600+200+50")
        self.grab_set()
        self.focus_set()

        app_ffprobe.pack(expand=1, fill=tk.Y)

    def check(self):
        app = tk.Frame(self, name='app')
        app.pack(expand=1, fill=tk.BOTH)
        scroll = Scrollable(app, width=16)
        add_edit_cams_scroll = tk.Frame(scroll)

        list_cams = db.get_cams('*')
        r = 1
        padx = 20
        pady = 5
        ttk.Label(add_edit_cams_scroll, text='Код района').grid(column=0, row=0, padx=padx, pady=pady)
        ttk.Label(add_edit_cams_scroll, text='Адрес').grid(column=1, row=0, padx=padx, pady=pady)
        ttk.Label(add_edit_cams_scroll, text='Порт').grid(column=2, row=0, padx=padx, pady=pady)
        ttk.Label(add_edit_cams_scroll, text='ID Района').grid(column=3, row=0, padx=padx, pady=pady)
        ttk.Label(add_edit_cams_scroll, text='').grid(column=4, row=0, padx=padx, pady=pady)
        for rows in list_cams:
            ttk.Label(add_edit_cams_scroll, text=rows[1]).grid(column=0, row=r, padx=padx, pady=pady)
            if rows[2].split('/')[0] == 'rtsp:':
                addr = rows[2].split('/')[2]
            else:
                addr = rows[2]
            ttk.Label(add_edit_cams_scroll, text=addr).grid(column=1, row=r, padx=padx, pady=pady)
            ttk.Label(add_edit_cams_scroll, text=rows[3]).grid(column=2, row=r, padx=padx, pady=pady)
            ttk.Label(add_edit_cams_scroll, text=rows[8]).grid(column=3, row=r, padx=padx, pady=pady)
            ttk.Button(add_edit_cams_scroll, text='Протестировать',
                       command=lambda
                           ip=rows[2],
                           port=rows[3],
                           login=rows[4],
                           password=rows[5],
                           type_conn=rows[7],
                           num_cams='1':
                       self.probe_file(MainFrame.rtsp_url(self, ip, port, login, password, type_conn, num_cams))
                       ).grid(column=4, row=r)
            r += 1

        self.title("Проверка потока видеорегистарора")
        self.geometry("650x400+300+50")
        self.resizable(0, 0)
        self.grab_set()
        self.focus_set()

        add_edit_cams_scroll.pack(expand=1, fill=tk.Y)
        scroll.update()

    def check_another(self):
        app = tk.Frame(self, name='app')
        app.pack(expand=1, fill=tk.BOTH)
        scroll = Scrollable(app, width=16)
        add_edit_cams_scroll = tk.Frame(scroll)
        padx = 30
        pady = 5
        ttk.Label(add_edit_cams_scroll, text='Код района').grid(column=0, row=0, padx=padx, pady=pady)
        entry_1 = ttk.Entry(add_edit_cams_scroll, width=40)
        entry_1.grid(column=1, row=0, padx=padx, pady=pady)
        ttk.Button(add_edit_cams_scroll, text='Протестировать',
                       command=lambda:
                       self.probe_file(entry_1.get())
                       ).grid(column=2, row=0)

        self.title("Проверка потока")
        self.geometry("600x400+300+50")
        self.resizable(0, 0)
        self.grab_set()
        self.focus_set()

        add_edit_cams_scroll.pack(expand=1, fill=tk.Y)
        scroll.update()

    def about_frame(self):
        help_frame = tk.Frame(self, name='app')
        help_frame.pack(expand=1, fill=tk.BOTH)
        text = tk.Text(help_frame)
        text.insert(1.0, "Программа для просмотра камер. "
                         "\nПараметры запуска:"
                         "\n    -debug_console - запускает режим вывода информации в консоль программы."
                         "\n    -gen - генерирует тестовую информацию в базе данных."
                         "\n\nРабота в программе:"
                         "\n    -Чтобы закрыть просмотр потока, необходимо нащать q"
                         "\n\nВарианты потоков:"
                         "\nНа текущий момент программа работает с сылками вида:"
                         "\n    NetSurveillance:"
                         "\n    rtsp://{ip}:{port}/user={login}&password={password}&channel={num_cams}&stream=1.sdp"
                         "\n    WebService:"
                         "\n    rtsp://{login}:{password}@{ip}:{port}/cam/realmonitor?channel={num_cams}&subtype=1"
                         "\n\nМожно использовать и свои ссылки, для этого ссылку нужно ввести в ячейку IP Адрес и выбрать тип Self")
        text.configure(state='disabled')
        text.pack()

        self.title("Помощь")
        self.geometry("650x400+300+50")
        self.grab_set()
        self.focus_set()

    def add_edit_area(self):
        add_edit = tk.Frame(self, name='add_edit')
        add_edit.pack(expand=1, fill=tk.BOTH)

        scroll = Scrollable(add_edit, width=16)
        add_edit_area_scroll = tk.Frame(scroll)

        list_areas = db.get_area('all')
        c = 0
        r = 2
        label_1 = ttk.Label(add_edit_area_scroll, text='ID')
        label_1.grid(column=0, row=0)

        label_2 = ttk.Label(add_edit_area_scroll, text='Код района')
        label_2.grid(column=1, row=0)

        label_3 = ttk.Label(add_edit_area_scroll, text='Район')
        label_3.grid(column=2, row=0)

        label_4 = ttk.Label(add_edit_area_scroll, text='Добавить')
        label_4.grid(column=3, row=0)

        label_5 = ttk.Label(add_edit_area_scroll, text='*')
        label_5.grid(column=0, row=1)

        entry_1 = ttk.Entry(add_edit_area_scroll)
        entry_1.grid(column=1, row=1)

        entry_2 = ttk.Entry(add_edit_area_scroll)
        entry_2.grid(column=2, row=1)

        button = ttk.Button(add_edit_area_scroll, text='Добавить', name="btn_1",
                            command=lambda: self.add_area(entry_1.get(), entry_2.get()))
        button.grid(column=3, row=1)
        for rows in list_areas:
            for row in rows:
                label_1 = tk.Label(add_edit_area_scroll, text=row)
                label_1.grid(column=c, row=r)
                c += 1
            button = ttk.Button(add_edit_area_scroll, text='Удалить', name="btn_%d" % r, command=lambda id = rows[0]:
                                self.delete_area(id))
            button.grid(column=c, row=r)
            c = 0
            r += 1
            height = 45+10*r
            if height < root.winfo_screenheight()-100:
                self.geometry("400x%d+1+1" % height)
            else:
                self.geometry("1200x800+1+1")
        self.title("Редактировать/добавить районы")
        #self.geometry("400x800+300+50")
        self.grab_set()
        self.focus_set()

        add_edit_area_scroll.pack(expand=1, fill=tk.Y)
        scroll.update()

    def add_edit_cams(self):
        add_edit = tk.Frame(self, name='add_edit')
        add_edit.pack(expand=1, fill=tk.BOTH)

        scroll = Scrollable(add_edit, width=16)
        add_edit_cams_scroll = tk.Frame(scroll)

        list_cams = db.get_cams('*')
        c = 0
        r = 2
        ttk.Label(add_edit_cams_scroll, text='ID').grid(column=0, row=0)
        ttk.Label(add_edit_cams_scroll, text='Код района').grid(column=1, row=0)
        ttk.Label(add_edit_cams_scroll, text='IP Адрес').grid(column=2, row=0)
        ttk.Label(add_edit_cams_scroll, text='Порт').grid(column=3, row=0)
        ttk.Label(add_edit_cams_scroll, text='Логин').grid(column=4, row=0)
        ttk.Label(add_edit_cams_scroll, text='Пароль').grid(column=5, row=0)
        ttk.Label(add_edit_cams_scroll, text='Кол-во Камер').grid(column=6, row=0)
        ttk.Label(add_edit_cams_scroll, text='Тип').grid(column=7, row=0)
        ttk.Label(add_edit_cams_scroll, text='ID Района').grid(column=8, row=0)
        ttk.Label(add_edit_cams_scroll, text='Добавить').grid(column=10, row=0)
        ttk.Label(add_edit_cams_scroll, text='*').grid(column=0, row=1)

        self.entry_1 = ttk.Entry(add_edit_cams_scroll)
        self.entry_1.grid(column=1, row=1)
        self.entry_2 = ttk.Entry(add_edit_cams_scroll)
        self.entry_2.grid(column=2, row=1)
        self.entry_3 = ttk.Entry(add_edit_cams_scroll)
        self.entry_3.grid(column=3, row=1)
        self.entry_4 = ttk.Entry(add_edit_cams_scroll)
        self.entry_4.grid(column=4, row=1)
        self.entry_5 = ttk.Entry(add_edit_cams_scroll)
        self.entry_5.grid(column=5, row=1)
        self.entry_6 = ttk.Entry(add_edit_cams_scroll)
        self.entry_6.grid(column=6, row=1)

        self.combo = ttk.Combobox(add_edit_cams_scroll, values=['NetSurveillance', 'WebService', 'none', 'Self'], state="readonly")
        self.combo.grid(column=7, row=1)
        self.combo.current(0)

        list_area = self.db.get_area('dict')
        self.comboExample = ttk.Combobox(add_edit_cams_scroll, values=list(list_area.values()), state="readonly")
        self.comboExample.grid(column=8, row=1)
        self.comboExample.current(0)

        ttk.Button(add_edit_cams_scroll, text='Добавить', command=lambda:
            self.add_cams(self.entry_1.get(),
                          self.entry_2.get(),
                          self.entry_3.get(),
                          self.entry_4.get(),
                          self.entry_5.get(),
                          self.entry_6.get(),
                          self.combo.get(),
                          list(list_area.keys())[list(list_area.values()).index(self.comboExample.get())])).grid(column=10, row=1)
        for rows in list_cams:
            for row in rows:
                if str(row).split('/')[0] == ('rtsp:' or 'http' or 'https'): row = row.split('/')[2]
                ttk.Label(add_edit_cams_scroll, text=row).grid(column=c, row=r)
                c += 1
            ttk.Button(add_edit_cams_scroll, text='Удалить', command=lambda id = rows[0]: self.delete_cams(id)).grid(column=c + 1, row=r)
            c = 0
            r += 1
            height = 45+25*r
            if height < root.winfo_screenheight()-100:
                self.geometry("1200x%d+1+1" % height)
            else:
                self.geometry("1200x800+1+1")
        self.title("Редактировать/добавить районы")
        #self.geometry("1200x800+1+1")
        self.grab_set()
        self.focus_set()

        add_edit_cams_scroll.pack(expand=1, fill=tk.Y)
        scroll.update()

    def delete_area(self, id):
        self.db.delete_area(id)
        self.add_edit_area()

    def delete_cams(self, id):
        self.db.delete_cams(id)
        self.add_edit_cams()

    def add_area(self, entry_1, entry_2):
        self.db.add_area(entry_1, entry_2)
        self.add_edit_area()

    def add_cams(self, code, ip, port, login, password, num_cams, type_conn, id_area):
        self.db.add_cams(code, ip, port, login, password, num_cams, type_conn, id_area)
        self.add_edit_cams()


if __name__ == "__main__":
    root = tk.Tk()
    Configurations()
    db = DBInOu()
    TopMenu(root)
    snap = GetSnap()
    app = MainFrame(root)
    root.title("ViewCam ПФР")
    root.geometry("1200x720+1+1")
    root.resizable(0, 0)
    root.mainloop()
