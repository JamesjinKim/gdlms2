from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio
import json
import os
from typing import List

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger("StockerWebServer")

# HTML 템플릿은 이전과 동일하게 유지
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Stocker Monitor</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                margin: 0;
                padding: 20px;
                font-family: Arial, sans-serif;
                background: #f5f5f5;
            }
            .container { 
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                border-bottom: 2px solid #eee;
                padding-bottom: 10px;
            }
            .status {
                margin: 20px 0;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 4px;
            }
            .data-display {
                background: #fff;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-top: 20px;
            }
            pre {
                white-space: pre-wrap;
                word-wrap: break-word;
                background: #f8f9fa;
                padding: 15px;
                border-radius: 4px;
                font-size: 14px;
            }
            .connected { color: #28a745; }
            .disconnected { color: #dc3545; }
            .error { color: #dc3545; }
            .alarm {
                background-color: #fff3cd;
                border: 1px solid #ffeeba;
                color: #856404;
                padding: 10px;
                margin-top: 10px;
                border-radius: 4px;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Stocker Monitoring System</h1>
            <div class="status">
                Connection Status: <span id="connection-status">Disconnected</span>
            </div>
            <div class="alarm" id="alarm-container">
                <strong>Alarm:</strong> <span id="alarm-message"></span>
            </div>
            <div class="data-display">
                <h3>Real-time Data:</h3>
                <pre id="data-container">Waiting for data...</pre>
            </div>
        </div>

        <script>
            let ws = new WebSocket("ws://localhost:5001/ws");
            const status = document.getElementById('connection-status');
            const dataContainer = document.getElementById('data-container');
            const alarmContainer = document.getElementById('alarm-container');
            const alarmMessage = document.getElementById('alarm-message');
            
            function formatData(data) {
                return JSON.stringify(data, null, 2);
            }
            
            ws.onopen = () => {
                status.textContent = 'Connected';
                status.className = 'connected';
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                dataContainer.textContent = formatData(data);
                
                if (data.status && data.status.alarm_code !== 0) {
                    alarmContainer.style.display = 'block';
                    alarmMessage.textContent = `Alarm Code ${data.status.alarm_code}`;
                } else {
                    alarmContainer.style.display = 'none';
                }
            };

            ws.onclose = () => {
                status.textContent = 'Disconnected';
                status.className = 'disconnected';
                setTimeout(reconnect, 5000);
            };

            ws.onerror = (error) => {
                status.textContent = 'Error';
                status.className = 'error';
                console.error('WebSocket error:', error);
            };
            
            function reconnect() {
                if (ws.readyState === WebSocket.CLOSED) {
                    status.textContent = 'Reconnecting...';
                    ws = new WebSocket("ws://localhost:5001/ws");
                }
            }
        </script>
    </body>
</html>
"""

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.socket_path = '/tmp/stocker_data.sock'
        self.unix_server = None

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, data: dict):
        for connection in self.active_connections[:]:
            try:
                await connection.send_json(data)
            except Exception as e:
                logger.error(f"Broadcast error: {e}")
                await self.disconnect(connection)

    async def handle_unix_connection(self, reader, writer):
        try:
            while True:
                data = await reader.read(4096)
                if not data:
                    break
                try:
                    json_data = json.loads(data.decode())
                    logger.info(f"Received data from Unix socket: {len(str(json_data))} bytes")
                    await self.broadcast(json_data)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON data received: {e}")
        finally:
            writer.close()
            await writer.wait_closed()

    async def setup_unix_socket(self):
        """유닉스 소켓 서버 설정"""
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        
        self.unix_server = await asyncio.start_unix_server(
            self.handle_unix_connection, 
            self.socket_path
        )
        return self.unix_server

    async def cleanup(self):
        """리소스 정리"""
        if self.unix_server:
            self.unix_server.close()
            await self.unix_server.wait_closed()
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 시작/종료 시 실행될 코드"""
    # 시작 시
    try:
        server = await manager.setup_unix_socket()
        asyncio.create_task(server.serve_forever())
        logger.info("Unix socket server started")
        yield
    finally:
        # 종료 시
        await manager.cleanup()
        logger.info("Unix socket server stopped and cleaned up")

app = FastAPI(lifespan=lifespan)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def get_root():
    """메인 페이지"""
    return HTMLResponse(html)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """웹소켓 연결 처리"""
    await manager.connect(websocket)
    try:
        while True:
            try:
                await websocket.receive_text()
                await asyncio.sleep(0.1)
            except WebSocketDisconnect:
                break
    finally:
        await manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    logger.info("=== Stocker Web Server Starting ===")
    
    uvicorn.run(
        app=app,
        host="0.0.0.0",
        port=5001,
        log_level="info"
    )