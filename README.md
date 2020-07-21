# V-PY_PFR
![img](https://user-images.githubusercontent.com/66995111/88040278-194e0b00-cb62-11ea-9c1e-646af5b38418.png)


This program is designed to help you work with registrars and ip cameras. This program saves usernames and passwords for authorization on ip cameras and registrars in order to have quick access to the device without web authorization, and can also test and verify the video streams.

![img2](https://user-images.githubusercontent.com/66995111/88041340-af366580-cb63-11ea-9dc0-02f1e01ff443.png) 
![img3](https://user-images.githubusercontent.com/66995111/88041349-b198bf80-cb63-11ea-9299-b15a45f83797.png)


At the moment, the program can work with links of the following type:

>  rtsp://{ip}:{port}/user={login}&password={password}&channel={num_cams}&stream=1.sdp

>  rtsp://{login}:{password}@{ip}:{port}/cam/realmonitor?channel={num_cams}&subtype=1

>  In progress...

**To use this program, you will need ffmpeg and ffprobe. So download ffmpeg and unpack the files to the ffmpeg folder in the root of the program**
