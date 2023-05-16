import paramiko
import os
import threading

# SFTP 서버 구성을 위한 클래스 정의
class SFTPServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        # 인증 로직 구현
        return paramiko.AUTH_SUCCESSFUL

    def check_channel_request(self, kind, chanid):
        # 채널 요청 검증
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def get_allowed_auths(self, username):
        # 허용되는 인증 방법 구현
        return 'password'

    def check_channel_exec_request(self, channel, command):
        # 명령어 실행 요청 검증
        return True

# SFTP 서버 설정
host_key = paramiko.RSAKey.generate(2048)
sftpserver = paramiko.Transport(('127.0.0.1', 22))
sftpserver.add_server_key(host_key)
server = SFTPServer()

# SFTP 서버 실행
try:
    sftpserver.start_server(server=server)
except Exception as e:
    print(f"Error: {str(e)}")

# SFTP 클라이언트 연결 대기
channel = sftpserver.accept(20)
if channel is None:
    print("SFTP client connection failed")
    sftpserver.close()
    sys.exit(1)

# 파일 업로드 처리
sftp = channel.makefile("rU")
sftp.write("SFTP server ready.\n")
sftp.flush()

while True:
    header = sftp.readline()
    if header.startswith("C"):
        parts = header.split()
        size = int(parts[1])
        filename = parts[2]
        print(f"Uploading file {filename} ({size} bytes)")
        data = sftp.read(size)
        print(data)
    else:
        break

sftp.close()
channel.close()
sftpserver.close()
