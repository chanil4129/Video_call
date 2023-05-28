import base64
import io
import json
import tkinter as tk
from PIL import Image, ImageTk
import websockets
import asyncio
import paramiko
from tkinter import filedialog
import aiohttp
from aiohttp import web
import socket
import threading
import cv2
import pickle
import struct
import imutils

'''
화상 및 파일 전송 프로그램(클라이언트)

위의 코드는 SFTP와 소켓을 사용하여 파일 업로드 및 비디오 수신을 처리하는 기능을 포함한 GUI 애플리케이션을 생성 
사용자가 파일을 선택하면, 선택한 파일이 SFTP를 통해 서버에 업로드
또한 서버에서 비디오 데이터를 수신하고 해당 데이터를 화면에 표시
'''

class SFTPUploadGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SFTP Upload")
        
        # SFTP 클라이언트 생성 및 연결
        self.transport = paramiko.Transport((hostname, port))
        self.transport.connect(username=username, password=password)
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        
        # GUI 구성
        self.create_widgets()

    # 위젯 생성
    def create_widgets(self):
        self.upload_button = tk.Button(self, text="Select File to Upload", command=self.sftp_upload)
        self.upload_button.pack()

        self.quit_button = tk.Button(self, text="QUIT", fg="red", command=self.close_sftp)
        self.quit_button.pack()

    # 업로드
    def sftp_upload(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            filename = filepath.split("/")[-1]  # 파일명 추출
            remote_file_path = f'/home/FILE/{filename}'  # 변경할 부분: 목적지 경로
            self.sftp.put(filepath, remote_file_path)
            print(f"File {filename} uploaded successfully.")

    def close_sftp(self):
        # SFTP 클라이언트 종료
        self.sftp.close()
        self.transport.close()
        self.quit()

# 비디오 프레임 데이터 수신 및 디코딩
def video_rev_frames(video_client_socket):
    data = b""
    payload_size = struct.calcsize("Q")
    while True :
        while len(data) < payload_size:
            packet = video_client_socket.recv(4*1024) # 4096 바이트를 수신
            if not packet: break
            data+=packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q",packed_msg_size)[0]

        # 전체 프레임을 수신할 때까지 데이터를 계속 수신
        while len(data) < msg_size:
            data += video_client_socket.recv(4*1024)
        frame_data = data[:msg_size]
        data  = data[msg_size:]

        # 프레임 데이터를 디코딩
        frame = pickle.loads(frame_data)

        # 디코딩된 프레임을 화면에 표시
        cv2.imshow("Client_Server",frame)

        # q를 눌러 창 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            video_client_socket.close()
            cv2.destroyAllWindows()
            break



# SFTP 서버 정보
hostname = "192.168.0.0"
port = 22
username = "username"
password = "password"

ADDR="ws://192.168.0.0:8765"
video_client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
video_host_ip = '192.168.0.0'
video_port = 10050

# SFTP
def run_gui():
    app = SFTPUploadGUI()
    app.mainloop()

gui_thread = threading.Thread(target=run_gui)
gui_thread.start()


# 비디오전송
video_client_socket.connect((video_host_ip,video_port)) 
print('서버에 연결되었습니다.')

video_rev_thread = threading.Thread(target=video_rev_frames, args=(video_client_socket, ))
video_rev_thread.start()

video_rev_thread.join()
gui_thread.join()
