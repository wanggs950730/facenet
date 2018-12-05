import tkinter as tk
from tkinter.filedialog import askopenfilename, askdirectory
from tkinter import messagebox
import tkinter.font as tkFont
# from demo_neo import Extractor
from PIL import Image
from PIL import ImageTk
from tkinter import *
import os
import threading
import time
import numpy as np
import uuid
import cv2
import pdb
import socket
from GUI.widgets import *
import sys

import face
import pymysql
import sql_operation


try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("10.98.57.165",1994)) # address port
except socket.error as msg:
    print(msg)
    sys.exit(1)

face_recognition = face.Recognition()
identify = face_recognition.identify

# face_identify = face.Identifier()

# 打开数据库连接
db = pymysql.connect("10.98.57.165","host","employee","EmployeeDB")
# 使用 cursor() 方法创建一个游标对象 cursor
cursor = db.cursor()

class Extractor_GUI():

    global faces, flag
    
    def __init__(self):
        self.__init_gui()
        # self.__init_model()
    def __init_gui(self):

        self.sql = sql_operation.Sql(cursor, db)
        self.faces = [] # record every frame 
        self.faces_name = None  # record the name 
        self.flag = True # if false: already send the embedding to the server
       
        self.window = tk.Tk()
        self.window.wm_title('Face_Recognition')
        self.window.config(background = '#FFFFFF')

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        menubar = Menu(self.window)
        menubar.add_command(label='Start',command = self.__action_read_frame, font=("黑体", 15))
        menubar.add_command(label='Close',command = self._action_close_camera,font=("黑体", 15))
        
        self.window.config(menu=menubar)
        # font type and size
        ft = tkFont.Font(size=15, weight=tkFont.BOLD)

        self.fm_control = tk.Frame(self.window, width=400, height=40, background = '#FFFFFF')
        self.fm_control.grid(row = 0, column=0, padx=0, pady=0)
       
        self.canvas = ICanvas(self.window, width = 400, height = 400)
        self.canvas.grid(row = 1, column = 0, padx=5, pady=5)
        img = misc.imread('1.gif')
        self.canvas.add(img)


        self.fm_status = tk.Frame(self.window, width = 200, height = 20, background = '#FFFFFF')
        self.fm_status.grid(row = 0, column=1, padx=10, pady=10)
        self.time_lable = tk.Label(self.fm_status, text="time", background = '#FFFFFF',font=ft)
        self.time_lable.grid(row = 0, column=0, padx=1, pady=2)


        self.image = tk.Frame(self.window, width = 200, height = 400, background = '#FFFFFF')
        self.image.grid(row = 1, column = 1, padx =5, pady = 5)
        # show photo
        load = Image.open('camera.jpg')
        self.render_nobody = ImageTk.PhotoImage(load) #定义初始照片框位置的图片
        self.image_lable = tk.Label(self.image, image = self.render_nobody)
        self.image_lable.place(x=30, y=50)
        #show unknown photo
        load_unknown = Image.open('unknown.jpg')
        self.render_unknown = ImageTk.PhotoImage(load_unknown) #定义未知人员照片
        self.render_my_photo = ImageTk.PhotoImage(load_unknown) #定义数据库存在的人员初始照片;\
                                                                #若不定义，局部变量会被回收，不能正常显示 
        # show name
        self.image_name1 = tk.Label(self.image, text = '姓名：', background = '#FFFFFF', font=ft)
        self.image_name2 = tk.Label(self.image, background = '#FFFFFF',font=ft)
        self.image_name2['text'] = 'Nobody'
        self.image_name1.place(x=10, y=220)
        self.image_name2.place(x=60, y=220)

        self.empty1 = tk.Frame(self.window, width=400,height=20,background= '#FFFFFF')
        self.fm_status.grid(row = 2, column=0, padx=10, pady=10)
        self.empty1 = tk.Frame(self.window,width=200,height=20,background= '#FFFFFF')
        self.fm_status.grid(row = 2, column=1, padx=10, pady=10)

        self.cap = cv2.VideoCapture(0)


    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to leave?"):
            if self.cap.isOpened():
                self.cap.release()
            self.window.destroy()


    def __action_read_frame(self):
        self.from_video()

    def _action_close_camera(self):
        self.close_camera()

    def draw(self, frame):

        if bool(self.faces):
            # paint circle and print 检测ing *********
            face_bb = self.faces[0].bounding_box.astype(int)

            cv2.rectangle(frame,
                            (face_bb[0],face_bb[1]), (face_bb[2],face_bb[3]),
                            (0,255,0), 2)
            
            if self.faces_name is None:
                cv2.putText(frame, "detect faces", (face_bb[0],face_bb[3]),
                                cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),thickness=2, lineType=2)
            else:
                cv2.putText(frame, "OK", (face_bb[0],face_bb[3]),
                                cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),thickness=2, lineType=2)
            # print(faces[0].name)

            # add_overlay(frame,faces[0])
            # 向数据库插入识别的人脸数据
            # if bool(faces):
            #     sql = "INSERT INTO Record (`name`) \
            #        VALUES ('%s')" % faces[0].name
            #     # insert data
            #     db_operation(sql)

        else: # no face in the camera
            self.flag = True # next face found should send to the server
            self.faces = [] # clear the face forefront
            self.faces_name = None # clear the name


    def from_video(self):

        if not self.cap.isOpened():
            self.cap = cv2.VideoCapture(0)

        frame_interval = 10  # Number of frames after which to run face detection
        # fps_display_interval = 5  # seconds
        # frame_rate = 0
        frame_count = 0

        ret,frame = self.cap.read()
        while ret:

            if not ret: # 摄像头关闭，则退出监测程序
                print("Camera closed!")
            
            if (frame_count % frame_interval) == 0: # 40帧检测摄像头视频一次
                self.faces = face_recognition.detect_face(frame) # face.py在identify中进行了阈值判断

                self.draw(frame)
           
            # print(frame)
            img = cv2.flip(frame,1)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # print(img.shape)

            self.canvas.add(img)

            #show photo
            if self.faces and self.faces_name is not None:
                if self.faces_name == 'Unidentified':
                    self.image_lable['image'] = self.render_unknown
                    self.image_name2['text'] = self.faces_name
                    self.flag = True
                else:
                    self.render_my_photo = self.sql.get_photo(self.faces_name) #需要先定义my_photo，\
                    self.image_lable['image'] = self.render_my_photo #否则(即没有self.my_photo过渡)局部变量\
                    self.image_name2['text'] = self.faces_name #-在加载时就会被回收，在图片框只会显示灰色图片
                    cv2.waitKey(1000)
                    self.flag = True
            else:
                self.image_lable['image'] = self.render_nobody
                self.image_name2['text'] = 'Nobody'

            self.window.update_idletasks()
            self.window.update()

            ret,frame = self.cap.read()
            frame_count += 1


    def close_camera(self):
        self.cap.release()
        img = misc.imread('1.gif')
        self.canvas.add(img)
        self.window.update_idletasks()
        self.window.update()


    def handle_face_name(self): # Parallel Processing

        while True:
            if bool(self.faces) and self.flag:
                self.faces = identify(self.faces)
                # print(faces[0].embedding)
                self.flag = False
                try:
                    s.send(str(self.faces[0].embedding).encode(encoding='utf_8', errors='strict'))
                except Exception:
                    self.flag = True
                    continue
                try:
                    self.faces_name = s.recv(1024).decode('utf-8') # turn to str
                    self.faces[0].name = self.faces_name
                    # faces[0].name = face_identify.identify(faces[0])
                    print(self.faces_name)
                except Exception:
                    continue
                print("OK")

                # else: # only one face
                #     try:
                #         faces[0].name = s.recv(1024).decode('utf-8') # turn to str
                #         # faces[0].name = face_identify.identify(faces[0])
                #         print(faces[0].name)
                #     except Exception:
                #         continue
            else:
                continue


    # def handle(self, signal, *args, **kwargs): # Parallel Processing
    #     while not signal.isSet():
    #         now = time.strftime("%Y-%D %H:%M:%S")
    #         self.time_lable['text'] = str(now)
    #         print(now)
    #     self.window.quit()


    def launch(self):
        self.window.mainloop()




if __name__ == '__main__':
    ext = Extractor_GUI()

    # subprocess
    t = threading.Thread(target=ext.handle_face_name)
    t.start()

    ext.launch()

    

