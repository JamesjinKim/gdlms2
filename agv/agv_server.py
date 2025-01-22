import asyncio
import logging
import json
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

class AGVServer:
    def __init__(self, host='0.0.0.0', port=9999):
        self.host = host
        self.port = port
        self.clients = {}  # AGV 클라이언트 관리
        self.server = None

    async def handle_client(self, reader, writer):
        # 클라이언트 주소 가져오기
        addr = writer.get_extra_info('peername')
        client_id = f"{addr[0]}:{addr[1]}"
        logging.info(f"New connection from {client_id}")
        
        # 클라이언트 등록
        self.clients[client_id] = {"reader": reader, "writer": writer}
        
        try:
            while True:
                # 데이터 수신
                data = await reader.read(1024)
                if not data:
                    break
                
                # 데이터 처리
                try:
                    decoded_data = data.decode()
                    message = json.loads(decoded_data)
                    await self.process_message(client_id, message)
                except json.JSONDecodeError:
                    logging.error(f"Invalid JSON from {client_id}")
                except Exception as e:
                    logging.error(f"Error processing message from {client_id}: {e}")

        except Exception as e:
            logging.error(f"Connection error with {client_id}: {e}")
        finally:
            # 클라이언트 연결 종료 처리
            await self.client_disconnect(client_id)

    async def process_message(self, client_id, message):
        """메시지 처리"""
        logging.info(f"Received from {client_id}: {message}")
        
        # 응답 메시지 생성
        response = {
            "timestamp": datetime.now().isoformat(),
            "status": "ok",
            "message": "received"
        }
        
        # 응답 전송
        await self.send_message(client_id, response)

    async def send_message(self, client_id, message):
        """클라이언트에 메시지 전송"""
        if client_id in self.clients:
            writer = self.clients[client_id]["writer"]
            try:
                writer.write(json.dumps(message).encode())
                await writer.drain()
                logging.info(f"Sent to {client_id}: {message}")
            except Exception as e:
                logging.error(f"Error sending message to {client_id}: {e}")

    async def client_disconnect(self, client_id):
        """클라이언트 연결 종료 처리"""
        if client_id in self.clients:
            writer = self.clients[client_id]["writer"]
            try:
                writer.close()
                await writer.wait_closed()
            except:
                pass
            del self.clients[client_id]
            logging.info(f"Client {client_id} disconnected")

    async def start(self):
        """서버 시작"""
        self.server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        logging.info(f"Server started on {self.host}:{self.port}")
        
        async with self.server:
            await self.server.serve_forever()

    async def stop(self):
        """서버 종료"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logging.info("Server stopped")

async def main():
    server = AGVServer()
    try:
        await server.start()
    except KeyboardInterrupt:
        await server.stop()
    except Exception as e:
        logging.error(f"Server error: {e}")
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())