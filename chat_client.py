import asyncio
import websockets
import tkinter as tk
import aiohttp
from aiohttp import web

'''
채팅 프로그램(클라이언트)

tkinter를 사용하여 만든 WebSocket 클라이언트
asyncio와 websockets 라이브러리를 이용하여 비동기적으로 메시지를 주고 받음 
'''

class ChatClient(tk.Tk):
    def __init__(self, loop):
        super().__init__()

        # 윈도우 제목
        self.title("Client")

        # 이벤트 루프
        self.loop = loop

        # WebSocket 클라이언트 초기화
        self.websocket = None

        # 대화 내용이 출력되는 텍스트 박스를 생성하고 초기 상태를 비활성화로 설정
        self.chat_box = tk.Text(self, state='disabled')
        self.chat_box.pack()  # GUI에 추가

        # 사용자의 메시지를 입력받는 엔트리 위젯을 생성
        self.msg_entry = tk.Entry(self)
        # 엔트리 위젯에 Return (Enter) 키 이벤트 핸들러를 연결
        self.msg_entry.bind("<Return>", self.on_entry_return)
        self.msg_entry.pack()  # GUI에 추가

        # 윈도우가 닫힐 때 호출되는 함수를 설정
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    # WebSocket 서버에 연결하는 비동기 메서드
    async def connect(self):
        self.websocket = await websockets.connect('ws://192.168.0.0:8765')

    # 서버로부터 메시지를 받는 비동기 메서드
    async def receive_message(self):
        while True:
            msg = await self.websocket.recv()  # 메시지를 받기
            self.chat_box.configure(state='normal')  # 텍스트 박스를 활성화
            self.chat_box.insert('end', f"Other: {msg}\n")  # 받은 메시지를 텍스트 박스에 추가
            self.chat_box.configure(state='disabled')  # 텍스트 박스를 다시 비활성화
            print(f"Other : {msg}")  # 받은 내용을 콘솔에 출력

    # Return 키 이벤트 핸들러
    def on_entry_return(self, event):
        msg = self.msg_entry.get()  # 입력된 메시지를 가져오기
        self.msg_entry.delete(0, 'end')  # 엔트리 위젯의 내용을 지우기
        self.loop.create_task(self.websocket.send(msg))  # 메시지를 서버에 보내기
        self.chat_box.configure(state='normal')  # 텍스트 박스를 활성화
        self.chat_box.insert('end', f"Me: {msg}\n")  # 보낸 메시지를 텍스트 박스에 추가
        self.chat_box.configure(state='disabled')  # 텍스트 박스를 다시 비활성화
        print(f"Me : {msg}")  # 보낸 내용을 콘솔에 출력

    # 윈도우가 닫힐 때 호출되는 메서드
    def on_closing(self):
        self.loop.create_task(self.websocket.close())  # WebSocket 연결을 닫기
        self.destroy()  # 윈도우를 닫기


if __name__ == "__main__":
    # 이벤트 루프를 가져오기
    loop = asyncio.get_event_loop()

    # ChatClient 인스턴스를 생성
    chat_client = ChatClient(loop)

    # 서버에 연결
    loop.run_until_complete(chat_client.connect())
    # 메시지를 받는 태스크를 생성
    loop.create_task(chat_client.receive_message())

    # Tkinter GUI를 업데이트하는 함수
    def run_tk(root, interval=0.05):  # 50 ms
        def update():
            root.update()  # GUI를 업데이트
            loop.call_later(interval, update)  # 다음 업데이트를 예약
        loop.call_soon(update)  # 첫 업데이트를 예약
        loop.run_forever()  # 이벤트 루프를 실행

    # run_tk 함수를 호출하여 GUI를 실행
    run_tk(chat_client)
