from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
import logging
import asyncio
import signal
from typing import Optional, Dict
import os
from logging.handlers import TimedRotatingFileHandler
import socket
import json
import time

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger("StockerServer")

# 로그 디렉토리 설정
log_dir = "./stocker_log"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "stocker_1.log")

# 로그 핸들러 설정
file_handler = TimedRotatingFileHandler(
    log_file,
    when="M",         # 1분 단위로 로테이션
    interval=1,       # 1분마다
    backupCount=1440, # 24시간치 보관 (60분 * 24시간)
    encoding='utf-8'
)
file_handler.suffix = "%Y%m%d_%H%M"  # 파일명 형식: stocker.log.202501211015
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# 콘솔 핸들러 설정
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

# 로거 설정
logger = logging.getLogger("StockerServer")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)
logger.addHandler(console_handler)

class ModbusFrameParser:
    @staticmethod
    def parse_frame(data: bytes) -> Optional[Dict]:
        """Modbus TCP 프레임 파싱"""
        try:
            frame = {
                'header': {
                    'transaction_id': int.from_bytes(data[0:2], 'big'),
                    'protocol_id': int.from_bytes(data[2:4], 'big'),
                    'length': int.from_bytes(data[4:6], 'big'),
                    'unit_id': data[6]
                },
                'pdu': {
                    'function_code': data[7],
                    'register_count': int.from_bytes(data[8:10], 'big'),
                    'data': data[10:]
                }
            }
            logger.debug(f"Parsed frame: {frame}")
            return frame
        except Exception as e:
            logger.error(f"Frame parsing error: {e}")
            return None

class CustomDataBlock(ModbusSequentialDataBlock):
    def __init__(self):
        super().__init__(0, [0] * 138)
        self.frame_parser = ModbusFrameParser()

    # CustomDataBlock 클래스에 추가할 메서드
    def get_structured_data(self, all_values):
        """구조화된 데이터 생성"""
        return {
            "basic": {
                "bunker_id": all_values[0],
                "stocker_id": all_values[1]
            },
            "port_a": {
                "barcode": all_values[3:33],
                "gas_type": all_values[63:68],
                "settings": {
                    "cap_torque": {
                        "remove_set": all_values[78],
                        "connect_set": all_values[79],
                        "remove_current": all_values[80],
                        "connect_current": all_values[81]
                    },
                    "positions": {
                        "cylinder_x": all_values[82],
                        "cap": {
                            "open_down": all_values[83],
                            "open_separate": all_values[84],
                            "open_up": all_values[85],
                            "close_down": all_values[87],
                            "close_screw": all_values[88],
                            "close_up": all_values[89]
                        },
                        "gripper": {
                            "barrel_turn_set": all_values[91],
                            "barrel_turn_current": all_values[92]
                        }
                    },
                    "door": {
                        "worker": {
                            "torque_set": all_values[94],
                            "torque_current": all_values[100],
                            "pos_open": all_values[96],
                            "pos_close": all_values[98],
                            "pos_current": all_values[102]
                        },
                        "bunker": {
                            "torque_set": all_values[95],
                            "torque_current": all_values[101],
                            "pos_open": all_values[97],
                            "pos_close": all_values[99],
                            "pos_current": all_values[103]
                        }
                    }
                }
            },
            "port_b": {
                "barcode": all_values[33:63],
                "gas_type": all_values[68:73],
                "settings": {
                    "cap_torque": {
                        "remove_set": all_values[110],
                        "connect_set": all_values[111],
                        "remove_current": all_values[112],
                        "connect_current": all_values[113]
                    },
                    "positions": {
                        "cylinder_x": all_values[115],
                        "cap": {
                            "open_down": all_values[117],
                            "open_separate": all_values[118],
                            "open_up": all_values[119],
                            "close_down": all_values[121],
                            "close_screw": all_values[122],
                            "close_up": all_values[123]
                        },
                        "gripper": {
                            "barrel_turn_set": all_values[125],
                            "barrel_turn_current": all_values[126]
                        }
                    },
                    "door": {
                        "worker": {
                            "torque_set": all_values[128],
                            "torque_current": all_values[134],
                            "pos_open": all_values[130],
                            "pos_close": all_values[132],
                            "pos_current": all_values[136]
                        },
                        "bunker": {
                            "torque_set": all_values[129],
                            "torque_current": all_values[135],
                            "pos_open": all_values[131],
                            "pos_close": all_values[133],
                            "pos_current": all_values[137]
                        }
                    }
                }
            },
            "status": {
                "alarm_code": all_values[74],
                "x_pos": all_values[75],
                "z_pos": all_values[76]
            }
        }

    def setValues(self, address, values):
        super().setValues(address, values)
        all_values = self.getValues(0, 138)  # 전체 레지스터 값 읽기
        print(all_values)
        logger.info("\n=== Received Data ===")
        
        # 기본 정보
        logger.info(f"Bunker ID: {all_values[0]}")
        logger.info(f"Stocker ID: {all_values[1]}")
        
        # Barcode 데이터
        logger.info("\n=== Barcode Data ===")
        logger.info(f"[A] Port Barcode Data: {all_values[3:33]}")
        logger.info(f"[B] Port Barcode Data: {all_values[33:63]}")
        
        # 가스 종류
        logger.info("\n=== Gas Type ===")
        logger.info(f"[A] Port 가스 종류: {all_values[63:68]}")
        logger.info(f"[B] Port 가스 종류: {all_values[68:73]}")
        
        # 알람 및 축 정보
        logger.info("\n=== System Status ===")
        logger.info(f"Stocker Alarm Code: {all_values[74]}")
        logger.info(f"X축 현재값: {all_values[75]}")
        logger.info(f"Z축 현재값: {all_values[76]}")
        
        # A Port 설정값들
        logger.info("\n=== A Port Settings ===")
        logger.info(f"Cap Unit 축 보호캡 분리 Torque 설정값: {all_values[78]}")
        logger.info(f"Cap Unit 축 보호캡 체결 Torque 설정값: {all_values[79]}")
        logger.info(f"Cap Unit 축 보호캡 분리 Torque 현재값: {all_values[80]}")
        logger.info(f"Cap Unit 축 보호캡 체결 Torque 현재값: {all_values[81]}")
        logger.info(f"X축 Cylinder Pos 설정값: {all_values[82]}")
        logger.info(f"Z축 Cap Open Down Pos 설정값: {all_values[83]}")
        logger.info(f"Z축 Cap Open Seperate Pos 설정값: {all_values[84]}")
        logger.info(f"Z축 Cap Open Up Pos 설정값: {all_values[85]}")
        logger.info(f"Z축 Cap Close Down Pos 설정값: {all_values[87]}")
        logger.info(f"Z축 Cap Close Screw Pos 설정값: {all_values[88]}")
        logger.info(f"Z축 Cap Close Up Pos 설정값: {all_values[89]}")
        logger.info(f"Cylinder Gripper축 Barrel Turn Pos 설정값: {all_values[91]}")
        logger.info(f"Cylinder Gripper축 Barrel Turn Pos 현재값: {all_values[92]}")
        logger.info(f"Worker Door Torque 설정값: {all_values[94]}")
        logger.info(f"Bunker Door Torque 설정값: {all_values[95]}")
        logger.info(f"Worker Door Open Pos 설정값: {all_values[96]}")
        logger.info(f"Bunker Door Open Pos 설정값: {all_values[97]}")
        logger.info(f"Worker Door Close Pos 설정값: {all_values[98]}")
        logger.info(f"Bunker Door Close Pos 설정값: {all_values[99]}")
        logger.info(f"Worker Door Torque 현재값: {all_values[100]}")
        logger.info(f"Bunker Door Torque 현재값: {all_values[101]}")
        logger.info(f"Worker Door Pos 현재값: {all_values[102]}")
        logger.info(f"Bunker Door Pos 현재값: {all_values[103]}")
        
        # B Port 설정값들
        logger.info("\n=== B Port Settings ===")
        logger.info(f"Cap Unit 축 보호캡 분리 Torque 설정값: {all_values[110]}")
        logger.info(f"Cap Unit 축 보호캡 체결 Torque 설정값: {all_values[111]}")
        logger.info(f"Cap Unit 축 보호캡 분리 Torque 현재값: {all_values[112]}")
        logger.info(f"Cap Unit 축 보호캡 체결 Torque 현재값: {all_values[113]}")
        logger.info(f"X축 Cylinder Pos 설정값: {all_values[115]}")
        logger.info(f"Z축 Cap Open Down Pos 설정값: {all_values[117]}")
        logger.info(f"Z축 Cap Open Seperate Pos 설정값: {all_values[118]}")
        logger.info(f"Z축 Cap Open Up Pos 설정값: {all_values[119]}")
        logger.info(f"Z축 Cap Close Down Pos 설정값: {all_values[121]}")
        logger.info(f"Z축 Cap Close Screw Pos 설정값: {all_values[122]}")
        logger.info(f"Z축 Cap Close Up Pos 설정값: {all_values[123]}")
        logger.info(f"Cylinder Gripper축 Barrel Turn Pos 설정값: {all_values[125]}")
        logger.info(f"Cylinder Gripper축 Barrel Turn Pos 현재값: {all_values[126]}")
        logger.info(f"Worker Door Torque 설정값: {all_values[128]}")
        logger.info(f"Bunker Door Torque 설정값: {all_values[129]}")
        logger.info(f"Worker Door Open Pos 설정값: {all_values[130]}")
        logger.info(f"Bunker Door Open Pos 설정값: {all_values[131]}")
        logger.info(f"Worker Door Close Pos 설정값: {all_values[132]}")
        logger.info(f"Bunker Door Close Pos 설정값: {all_values[133]}")
        logger.info(f"Worker Door Torque 현재값: {all_values[134]}")
        logger.info(f"Bunker Door Torque 현재값: {all_values[135]}")
        logger.info(f"Worker Door Pos 현재값: {all_values[136]}")
        logger.info(f"Bunker Door Pos 현재값: {all_values[137]}")
        
        logger.info("\n==================")

        # 구조화된 데이터 생성 및 소켓으로 전송
        structured_data = self.get_structured_data(all_values)
        retry_count = 0
        max_retries = 3  # 최대 재시도 횟수

        while retry_count < max_retries:
            try:
                if os.path.exists('/tmp/stocker_data.sock'):
                    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
                        sock.settimeout(1.0)  # 1초 타임아웃 설정
                        sock.connect('/tmp/stocker_data.sock')
                        sock.sendall(json.dumps(structured_data).encode())
                    break  # 성공하면 루프 종료
                else:
                    if retry_count == 0:  # 첫 번째 시도에서만 로그 출력
                        logger.info("Waiting for web server socket to be ready...")
                    time.sleep(1)  # asyncio.sleep 대신 time.sleep 사용
            except Exception as e:
                if retry_count == max_retries - 1:  # 마지막 시도에서만 에러 로그 출력
                    logger.error(f"Socket communication error after {max_retries} attempts: {e}")
                time.sleep(1)
            retry_count += 1

class ModbusServer:
    def __init__(self):
        self.running = True
        self.datablock = CustomDataBlock()
        store = ModbusSlaveContext(
            di=self.datablock,  # discrete inputs
            co=self.datablock,  # coils
            hr=self.datablock,  # holding registers
            ir=self.datablock,  # input registers
        )
        self.context = ModbusServerContext(slaves=store, single=True)
        
    async def run(self):
        server = None
        try:
            logger.info("\n=== Modbus Server Starting... ===")
            server = await StartAsyncTcpServer(
                context=self.context,
                address=('127.0.0.1', 5020),
                # allow_reuse_address와 timeout 제거
            )
            
            logger.info("Server started successfully")
            
            # 무한 루프로 서버 실행 유지
            while self.running:
                try:
                    await asyncio.sleep(0.1)
                except asyncio.CancelledError:
                    break
            
        except asyncio.CancelledError:
            logger.info("Server shutdown initiated")
            
        except Exception as e:
            logger.error(f"Server error: {e}")
                
        finally:
            self.running = False
            if server:
                await server.shutdown()
                logger.info("Server shutdown complete")

async def main():
    server = ModbusServer()
    
    def signal_handler():
        logger.info("Shutting down server...")
        server.running = False
        for task in asyncio.all_tasks():
            if task is not asyncio.current_task():
                task.cancel()

    try:
        loop = asyncio.get_running_loop()
        loop.add_signal_handler(signal.SIGINT, signal_handler)
        await server.run()
        
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Server shutdown complete")

if __name__ == "__main__":
    asyncio.run(main())