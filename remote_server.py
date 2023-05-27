import asyncio
import websockets
import pyautogui
import json
import base64
import io

# 클라이언트와의 연결을 관리하는 함수
async def handle_client(websocket, path):
    async for message in websocket:
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
        elif data["type"] in ["mouse_down", "mouse_up"]:
            x, y, button = data["data"]
            if data["type"] == "mouse_down":
                pyautogui.mouseDown(x, y, button=button)
            else:
                pyautogui.mouseUp(x, y, button=button)

        # 키보드 입력 요청 처리
        elif data["type"] == "write":
            text = data["text"]
            pyautogui.write(text)


        # 마우스 드래그
        elif data["type"] == "drag":
            x1, y1, x2, y2, button = data["data"]
            pyautogui.moveTo(x1, y1)
            pyautogui.dragTo(x2, y2, button=button)

        # 마우스 누르기
        elif data["type"] == "mouse_down":
            x, y, button = data["data"]
            pyautogui.mouseDown(x, y, button=button)

        # 마우스 떼기
        elif data["type"] == "mouse_up":
            x, y, button = data["data"]
            pyautogui.mouseUp(x, y, button=button)
        


# 웹소켓 서버 시작
start_server = websockets.serve(handle_client, "0.0.0.0", 8765)

# 이벤트 루프 실행
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()