import tkinter as tk
from tkinter import ttk
import sqlite3
import cv2

app = tk.Tk()
app.title("VPY ПФР")
app.geometry("1030x720+1+1")

conn = sqlite3.connect('base.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS area (id integer primary key, code text, area_title text)''')
c.execute('''CREATE TABLE IF NOT EXISTS cams (
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
conn.commit()


def rtsp_url(ip, port, login, password, type_conn, num_cams):
    if type_conn == 'NetSurveillance':
        url = f'rtsp://{ip}:{port}/user={login}&password={password}&channel={num_cams}&stream=1.sdp?real_stream--rtp-caching=100'
    elif type_conn == 'WebService':
        url = f'rtsp://{login}:{password}@{ip}:{port}/cam/realmonitor?channel={num_cams}&subtype=1'
    else:
        url = 'none'
    return url


def get_cams_from_area(id_area):
    c.execute("SELECT * FROM cams WHERE id_area = (?)", [id_area])
    rows = c.fetchall()
    return rows


def view_from_base():
    dict_areas = {}
    c.execute('''SELECT * FROM area''')
    rows = c.fetchall()
    for row in rows:
        dict_areas[row[0]] = '%s' % row[2]
    return dict_areas


def add_area_to_base(area):
    c.execute('''INSERT INTO area(area_title) VALUES (?)''', [area])
    conn.commit()


def add_area_to_cam(cam_title, cam_url, id_area):
    c.execute('''INSERT INTO area(cam_title, cam_url, id_area) VALUES (?, ?, ?)''', [cam_title, cam_url, id_area])
    conn.commit()


def rtsp_cam(title_cams, url_cams):
    cam_stream_0 = cv2.VideoCapture(url_cams)
    while True:
        cam_0, frame_0 = cam_stream_0.read()
        cv2.imshow(title_cams, frame_0)
        if cv2.waitKey(1) == ord('q'):
            break
    cam_stream_0.release()
    cv2.destroyAllWindows()


def return_cams(event):
    the_selection0 = event.widget.get()
    id_area = list(dict_area.keys())[list(dict_area.values()).index(the_selection0)]
    cam = 1
    step = 0
    col = 0
    row = 0
    row_area = get_cams_from_area(id_area)
    for rows in row_area:
        id = rows[0]
        code = rows[1]
        ip = rows[2]
        port = rows[3]
        login = rows[4]
        password = rows[5]
        num_cams = rows[6]
        type_conn = rows[7]
        if rtsp_url(ip, port, login, password, type_conn, num_cams) != 'none':
            while cam < num_cams+1:
                frame = ttk.Frame(app, width=200, height=200, style='TNotebook', name="frame_%s_%s" % (cam, step))
                frame.grid(column=col, row=2 + row, padx=3, pady=3)
                url = rtsp_url(ip, port, login, password, type_conn, cam)
                button = tk.Button(app, command=lambda the_selection0=the_selection0, url=url: rtsp_cam(the_selection0, url),
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
        else:
            tk.Label(app, text="Cams not supported", name="frame_%s" % id).grid(column=2, row=1, padx=3, pady=3)


dict_area = view_from_base()
labelTop = tk.Label(app, text="Выберите район").grid(column=0, row=0)
comboExample = ttk.Combobox(app, values=list(dict_area.values()), state="readonly", name="box")
comboExample.grid(column=0, row=1)
comboExample.current(0)
comboExample.bind("<<ComboboxSelected>>", return_cams)
app.mainloop()
