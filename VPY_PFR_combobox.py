import tkinter as tk
from tkinter import ttk
import sqlite3
import cv2

app = tk.Tk()
app.title("VPY ПФР")
app.geometry("1030x720+1+1")

conn = sqlite3.connect('base.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS AREAS (id integer primary key, CODE integer, AREA text, IP text, PORT integer, LOGIN text, PASSWORD text, CAMS integer , MODE text)''')
c.execute('''CREATE TABLE IF NOT EXISTS area (id integer primary key, area_title text)''')
c.execute('''CREATE TABLE IF NOT EXISTS cams (id integer primary key, cam_title text, cam_url text, id_area integer, FOREIGN  KEY (id_area) REFERENCES area(id))''')
conn.commit()


def RTSP_URL(IP, LOGIN, PASS, MODE, CAMS):
    if MODE == 'NetSurveillance':
        url = f'rtsp://{IP}:554/user={LOGIN}&password={PASS}&channel={CAMS}&stream=1.sdp?real_stream--rtp-caching=100'
    elif MODE == 'WebService':
        url = f'rtsp://{LOGIN}:{PASS}@{IP}:554/cam/realmonitor?channel={CAMS}&subtype=1'

    else:
        url = 'none'
    print(url)
    return url

def get_cams_from_area(id_area):
    dict_current_area = {}
    c.execute("SELECT * FROM cams WHERE id_area = (?)", [id_area])
    rows = c.fetchall()
    for row in rows:
        dict_current_area[row[1]] = '%s' % row[2]
    return dict_current_area

def get_cams_from_areas(id_area):
    c.execute("SELECT * FROM areas WHERE id = (?)", [id_area])
    rows = c.fetchall()
    return rows


def view_from_base():
    dict_areas = {}
    c.execute('''SELECT * FROM areas''')
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
    #cam_stream_0 = cv2.VideoCapture('rtsp://upf834:5896ae@10.2.29.190:554/cam/realmonitor?channel=1&subtype=1')
    #cam_stream_0 = cv2.VideoCapture('rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov')
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
    #the_selection1 = event.widget
    id_area = list(dict_area.keys())[list(dict_area.values()).index(the_selection0)]
    cam = 0
    col = 0
    row = 0
    #dict_cams = get_cams_from_area(id_area)
    row_area = get_cams_from_areas(id_area)
    #for key, value in dict_cams.items():
    for rows in row_area:
        id = rows[0]
        areas = rows[2]
        ip = rows[3]
        login = rows[5]
        password = rows[6]
        cams = rows[7]
        mode = rows[8]

    while cam < 10:
        frame = ttk.Frame(app, width=200, height=200, style='TNotebook', name="frame_%s" % cam)
        frame.grid(column=col, row=2 + row, padx=3, pady=3)
        URL = RTSP_URL(ip, login, password, mode, cam)
        #button = tk.Button(app, command=lambda key=key, value=value: rtsp_cam(key, value), text="Камера %s" % key, bg='#aaaaff', name="button_%s" % cam)
        button = tk.Button(app, command=lambda areas=areas, URL=URL: rtsp_cam(areas, URL), text="Камера %s" % cam,
                           bg='#aaaaff', name="button_%s" % cam)
        #print(key, ' = ', value)
        button.grid(column=col, row=3 + row, padx=3, pady=3)
        if col == 4:
            row += 3
            col = 0
        else:
            col += 1
        cam += 1


dict_area = view_from_base()
labelTop = tk.Label(app, text="Выберите район").grid(column=0, row=0)
comboExample = ttk.Combobox(app, values=list(dict_area.values()), state="readonly", name="box")
comboExample.grid(column=0, row=1)
comboExample.current(0)
comboExample.bind("<<ComboboxSelected>>", return_cams)
app.mainloop()