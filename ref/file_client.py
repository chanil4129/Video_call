import paramiko
import tkinter as tk
from tkinter import filedialog
import threading

# SFTP 서버 정보
hostname = "192.168.0.0"
port = 22
username = "username"
password = "password"

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

    def create_widgets(self):
        self.upload_button = tk.Button(self, text="Select File to Upload", command=self.sftp_upload)
        self.upload_button.pack()

        self.quit_button = tk.Button(self, text="QUIT", fg="red", command=self.close_sftp)
        self.quit_button.pack()

    def sftp_upload(self):
        filepath = filedialog.askopenfilename()
        if filepath:
            filename = filepath.split("/")[-1]  # 파일명 추출
            remote_file_path = f'/tmp/{filename}'  # 변경할 부분: 목적지 경로
            self.sftp.put(filepath, remote_file_path)
            print(f"File {filename} uploaded successfully.")

    def close_sftp(self):
        # SFTP 클라이언트 종료
        self.sftp.close()
        self.transport.close()
        self.quit()

def run_gui():
    app = SFTPUploadGUI()
    app.mainloop()

if __name__ == "__main__":
    gui_thread = threading.Thread(target=run_gui)
    gui_thread.start()

    # GUI 쓰레드가 종료될 때까지 기다림
    gui_thread.join()
