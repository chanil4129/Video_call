import asyncio
import websockets
import pyautogui
import json
import base64
import io

# 클라이언트로부터 받은 메시지를 처리하는 함수
async def remote_control(websocket, path):
    async for message in websocket:
        data = json.loads(message)

        # 마우스 이동
        if data["type"] == "move_to":
            pyautogui.moveTo(data["x"], data["y"])

        # 마우스 클릭
        elif data["type"] == "click":
            pyautogui.click(data["x"], data["y"], button=data["button"])

        # 키보드 입력
        elif data["type"] == "write":
            pyautogui.write(data["text"])

# 클라이언트와의 연결을 관리하는 함수
async def handle_client(websocket, path):
    while True:
        try:
            # 클라이언트로부터 메시지 받기
            message = await websocket.recv()
            data = json.loads(message)

            # 화면 스크린샷 요청 처리
            if data["type"] == "request_screen":
                screenshot = pyautogui.screenshot()
                buffered = io.BytesIO()
                screenshot.save(buffered, format="PNG")
                screenshot_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
                # 클라이언트에게 스크린샷 전송
                await websocket.send(json.dumps({"type": "screen", "data": screenshot_base64}))

            # 마우스 클릭 요청 처리
            elif data["type"] == "mouse_click":
                x, y, button = data["data"]
                pyautogui.click(x, y, button=button)

            # 키보드 입력 요청 처리
            elif data["type"] == "write":
                text = data["text"]
                pyautogui.write(text)

        except websockets.ConnectionClosed:
            break

# 웹소켓 서버 시작
start_server = websockets.serve(handle_client, "0.0.0.0", 8765)

# 이벤트 루프 실행
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
