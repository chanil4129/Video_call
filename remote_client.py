import base64
import io
import json
import tkinter as tk
from PIL import Image, ImageTk
import websockets
import asyncio

ADDR="ws://192.1.1.1:8765" # 주소 및 포트

# 서버에게 명령을 보내는 함수
async def send_commands():
    async with websockets.connect(ADDR) as websocket:
        # 마우스 이동 명령 전송
        await websocket.send(json.dumps({"type": "move_to", "x": 100, "y": 100}))

        # 마우스 클릭 명령 전송
        await websocket.send(json.dumps({"type": "click", "x": 100, "y": 100, "button": "left"}))

        # 키보드 입력 명령 전송
        await websocket.send(json.dumps({"type": "write"}))

# 서버에게 스크린샷을 요청하는 함수
async def request_screenshot(websocket):
    await websocket.send(json.dumps({"type": "request_screen"}))
    response = await websocket.recv()
    data = json.loads(response)
    if data["type"] == "screen":
        screenshot_base64 = data["data"]
        return Image.open(io.BytesIO(base64.b64decode(screenshot_base64)))

# 화면 갱신을 위한 함수
async def update_screen(websocket, canvas):
    while True:
        screenshot = await request_screenshot(websocket)
        tk_image = ImageTk.PhotoImage(screenshot)
        canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
        canvas.image = tk_image
        canvas.update()

# 메인 함수. 마우스 클릭 이벤트와 키보드 입력 이벤트를 처리
async def main(websocket, root, canvas):
    loop = asyncio.get_event_loop()

    # 마우스 클릭 이벤트 처리 함수
    def on_mouse_click(event):
        data = {"type": "mouse_click", "data": [event.x, event.y, "left"]}
        loop.call_soon_threadsafe(lambda: asyncio.create_task(websocket.send(json.dumps(data))))

    # 키보드 입력 이벤트 처리 함수
    def on_key_press(event):
        data = {"type": "write", "text": event.char}
        loop.call_soon_threadsafe(lambda: asyncio.create_task(websocket.send(json.dumps(data))))

    canvas.bind("<Button-1>", on_mouse_click)  # 캔버스에 마우스 클릭 이벤트 바인딩
    root.bind("<Key>", on_key_press)  # 루트 윈도우에 키보드 이벤트 바인딩

    while True:
        await update_screen(websocket, canvas)  # 화면 갱신

# 웹소켓 서버에 연결하고 메인 함수 실행
async def run_main(root, canvas):
    async with websockets.connect(ADDR) as websocket:
        await main(websocket, root, canvas)

# 기본 이벤트 루프 정책 설정 (tkinter와 호환)
asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

root = tk.Tk()  # 루트 윈도우 생성
canvas = tk.Canvas(root, width=800, height=600)  # 캔버스 생성
canvas.pack()

# 별도의 스레드에서 tkinter 이벤트 루프 실행
import threading
threading.Thread(target=asyncio.run, args=(run_main(root, canvas),), daemon=True).start()

# tkinter 메인 루프 시작
root.mainloop()

# 서버에게 명령 보내기
asyncio.run(send_commands())