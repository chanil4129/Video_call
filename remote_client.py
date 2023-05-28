import base64
import io
import json
import tkinter as tk
from PIL import Image, ImageTk
import websockets
import asyncio

'''
원격 제어 프로그램(클라이언트)

위의 코드는 웹소켓을 사용하여 원격에서 다른 컴퓨터의 화면을 제어할 수 있는 기능을 제공 
또한 마우스 클릭 및 키보드 입력 등의 이벤트를 서버에 전송하고, 서버의 스크린샷을 요청하여 클라이언트 화면에 표시
'''

ADDR = "ws://192.168.0.0:8765"

# 서버에게 스크린샷을 요청하는 함수
async def request_screenshot(websocket):
    # 스크린샷 요청 메시지를 서버에게 전송
    await websocket.send(json.dumps({"type": "request_screen"}))
    # 서버의 응답을 받음
    response = await websocket.recv()
    # 응답을 파이썬 객체로 변환
    data = json.loads(response)
    # 스크린샷 데이터가 있다면, 이를 이미지로 변환하여 반환
    if data["type"] == "screen":
        screenshot_base64 = data["data"]
        return Image.open(io.BytesIO(base64.b64decode(screenshot_base64)))

# 화면 갱신을 위한 함수
async def update_screen(websocket, canvas):
    while True:
        # 스크린샷 요청
        screenshot = await request_screenshot(websocket)
        # 스크린샷 이미지를 tkinter에서 사용할 수 있는 이미지로 변환
        tk_image = ImageTk.PhotoImage(screenshot)
        # 캔버스에 이미지 추가
        canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
        # 캔버스에 있는 이미지를 유지하기 위해 참조
        canvas.image = tk_image
        # 화면 갱신
        canvas.update()

# 메인 함수. 마우스 클릭 이벤트와 키보드 입력 이벤트를 처리
async def main(websocket, root, canvas):
    loop = asyncio.get_event_loop()

    start = None

    # 마우스 버튼을 누르면 호출되는 함수
    def on_mouse_down(event):
        nonlocal start
        start = (event.x, event.y)
        # 마우스 버튼을 누른 위치를 서버에 전송
        data = {"type": "mouse_down", "data": [start[0], start[1], "left"]}
        loop.call_soon_threadsafe(lambda: asyncio.create_task(websocket.send(json.dumps(data))))

    # 마우스 버튼을 놓으면 호출되는 함수
    def on_mouse_up(event):
        nonlocal start
        if start is not None:
            # 마우스 버튼을 놓은 위치를 서버에 전송
            data = {"type": "mouse_up", "data": [event.x, event.y, "left"]}
            loop.call_soon_threadsafe(lambda: asyncio.create_task(websocket.send(json.dumps(data))))
            start = None

    # 오른쪽 마우스 버튼을 누르면 호출되는 함수
    def on_right_mouse_down(event):
        data = {"type": "mouse_down", "data": [event.x, event.y, "right"]}
        loop.call_soon_threadsafe(lambda: asyncio.create_task(websocket.send(json.dumps(data))))

    # 오른쪽 마우스 버튼을 놓으면 호출되는 함수
    def on_right_mouse_up(event):
        data = {"type": "mouse_up", "data": [event.x, event.y, "right"]}
        loop.call_soon_threadsafe(lambda: asyncio.create_task(websocket.send(json.dumps(data))))

    # 키를 누르면 호출되는 함수
    def on_key_press(event):
        # 입력한 키 값을 서버에 전송
        data = {"type": "write", "text": event.char}
        loop.call_soon_threadsafe(lambda: asyncio.create_task(websocket.send(json.dumps(data))))

    # 마우스 클릭과 키보드 입력 이벤트를 각 함수와 연결
    canvas.bind("<Button-1>", on_mouse_down)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)
    canvas.bind("<Button-3>", on_right_mouse_down)
    canvas.bind("<ButtonRelease-3>", on_right_mouse_up)
    root.bind("<Key>", on_key_press)

    # 화면 갱신을 반복
    while True:
        await update_screen(websocket, canvas)

# 웹소켓 서버에 연결하고 메인 함수를 실행하는 함수
async def run_main(root, canvas):
    async with websockets.connect(ADDR) as websocket:
        await main(websocket, root, canvas)

# 루트 윈도우 생성
root = tk.Tk()
# 캔버스 생성
canvas = tk.Canvas(root, width=1440, height=900)
canvas.pack()

# 별도의 스레드에서 tkinter 이벤트 루프를 실행
import threading
threading.Thread(target=asyncio.run, args=(run_main(root, canvas),), daemon=True).start()

# tkinter 메인 루프 시작
root.mainloop()
