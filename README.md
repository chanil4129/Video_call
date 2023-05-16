### Linux
가상환경 설정
```
sudo apt-get update
sudo apt-get install python3.9-dev python3.9-venv
python3 -m venv venv

// 가상환경 실행
source venv/bin/activate
```

라이브러리 설정
```
// pip 최신 버전으로 업그레이드
pip install --upgrade pip

// remote_server
sudo apt-get install python3.9-tk python3.9-dev
pip install websockets
pip install pyautogui
pip install Pillow


// remote_client
pip install Image
pip install websockets

// file_server
pip install --upgrade pip
pip install setuptools_rust
sudo apt install curl
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
pip install bcrypt
pip install paramiko
```