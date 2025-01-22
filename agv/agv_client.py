import asyncio
import serial_asyncio
import json
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S'
)

class AGVClient:
    def __init__(self, server_host='localhost', server_port=9999,
                 serial_port='/dev/ttyUSB0', serial_baudrate=9600):
        # TCP/IP 설정
        self.server_host = server_host
        self.server_port = server_port
        self.reader = None
        self.writer = None
        
        # 시리얼 통신 설정
        self.serial_port = serial_port
        self.serial_baudrate = serial_baudrate
        self.serial_reader = None
        self.serial_writer = None
        
        # 상태 플래그
        self.running = False

    async def connect_serial(self):
        """시리얼 포트 연결"""
        try:
            self.serial_reader, self.serial_writer = await serial_asyncio.open_serial_connection(
                url=self.serial_port,
                baudrate=self.serial_baudrate
            )
            logging.info(f"Serial connected on {self.serial_port}")
            return True
        except Exception as e:
            logging.error(f"Serial connection error: {e}")
            return False

    async def connect_server(self):
        """서버 연결"""
        try:
            self.reader, self.writer = await asyncio.open_connection(
                self.server_host,
                self.server_port
            )
            logging.info(f"Connected to server {self.server_host}:{self.server_port}")
            return True
        except Exception as e:
            logging.error(f"Server connection error: {e}")
            return False

    async def read_serial(self):
        """시리얼 포트에서 데이터 읽기"""
        while self.running:
            try:
                # 시리얼 데이터 읽기
                data = await self.serial_reader.readline()
                decoded_data = data.decode().strip()
                
                if decoded_data:
                    # 데이터 처리 및 서버로 전송
                    await self.process_serial_data(decoded_data)
                    
            except Exception as e:
                logging.error(f"Serial read error: {e}")
                await asyncio.sleep(1)

    async def read_server(self):
        """서버로부터 데이터 읽기"""
        while self.running:
            try:
                data = await self.reader.read(1024)
                if not data:
                    break
                
                decoded_data = data.decode()
                message = json.loads(decoded_data)
                await self.process_server_data(message)
                
            except Exception as e:
                logging.error(f"Server read error: {e}")
                break

    async def process_serial_data(self, data):
        """시리얼 데이터 처리 및 서버로 전송"""
        try:
            # 데이터를 서버 포맷으로 변환
            message = {
                "timestamp": datetime.now().isoformat(),
                "type": "agv_data",
                "data": data
            }
            
            # 서버로 전송
            self.writer.write(json.dumps(message).encode())
            await self.writer.drain()
            logging.info(f"Sent to server: {message}")
            
        except Exception as e:
            logging.error(f"Error processing serial data: {e}")

    async def process_server_data(self, message):
        """서버 데이터 처리 및 필요시 시리얼로 전송"""
        try:
            logging.info(f"Received from server: {message}")
            
            # 필요한 경우 시리얼로 데이터 전송
            if "command" in message:
                command = f"{message['command']}\n".encode()
                self.serial_writer.write(command)
                await self.serial_writer.drain()
                
        except Exception as e:
            logging.error(f"Error processing server data: {e}")

    async def run(self):
        """클라이언트 실행"""
        self.running = True
        
        # 시리얼 포트 연결
        if not await self.connect_serial():
            return
        
        # 서버 연결
        if not await self.connect_server():
            return
        
        try:
            # 시리얼 및 서버 데이터 읽기 태스크 생성
            tasks = [
                asyncio.create_task(self.read_serial()),
                asyncio.create_task(self.read_server())
            ]
            
            # 태스크 실행
            await asyncio.gather(*tasks)
            
        except Exception as e:
            logging.error(f"Runtime error: {e}")
        finally:
            await self.stop()

    async def stop(self):
        """클라이언트 종료"""
        self.running = False
        
        # 서버 연결 종료
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
        
        # 시리얼 포트 종료
        if self.serial_writer:
            self.serial_writer.close()

async def main():
    client = AGVClient()
    try:
        await client.run()
    except KeyboardInterrupt:
        await client.stop()
    except Exception as e:
        logging.error(f"Client error: {e}")
        await client.stop()

if __name__ == "__main__":
    asyncio.run(main())