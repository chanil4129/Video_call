import paramiko

# SFTP 서버 정보
hostname = "192.1.1.1" # IP
port = 22
username = "username"
password = "password"

# SFTP 클라이언트 생성
transport = paramiko.Transport((hostname, port))
transport.connect(username=username, password=password)
sftp = paramiko.SFTPClient.from_transport(transport)

# 파일 업로드 및 다운로드
local_file_path = "C:\\Users\\user\\Pictures\\1.png" # 업로드 하려는 파일 경로(windows)
remote_file_path = "/home/1.png" # 다운로드 하려는 파일 경로(linux)
sftp.put(local_file_path, remote_file_path)

# SFTP 클라이언트 종료
sftp.close()
transport.close()
