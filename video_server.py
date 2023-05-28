import asyncio
import websockets
import pyautogui
import json
import base64
import io
import paramiko
import tkinter as tk
import threading
import socket
import cv2
import pickle
import struct
import imutils
from multiprocessing import Process
import tkinter.filedialog

'''
화상 및 파일 전송 프로그램(서버)

이 코드는 SFTP 서버를 설정하고, 이 서버에 파일을 업로드하는 기능을 제공하는 GUI를 생성
또한 서버에서 비디오 데이터를 송신하고 해당 데이터를 화면에 표시
이를 위해 여러 쓰레드가 병렬로 실행
'''
        
class SFTPServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        # 사용자 이름과 비밀번호가 일치하는지 확인
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_request(self, kind, chanid):
        # 클라이언트로부터 채널 요청이 왔을 때의 동작 정의
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        # 허용되는 인증 방법을 반환
        return 'password'

    def check_channel_exec_request(self, channel, command):
        # 채널 실행 요청을 확인
        return True

class SFTPServerUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SFTP Server")

        # 클라이언트의 SFTP 서버에 연결하여 SFTP 클라이언트 생성
        client_hostname = "192.168.0.0"  # 클라이언트 IP 주소
        client_port = 22  # 클라이언트 포트 번호
        client_username = "username"  
        client_password = "password"  

        # 클라이언트 호스트와 포트로 트랜스포트 객체 생성 및 연결
        self.client_transport = paramiko.Transport((client_hostname, client_port))
        self.client_transport.connect(username=client_username, password=client_password)
        # 트랜스포트를 사용해 SFTP 클라이언트 생성
        self.client_sftp = paramiko.SFTPClient.from_transport(self.client_transport)

        # GUI 생성 - 파일 업로드 버튼 및 종료 버튼 추가
        self.upload_button = tk.Button(self, text="Select File to Upload", command=self.sftp_upload)
        self.upload_button.pack()
        self.quit_button = tk.Button(self, text="QUIT", fg="red", command=self.on_closing)
        self.quit_button.pack()

    def sftp_upload(self):
        # 파일 다이얼로그를 통해 업로드할 파일 선택
        filepath = tk.filedialog.askopenfilename()
        if filepath:
            # 선택된 파일의 이름을 가져와서 원격 경로 생성
            filename = filepath.split("/")[-1]
            remote_file_path = f'/home/FILE/{filename}'
            # 선택된 파일을 원격 경로로 업로드
            self.client_sftp.put(filepath, remote_file_path)
            print(f"파일 {filename}이(가) 클라이언트에 성공적으로 업로드되었습니다.")

    def on_closing(self):
        # 프로그램 종료시 SFTP 클라이언트 및 트랜스포트를 닫고 GUI를 파괴
        self.client_sftp.close()
        self.client_transport.close()
        self.destroy()

def start_sftp_server():
    # RSA 키를 생성하고 SFTP 서버를 설정
    host_key = paramiko.RSAKey.generate(2048)
    sftpserver = paramiko.Transport(('127.0.1.1', 22))
    sftpserver.add_server_key(host_key)
    server = SFTPServer()

    # 서버를 시작
    try:
        sftpserver.start_server(server=server)
    except Exception as e:
        print(f"에러: {str(e)}")

# 클라이언트로 비디오 프레임 데이터를 송신
def video_send_frames(video_client_socket):
    while True:
        if video_client_socket:
            # 'test_video.mp4' 파일에서 비디오를 읽기
            vid = cv2.VideoCapture('test_video.mp4')

            while(vid.isOpened()):
                img,frame = vid.read()
                a = pickle.dumps(frame)
                message = struct.pack("Q",len(a))+a

                # 생성한 메시지를 소켓을 통해 클라이언트에게 보내기
                video_client_socket.sendall(message)
                cv2.imshow("Server_Client",frame)

                # q를 누르면 창 종료
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    video_client_socket.close()
                    cv2.destroyAllWindows()
                    break

def run_gui():
    # 메인 쓰레드에서 GUI를 실행
    server_ui = SFTPServerUI()
    server_ui.protocol("WM_DELETE_WINDOW", server_ui.on_closing)
    server_ui.mainloop()

# 별도의 쓰레드에서 SFTP 서버를 시작
server_thread = threading.Thread(target=start_sftp_server)
server_thread.start()

# GUI를 별도의 쓰레드에서 실행
gui_thread = threading.Thread(target=run_gui)
gui_thread.start()


# 비디오 전송 설정
video_server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
video_host_name  = socket.gethostname()
video_host_ip = socket.gethostbyname(video_host_name)
video_port = 10050

socket_address = ('0.0.0.0',video_port)
video_server_socket.bind(socket_address)
video_server_socket.listen(5)

# 비디오 클라이언트와 연결
video_client_socket,video_addr = video_server_socket.accept()

# 비디오 전송 쓰레드 시작
video_send_thread = threading.Thread(target=video_send_frames, args=(video_client_socket,))
video_send_thread.start()

# 두 쓰레드가 종료될 때까지 기다림
server_thread.join()
gui_thread.join()
video_send_thread.join()
