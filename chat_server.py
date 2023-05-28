import asyncio
import websockets
import tkinter as tk

'''
채팅 프로그램(서버)

tkinter를 사용하여 만든 WebSocket 서버. 
특징은 서버 역할과 동시에 이 서버를 사용자가 직접 이용
asyncio와 websockets 라이브러리를 이용하여 비동기적으로 메시지를 주고 받음 
클라이언트로부터 메시지를 받으면 화면에 출력하고, 사용자가 메시지를 입력하면 모든 클라이언트에게 보내기
'''

class ChatServer(tk.Tk):
    def __init__(self, loop):
        super().__init__()

        # 윈도우 제목
        self.title("Server")

        # 이벤트 루프를 저장
        self.loop = loop

        # WebSocket 서버를 초기화
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

    # WebSocket 서버를 시작하는 비동기 메서드
    async def start_server(self):
        self.websocket = await websockets.serve(self.server, '0.0.0.0', 8765)

    # 클라이언트로부터 메시지를 받는 비동기 메서드
    async def server(self, websocket, path):
        connected.add(websocket)
        try:
            while True:
                message = await websocket.recv()  # 메시지를 받기
                print(f"Other: {message}")  # 받은 내용을 콘솔에 출력
                self.chat_box.configure(state='normal')  # 텍스트 박스를 활성화
                self.chat_box.insert('end', f"Other: {message}\n")  # 받은 메시지를 텍스트 박스에 추가
                self.chat_box.configure(state='disabled')  # 텍스트 박스를 다시 비활성화

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            connected.remove(websocket)  # 연결이 끊긴 클라이언트를 제거

    # Return 키 이벤트 핸들러
    def on_entry_return(self, event):
        msg = self.msg_entry.get()  # 입력된 메시지를 가져오기
        self.msg_entry.delete(0, 'end')  # 엔트리 위젯의 내용을 지우기

        for conn in connected:
            self.loop.create_task(conn.send(msg))  # 메시지를 모든 클라이언트에 보내기
            print(f"Me: {msg}")  # 보낸 내용을 콘솔에 출력
            self.chat_box.configure(state='normal')  # 텍스트 박스를 활성화
            self.chat_box.insert('end', f"Me: {msg}\n")  # 보낸 메시지를 텍스트 박스에 추가
            self.chat_box.configure(state='disabled')  # 텍스트 박스를 다시 비활성화

    # 윈도우가 닫힐 때 호출되는 메서드
    def on_closing(self):
        for conn in connected:
            self.loop.create_task(conn.close())  # 모든 WebSocket 연결을 닫기
        self.destroy()  # 윈도우를 닫기


if __name__ == "__main__":
    # 연결된 클라이언트를 저장할 집합
    connected = set()

    # 이벤트 루프를 가져오기
    loop = asyncio.get_event_loop()

    # ChatServer 인스턴스를 생성
    chat_server = ChatServer(loop)

    # 서버 시작
    loop.run_until_complete(chat_server.start_server())

    # Tkinter GUI를 업데이트하는 함수
    def run_tk():
        chat_server.update()  # GUI를 업데이트
        loop.call_later(0.05, run_tk)  # 다음 업데이트를 예약

    # run_tk 함수를 호출하여 GUI를 실행
    run_tk()
    loop.run_forever()  # 이벤트 루프를 실행
