from pymodbus.client import AsyncModbusTcpClient
import random
import asyncio
import logging
import signal
from typing import List, Dict

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger("StockerClient")

class ModbusFrameGenerator:
    def __init__(self):
        self.transaction_id = 0

    def create_modbus_frame(self, data: List[int]) -> Dict:
        """Modbus TCP 프레임 생성"""
        # 트랜잭션 ID 증가 (0x0000 ~ 0xFFFF)
        self.transaction_id = (self.transaction_id + 1) & 0xFFFF
        
        # 데이터 길이 계산
        data_length = 6 + len(data) * 2  # Function Code(1) + Start Address(2) + Length(2) + Byte Count(1) + Data
        
        frame = {
            'header': {
                'transaction_id': self.transaction_id.to_bytes(2, 'big'),
                'protocol_id': (0).to_bytes(2, 'big'),
                'length': data_length.to_bytes(2, 'big'),
                'unit_id': (0xFF).to_bytes(1, 'big')
            },
            'pdu': {
                'function_code': (0x10).to_bytes(1, 'big'),
                'start_address': (0).to_bytes(2, 'big'),
                'register_count': len(data).to_bytes(2, 'big'),
                'byte_count': (len(data) * 2).to_bytes(1, 'big'),
                'data': [value.to_bytes(2, 'big') for value in data]
            }
        }
        return frame

    def frame_to_bytes(self, frame: Dict) -> bytearray:
        """프레임을 바이트 시퀀스로 변환"""
        result = bytearray()
        
        # Header 조립
        result.extend(frame['header']['transaction_id'])
        result.extend(frame['header']['protocol_id'])
        result.extend(frame['header']['length'])
        result.extend(frame['header']['unit_id'])
        
        # PDU 조립
        result.extend(frame['pdu']['function_code'])
        result.extend(frame['pdu']['start_address'])
        result.extend(frame['pdu']['register_count'])
        result.extend(frame['pdu']['byte_count'])
        
        # 데이터 조립
        for data_bytes in frame['pdu']['data']:
            result.extend(data_bytes)
            
        return result

    def log_frame_details(self, frame: Dict):
        """프레임 상세 정보 로깅"""
        logger.info("\n=== Modbus Frame Structure ===")
        logger.info(f"Transaction ID: {frame['header']['transaction_id'].hex()}")
        logger.info(f"Protocol ID: {frame['header']['protocol_id'].hex()}")
        logger.info(f"Length: {frame['header']['length'].hex()}")
        logger.info(f"Unit ID: {frame['header']['unit_id'].hex()}")
        logger.info(f"Function Code: {frame['pdu']['function_code'].hex()}")
        logger.info(f"Start Address: {frame['pdu']['start_address'].hex()}")
        logger.info(f"Register Count: {frame['pdu']['register_count'].hex()}")
        logger.info(f"Byte Count: {frame['pdu']['byte_count'].hex()}")
        logger.info("Data: " + ' '.join(data.hex() for data in frame['pdu']['data'][:10]) + "...")

def generate_random_data():
    """랜덤 데이터 생성"""
    data = []
    
    # Bunker ID
    data.append(random.randint(1, 100))  # 0: Bunker ID
    
    # Stocker ID
    data.append(random.randint(1, 100))  # 1: Stocker ID
    
    # [A] Port Barcode Data (3~32)
    data.extend([random.randint(0, 65535) for _ in range(30)])
    
    # [B] Port Barcode Data (33~62)
    data.extend([random.randint(0, 65535) for _ in range(30)])
    
    # [A] Port 가스 종류 (63~67)
    data.extend([random.randint(1, 100) for _ in range(5)])
    
    # [B] Port 가스 종류 (68~72)
    data.extend([random.randint(1, 100) for _ in range(5)])
    
    # Stocker Alarm Code (74)
    data.append(random.randint(0, 500))  # 알람 코드 범위 가정
    
    # 위치 값들
    data.append(random.randint(0, 1000))  # 75: X축 현재값
    data.append(random.randint(0, 1000))  # 76: Z축 현재값
    
    # [A] Port 설정값들 (78~103)
    data.append(random.randint(0, 100))  # Cap Unit 축 보호캡 분리 Torque 설정값
    data.append(random.randint(0, 100))  # Cap Unit 축 보호캡 체결 Torque 설정값
    data.append(random.randint(0, 100))  # Cap Unit 축 보호캡 분리 Torque 현재값
    data.append(random.randint(0, 100))  # Cap Unit 축 보호캡 체결 Torque 현재값
    data.append(random.randint(0, 1000))  # X축 Cylinder Pos 설정값
    data.append(random.randint(0, 1000))  # Z축 Cap Open Down Pos 설정값
    data.append(random.randint(0, 1000))  # Z축 Cap Open Seperate Pos 설정값
    data.append(random.randint(0, 1000))  # Z축 Cap Open Up Pos 설정값
    data.append(random.randint(0, 1000))  # Z축 Cap Close Down Pos 설정값
    data.append(random.randint(0, 1000))  # Z축 Cap Close Screw Pos 설정값
    data.append(random.randint(0, 1000))  # Z축 Cap Close Up Pos 설정값
    data.append(random.randint(0, 1000))  # Cylinder Gripper축 Barrel Turn Pos 설정값
    data.append(random.randint(0, 1000))  # Cylinder Gripper축 Barrel Turn Pos 현재값
    data.append(random.randint(0, 100))   # Worker Door Torque 설정값
    data.append(random.randint(0, 100))   # Bunker Door Torque 설정값
    data.append(random.randint(0, 1000))  # Worker Door Open Pos 설정값
    data.append(random.randint(0, 1000))  # Bunker Door Open Pos 설정값
    data.append(random.randint(0, 1000))  # Worker Door Close Pos 설정값
    data.append(random.randint(0, 1000))  # Bunker Door Close Pos 설정값
    data.append(random.randint(0, 100))   # Worker Door Torque 현재값
    data.append(random.randint(0, 100))   # Bunker Door Torque 현재값
    data.append(random.randint(0, 1000))  # Worker Door Pos 현재값
    data.append(random.randint(0, 1000))  # Bunker Door Pos 현재값
    
    # [B] Port 설정값들 (110~137)
    data.append(random.randint(0, 100))   # Cap Unit 축 보호캡 분리 Torque 설정값
    data.append(random.randint(0, 100))   # Cap Unit 축 보호캡 체결 Torque 설정값
    data.append(random.randint(0, 100))   # Cap Unit 축 보호캡 분리 Torque 현재값
    data.append(random.randint(0, 100))   # Cap Unit 축 보호캡 체결 Torque 현재값
    data.append(random.randint(0, 1000))  # X축 Cylinder Pos 설정값
    data.append(random.randint(0, 1000))  # Z축 Cap Open Down Pos 설정값
    data.append(random.randint(0, 1000))  # Z축 Cap Open Seperate Pos 설정값
    data.append(random.randint(0, 1000))  # Z축 Cap Open Up Pos 설정값
    data.append(random.randint(0, 1000))  # Z축 Cap Close Down Pos 설정값
    data.append(random.randint(0, 1000))  # Z축 Cap Close Screw Pos 설정값
    data.append(random.randint(0, 1000))  # Z축 Cap Close Up Pos 설정값
    data.append(random.randint(0, 1000))  # Cylinder Gripper축 Barrel Turn Pos 설정값
    data.append(random.randint(0, 1000))  # Cylinder Gripper축 Barrel Turn Pos 현재값
    data.append(random.randint(0, 100))   # Worker Door Torque 설정값
    data.append(random.randint(0, 100))   # Bunker Door Torque 설정값
    data.append(random.randint(0, 1000))  # Worker Door Open Pos 설정값
    data.append(random.randint(0, 1000))  # Bunker Door Open Pos 설정값
    data.append(random.randint(0, 1000))  # Worker Door Close Pos 설정값
    data.append(random.randint(0, 1000))  # Bunker Door Close Pos 설정값
    data.append(random.randint(0, 100))   # Worker Door Torque 현재값
    data.append(random.randint(0, 100))   # Bunker Door Torque 현재값
    data.append(random.randint(0, 1000))  # Worker Door Pos 현재값
    data.append(random.randint(0, 1000))  # Bunker Door Pos 현재값
    
    return data
    
async def run_client():
    frame_generator = ModbusFrameGenerator()
    client = None
    loop = asyncio.get_running_loop()
    should_exit = asyncio.Event()

    async def connect_client():
        nonlocal client
        try:
            if client is None or not client.connected:
                logger.info("\n=== Modbus TCP 클라이언트 연결 시도 ===")
                client = AsyncModbusTcpClient(
                    '127.0.0.1', 
                    port=5020,
                    framer='socket',  # 'tcp' 대신 'socket' 사용
                    timeout=10,
                    retries=3
                )
                connected = await client.connect()
                if connected:
                    logger.info("서버 연결 성공!")
                else:
                    logger.error("서버 연결 실패!")
                return connected
            return client.connected
        except Exception as e:
            logger.error(f"연결 오류: {e}")
            return False
    
    async def send_data():
        if not await connect_client():
            logger.error("서버에 연결할 수 없습니다. 재시도 중...")
            return
            
        try:
            # 데이터 생성
            data = generate_random_data()
            logger.info("\n=== 생성된 Stocker 데이터 ===")
            logger.info(f"Bunker ID: {data[0]}")
            logger.info(f"Stocker ID: {data[1]}")
            
            # Modbus 프레임 생성 및 로깅
            frame = frame_generator.create_modbus_frame(data)
            frame_generator.log_frame_details(frame)
            
            # 데이터 전송
            if client and client.connected:
                try:
                    # 블록 단위로 데이터 전송 (한 번에 보내는 데이터 크기 제한)
                    BLOCK_SIZE = 50
                    for i in range(0, len(data), BLOCK_SIZE):
                        block = data[i:i + BLOCK_SIZE]
                        result = await client.write_registers(
                            address=i,
                            values=block,
                            slave=1
                        )
                        # 각 블록 전송 후 잠시 대기
                        await asyncio.sleep(0.1)

                    logger.info("데이터 전송 성공")
                    
                except Exception as e:
                    logger.error(f"레지스터 쓰기 오류: {e}")
                    await client.close()
                    await connect_client()
                    return
                    
        except Exception as e:
            logger.error(f"데이터 전송 중 오류 발생: {e}")
            if client and client.connected:
                await client.close()

    async def client_loop():
        try:
            while not should_exit.is_set():
                try:
                    await send_data()
                    # 전송 간격을 더 길게 설정
                    await asyncio.sleep(5)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"전송 중 오류: {e}")
                    await asyncio.sleep(1)  # 오류 발생시 1초 대기
        except asyncio.CancelledError:
            logger.info("클라이언트 루프가 취소되었습니다.")
        except Exception as e:
            logger.error(f"클라이언트 루프 오류: {e}")

    def signal_handler():
        logger.info("\n프로그램 종료 시작...")
        should_exit.set()
        for task in asyncio.all_tasks(loop):
            if task is not asyncio.current_task():
                task.cancel()

    try:
        loop.add_signal_handler(signal.SIGINT, signal_handler)
        logger.info("\n=== Modbus TCP 클라이언트 시작 ===")
        await client_loop()  # 여기서 client_loop를 호출
    except asyncio.CancelledError:
        logger.info("프로그램이 취소되었습니다.")
    except Exception as e:
        logger.error(f"예기치 않은 오류: {e}")
    finally:
        if client and hasattr(client, 'connected') and client.connected:
            await client.close()
            logger.info("클라이언트 연결 종료 완료")

if __name__ == "__main__":
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        logger.info("\n사용자가 프로그램을 중단했습니다.")
    except Exception as e:
        logger.error(f"\n예기치 않은 오류 발생: {e}")