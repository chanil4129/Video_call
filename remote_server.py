import asyncio
import websockets
import pyautogui
import json
import base64
import io

'''
원격 제어 프로그램(서버)

이 코드는 웹소켓을 사용하여 원격 제어 서버 생성
서버는 클라이언트로부터 다양한 타입의 요청을 받아 처리 
이를 통해 원격에서 마우스 클릭, 마우스 드래그, 키보드 입력 등의 작업을 수행 가능 
화면 스크린샷을 찍어 클라이언트에게 전송하는 기능 포함
'''

# 클라이언트와의 연결을 관리하는 함수
async def handle_client(websocket, path):
    # 클라이언트로부터 메시지를 비동기적으로 받기
    async for message in websocket:
        # JSON 형식의 메시지를 파이썬 객체로 변환
        data = json.loads(message)

        # 화면 스크린샷 요청을 처리
        if data["type"] == "request_screen":
            # 화면 스크린샷을 찍기
            screenshot = pyautogui.screenshot()
            buffered = io.BytesIO()
            screenshot.save(buffered, format="PNG")
            # 스크린샷을 Base64 형식으로 인코딩
            screenshot_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
            # 클라이언트에게 스크린샷을 전송
            await websocket.send(json.dumps({"type": "screen", "data": screenshot_base64}))

        # 마우스 클릭 요청을 처리
        elif data["type"] in ["mouse_down", "mouse_up"]:
            x, y, button = data["data"]
            if data["type"] == "mouse_down":
                # 마우스를 누르기
                pyautogui.mouseDown(x, y, button=button)
            else:
                # 마우스를 떼기
                pyautogui.mouseUp(x, y, button=button)

        # 키보드 입력 요청을 처리
        elif data["type"] == "write":
            text = data["text"]
            # 텍스트를 입력
            pyautogui.write(text)

        # 마우스 드래그 요청을 처리
        elif data["type"] == "drag":
            x1, y1, x2, y2, button = data["data"]
            pyautogui.moveTo(x1, y1)
            # 마우스를 드래그
            pyautogui.dragTo(x2, y2, button=button)

        # 마우스 누르기 요청을 처리
        elif data["type"] == "mouse_down":
            x, y, button = data["data"]
            # 마우스를 누르기
            pyautogui.mouseDown(x, y, button=button)

        # 마우스 떼기 요청을 처리
        elif data["type"] == "mouse_up":
            x, y, button = data["data"]
            # 마우스를 떼기
            pyautogui.mouseUp(x, y, button=button)


# 웹소켓 서버를 시작
start_server = websockets.serve(handle_client, "0.0.0.0", 8765)

# 이벤트 루프를 실행
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
