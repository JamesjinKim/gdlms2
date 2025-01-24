from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import logging
import asyncio
import os
import socket
import json
import time
from stocker_alarm_codes import stocker_alarm_code
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime


# Ensure the log directory exists
log_dir = "./log"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "stocker.log")

# 로깅 설정
log_handler = TimedRotatingFileHandler(
    log_file, when="M", interval=1, backupCount=10
)
log_handler.suffix = "%Y%m%d%H%M"
log_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
log_handler.setLevel(logging.INFO)

# 로거 설정
logger = logging.getLogger("StockerLogger")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.addHandler(logging.StreamHandler())

class CustomDataBlock(ModbusSequentialDataBlock):
    def __init__(self):
        super().__init__(0, [0] * 1000)  # Initialize with 138 WORDs
        self.last_log_time = 0
        self.LOG_INTERVAL = 1  # 1초 간격으로 로깅
        self._buffer = []  # 데이터 버퍼 추가

    def setValues(self, address, values):
        # 변경된 데이터를 버퍼에 추가
        self._buffer.append((address, values))
        super().setValues(address, values)
        
        current_time = time.time()
        if current_time - self.last_log_time >= self.LOG_INTERVAL:
            self.last_log_time = current_time
            self.log_all_data()
            self._buffer.clear()  # 버퍼 초기화
    
    def log_all_data(self):
        """모든 데이터 로깅"""
        # PLC 데이터 영역 로깅
        all_values = self.getValues(0, 100)
        self.log_plc_data(all_values)
        
        # 비트 데이터 영역 로깅
        bit_values = self.getValues(100, 18)
        self.log_bit_data(bit_values)
    
    def log_plc_data(self, all_values):
        """PLC data logging (addresses 0-99)"""
        logger.info("\n=== Stocker PLC Data Area ===")

        # Basic Information (0-1)
        logger.info(f"Bunker ID: {all_values[0]}")
        logger.info(f"Stocker ID: {all_values[1]}")

        # Gas Stocker Types (2-6)
        logger.info(f"Gas Stocker 가스 종류: {all_values[2:7]}")

        # System Status (8)
        logger.info(f"Stocker Alarm Code: {all_values[8]}")

        # Position Values (10-11)
        logger.info(f"X축 현재값: {all_values[10]}")
        logger.info(f"Z축 현재값: {all_values[11]}")

        # Torque Settings (12-13)
        logger.info(f"Cap Unit 축 보호캡 분리 Torque 설정값: {all_values[12]}")
        logger.info(f"Cap Unit 축 보호캡 체결 Torque 설정값: {all_values[13]}")

        # [A] Port Barcode Data (30-59)
        barcode_a = ''.join([chr(x) if 32 <= x <= 126 else '?' for x in all_values[30:60]])
        logger.info(f"[A] Port Barcode Data: {barcode_a}")

        # [B] Port Barcode Data (60-89)
        barcode_b = ''.join([chr(x) if 32 <= x <= 126 else '?' for x in all_values[60:90]])
        logger.info(f"[B] Port Barcode Data: {barcode_b}")

        # [A] Port Gas Types (90-94)
        logger.info(f"[A] Port 가스 종류: {all_values[90:95]}")

        # [B] Port Gas Types (95-99)
        logger.info(f"[B] Port 가스 종류: {all_values[95:100]}")
        logger.info("==================")
        
    def log_bit_data(self, bit_values):
        """Bit data logging (addresses 100-117)"""
        logger.info("\n=== Stocker Bit Area Data ===")

        # Word 100 (Basic signals)
        word_100 = bit_values[0]
        logger.info("\n[100] Basic Signals:")
        basic_signals = [
            "EMG Signal", "Heart Bit", "Run/Stop Signal", "Server Connected Bit",
            "T-LAMP RED", "T-LAMP YELLOW", "T-LAMP GREEN", "Touch 수동동작中 Signal"
        ]
        for i, name in enumerate(basic_signals):
            logger.info(f"{name}: {bool(word_100 & (1 << i))}")

        # Word 105 (Door and cylinder status)
        word_105 = bit_values[5]
        logger.info("\n[105] Door and Cylinder Status:")
        door_cylinder_status = [
            "[A] Port 실린더 유무", "[B] Port 실린더 유무",
            "[A] Worker Door Open", "[A] Worker Door Close",
            "[A] Bunker Door Open", "[A] Bunker Door Close",
            "[B] Worker Door Open", "[B] Worker Door Close",
            "[B] Bunker Door Open", "[B] Bunker Door Close"
        ]
        for i, name in enumerate(door_cylinder_status):
            logger.info(f"{name}: {bool(word_105 & (1 << i))}")

        # Word 110 ([A] Port operation status)
        word_110 = bit_values[10]
        logger.info("\n[110] [A] Port Operation Status:")
        a_port_operation_status = [
            "[A] Port 보호캡 분리 완료", "[A] Port 보호캡 체결 완료",
            "[A] Worker Door Open 완료", "[A] Worker Door Close 완료",
            "[A] Worker 투입 Ready", "[A] Worker 투입 Complete",
            "[A] Worker 배출 Ready", "[A] Worker 배출 Comlete",
            "[A] Bunker Door Open 완료", "[A] Bunker Door Close 완료",
            "[A] Bunker 투입 Ready", "[A] Bunker 투입 Complete",
            "[A] Bunker 배출 Ready", "[A] Bunker 배출 Comlete",
            "[A] Cylinder Align 진행중", "[A] Cylinder Align 완료"
        ]
        for i, name in enumerate(a_port_operation_status):
            logger.info(f"{name}: {bool(word_110 & (1 << i))}")

        # Word 111 ([A] Port detailed status)
        word_111 = bit_values[11]
        logger.info("\n[111] [A] Port Detailed Status:")
        a_port_detailed_status = [
            "[A] Cap Open 진행중", "[A] Cap Close 진행중",
            "[A] Cylinder 위치로 X축 이동중", "[A] Cylinder 위치로 X축 이동완료",
            "[A] Cap 위치 찾는중", "[A] Cylinder Neck 위치 찾는중",
            "[A] Worker door Open 진행중", "[A] Worker door Close 진행중",
            "[A] Bunker door Open 진행중", "[A] Bunker door Close 진행중"
        ]
        for i, name in enumerate(a_port_detailed_status):
            logger.info(f"{name}: {bool(word_111 & (1 << i))}")

        # Word 115 ([B] Port operation status)
        word_115 = bit_values[15]
        logger.info("\n[115] [B] Port Operation Status:")
        b_port_operation_status = [
            "[B] Port 보호캡 분리 완료", "[B] Port 보호캡 체결 완료",
            "[B] Worker Door Open 완료", "[B] Worker Door Close 완료",
            "[B] Worker 투입 Ready", "[B] Worker 투입 Complete",
            "[B] Worker 배출 Ready", "[B] Worker 배출 Comlete",
            "[B] Bunker Door Open 완료", "[B] Bunker Door Close 완료",
            "[B] Bunker 투입 Ready", "[B] Bunker 투입 Complete",
            "[B] Bunker 배출 Ready", "[B] Bunker 배출 Comlete",
            "[B] Cylinder Align 진행중", "[B] Cylinder Align 완료"
        ]
        for i, name in enumerate(b_port_operation_status):
            logger.info(f"{name}: {bool(word_115 & (1 << i))}")

        # Word 116 ([B] Port detailed status)
        word_116 = bit_values[16]
        logger.info("\n[116] [B] Port Detailed Status:")
        b_port_detailed_status = [
            "[B] Cap Open 진행중", "[B] Cap Close 진행중",
            "[B] Cylinder 위치로 X축 이동중", "[B] Cylinder 위치로 X축 이동완료",
            "[B] Cap 위치 찾는중", "[B] Cylinder Neck 위치 찾는중",
            "[B] Worker door Open 진행중", "[B] Worker door Close 진행중",
            "[B] Bunker door Open 진행중", "[B] Bunker door Close 진행중"
        ]
        for i, name in enumerate(b_port_detailed_status):
            logger.info(f"{name}: {bool(word_116 & (1 << i))}")

class ModbusServer:
    def __init__(self):
        self.running = True
        self.datablock = CustomDataBlock()
        store = ModbusSlaveContext(
            di=self.datablock,  # discrete inputs
            co=self.datablock,  # coils
            hr=self.datablock,  # holding registers
            ir=self.datablock   # input registers
        )
        self.context = ModbusServerContext(slaves=store, single=True)

        # 소켓 통신 관련 초기화
        self.socket_path = '/tmp/modbus_data.sock'
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)
        self.data_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.data_socket.bind(self.socket_path)
        self.data_socket.listen(1)
        self.data_socket.setblocking(False)

    async def send_time_sync(self):
        """현재 시간을 클라이언트로 전송"""
        now = datetime.now()
        time_data = [
            now.year,   # Address 0: 년
            now.month,  # Address 1: 월
            now.day,    # Address 2: 일
            now.hour,   # Address 3: 시
            now.minute, # Address 4: 분
            now.second  # Address 5: 초
        ]
        
        async with self.data_lock:
            self.datablock.setValues(0, time_data)
            # 디버그 메시지는 클라이언트가 연결된 경우에만 출력
            if len(self.clients) > 0:
                print(f"시간 동기화 데이터 클라이언트로 전송: {time_data}")
    
    async def handle_socket_client(self, client, addr):
        """소켓 클라이언트 처리"""
        try:
            while True:
                # 데이터 요청을 받으면 현재 데이터 전송
                data = await self.get_current_data()
                await self.send_socket_data(client, data)
                await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Socket client error: {e}")
        finally:
            client.close()

    async def send_socket_data(self, client, data):
        """소켓을 통해 데이터 전송"""
        try:
            json_data = json.dumps(data)
            #client.send(json_data.encode('utf-8'))
            await asyncio.get_event_loop().sock_sendall(client, json_data.encode('utf-8'))
        except Exception as e:
            print(f"Socket send error: {e}")

    async def accept_socket_clients(self):
        """소켓 클라이언트 연결 수락"""
        while self.running:  # 실행 상태 확인
            try:
                client, addr = await asyncio.get_event_loop().sock_accept(self.data_socket)
                print(f"Socket client connected: {addr}")
                asyncio.create_task(self.handle_socket_client(client, addr))
            except Exception as e:
                if self.running:  # 정상 실행 중일 때만 에러 출력
                    print(f"Socket accept error: {e}")
                await asyncio.sleep(1)

    async def get_current_data(self):
        """현재 모든 데이터 조회"""
        async with self.data_lock:
            # PLC 데이터 영역 (0-99)
            plc_data = self.datablock.getValues(0, 140)
            # 비트 데이터 영역 (100-117)
            bit_data = self.datablock.getValues(100, 20)
            
            print("\n=== 서버 데이터 읽기 ===")
            print(f"PLC 데이터 첫 10개: {plc_data[:10]}")
            print(f"Bit 데이터 첫 5개: {bit_data[:5]}")

            return {
                "plc_data": {
                    "bunker_id": plc_data[0],
                    "stocker_id": plc_data[1], 
                    "gas_type": plc_data[2:7],
                    "system_status": {
                        "alarm_code": plc_data[8],
                        "alarm_message": self._get_alarm_message(plc_data[8])
                    },
                    "position": {
                        "x_axis": plc_data[10],
                        "z_axis": plc_data[11]
                    },
                    "torque": {
                        "cap_open": plc_data[12],
                        "cap_close": plc_data[13]
                    },
                    "port_a": {
                        "barcode": ''.join([chr(x) if 32 <= x <= 126 else '?' for x in plc_data[30:60]]),
                        "gas_type": plc_data[90:95]
                    },
                    "port_b": {
                        "barcode": ''.join([chr(x) if 32 <= x <= 126 else '?' for x in plc_data[60:90]]),
                        "gas_type": plc_data[95:100]
                    }
                },
                "bit_data": {
                    "word_100": {
                        "raw": bit_data[0],
                        "states": {
                            "emg_signal": bool(bit_data[0] & (1 << 0)),
                            "heart_bit": bool(bit_data[0] & (1 << 1)),
                            "run_stop_signal": bool(bit_data[0] & (1 << 2)),
                            "server_connected": bool(bit_data[0] & (1 << 3)),
                            "t_lamp_red": bool(bit_data[0] & (1 << 4)),
                            "t_lamp_yellow": bool(bit_data[0] & (1 << 5)), 
                            "t_lamp_green": bool(bit_data[0] & (1 << 6)),
                            "touch_manual": bool(bit_data[0] & (1 << 7))
                        }
                    },
                    "word_105": {
                        "raw": bit_data[5],
                        "states": {
                            "[A]_cylinder": bool(bit_data[5] & (1 << 0)),
                            "[B]_cylinder": bool(bit_data[5] & (1 << 1)),
                            "[A]_worker_door_open": bool(bit_data[5] & (1 << 2)),
                            "[A]_worker_door_close": bool(bit_data[5] & (1 << 3)),
                            "[A]_bunker_door_open": bool(bit_data[5] & (1 << 4)),
                            "[A]_bunker_door_close": bool(bit_data[5] & (1 << 5)),
                            "[B]_worker_door_open": bool(bit_data[5] & (1 << 6)),
                            "[B]_worker_door_close": bool(bit_data[5] & (1 << 7)),
                            "[B]_bunker_door_open": bool(bit_data[5] & (1 << 8)),
                            "[B]_bunker_door_close": bool(bit_data[5] & (1 << 9))
                        }
                    },
                    "word_110": {
                        "raw": bit_data[10],
                        "states": {
                            "[A]_cap_open_complete": bool(bit_data[10] & (1 << 0)),
                            "[A]_cap_close_complete": bool(bit_data[10] & (1 << 1)),
                            "[A]_worker_door_open_complete": bool(bit_data[10] & (1 << 2)),
                            "[A]_worker_door_close_complete": bool(bit_data[10] & (1 << 3)),
                            "[A]_worker_input_ready": bool(bit_data[10] & (1 << 4)),
                            "[A]_worker_input_complete": bool(bit_data[10] & (1 << 5)),
                            "[A]_worker_output_ready": bool(bit_data[10] & (1 << 6)),
                            "[A]_worker_output_complete": bool(bit_data[10] & (1 << 7)),
                            "[A]_bunker_door_open_complete": bool(bit_data[10] & (1 << 8)),
                            "[A]_bunker_door_close_complete": bool(bit_data[10] & (1 << 9)),
                            "[A]_bunker_input_ready": bool(bit_data[10] & (1 << 10)),
                            "[A]_bunker_input_complete": bool(bit_data[10] & (1 << 11)),
                            "[A]_bunker_output_ready": bool(bit_data[10] & (1 << 12)),
                            "[A]_bunker_output_complete": bool(bit_data[10] & (1 << 13)),
                            "[A]_cylinder_align_in_progress": bool(bit_data[10] & (1 << 14)),
                            "[A]_cylinder_align_complete": bool(bit_data[10] & (1 << 15))
                        }
                    },
                    "word_111": {
                        "raw": bit_data[11],
                        "states": {
                            "[A]_cap_opening": bool(bit_data[11] & (1 << 0)),
                            "[A]_cap_closing": bool(bit_data[11] & (1 << 1)),
                            "[A]_x_axis_moving": bool(bit_data[11] & (1 << 2)),
                            "[A]_x_axis_complete": bool(bit_data[11] & (1 << 3)),
                            "[A]_finding_cap": bool(bit_data[11] & (1 << 4)),
                            "[A]_finding_cylinder_neck": bool(bit_data[11] & (1 << 5)),
                            "[A]_worker_door_opening": bool(bit_data[11] & (1 << 6)),
                            "[A]_worker_door_closing": bool(bit_data[11] & (1 << 7)),
                            "[A]_bunker_door_opening": bool(bit_data[11] & (1 << 8)),
                            "[A]_bunker_door_closing": bool(bit_data[11] & (1 << 9))
                        }
                    },
                    "word_115": {
                        "raw": bit_data[15],
                        "states": {
                            "[B]_cap_open_complete": bool(bit_data[15] & (1 << 0)),
                            "[B]_cap_close_complete": bool(bit_data[15] & (1 << 1)),
                            "[B]_worker_door_open_complete": bool(bit_data[15] & (1 << 2)),
                            "[B]_worker_door_close_complete": bool(bit_data[15] & (1 << 3)),
                            "[B]_worker_input_ready": bool(bit_data[15] & (1 << 4)),
                            "[B]_worker_input_complete": bool(bit_data[15] & (1 << 5)),
                            "[B]_worker_output_ready": bool(bit_data[15] & (1 << 6)),
                            "[B]_worker_output_complete": bool(bit_data[15] & (1 << 7)),
                            "[B]_bunker_door_open_complete": bool(bit_data[15] & (1 << 8)),
                            "[B]_bunker_door_close_complete": bool(bit_data[15] & (1 << 9)),
                            "[B]_bunker_input_ready": bool(bit_data[15] & (1 << 10)),
                            "[B]_bunker_input_complete": bool(bit_data[15] & (1 << 11)),
                            "[B]_bunker_output_ready": bool(bit_data[15] & (1 << 12)),
                            "[B]_bunker_output_complete": bool(bit_data[15] & (1 << 13)),
                            "[B]_cylinder_align_in_progress": bool(bit_data[15] & (1 << 14)),
                            "[B]_cylinder_align_complete": bool(bit_data[15] & (1 << 15))
                        }
                    },
                    "word_116": {
                        "raw": bit_data[16],
                        "states": {
                            "[B]_cap_opening": bool(bit_data[16] & (1 << 0)),
                            "[B]_cap_closing": bool(bit_data[16] & (1 << 1)), 
                            "[B]_x_axis_moving": bool(bit_data[16] & (1 << 2)),
                            "[B]_x_axis_complete": bool(bit_data[16] & (1 << 3)),
                            "[B]_finding_cap": bool(bit_data[16] & (1 << 4)),
                            "[B]_finding_cylinder_neck": bool(bit_data[16] & (1 << 5)),
                            "[B]_worker_door_opening": bool(bit_data[16] & (1 << 6)),
                            "[B]_worker_door_closing": bool(bit_data[16] & (1 << 7)),
                            "[B]_bunker_door_opening": bool(bit_data[16] & (1 << 8)),
                            "[B]_bunker_door_closing": bool(bit_data[16] & (1 << 9))
                        }
                    }
                }
            }
        
    async def handle_client(self, client):
        self.clients.add(client)
        try:
            while True:
                await asyncio.sleep(0.1)  
                if client.is_closing():
                    break
        finally:
            self.clients.remove(client)

    async def update_values(self, address, values):
        async with self.data_lock:
            self.datablock.setValues(address, values)

    async def on_client_connect(self, client_socket):
        """클라이언트 연결 시 호출되는 콜백"""
        print(f"새로운 클라이언트 연결됨: {client_socket.getpeername()}")
        await self.send_time_sync()  # 시간 동기화 데이터 전송

    def __del__(self):
        """소멸자: 소켓 파일 정리"""
        if hasattr(self, 'data_socket'):
            self.data_socket.close()
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)

    async def run_server(self):
        """서버 실행"""
        server = None
        try:
            print("\n=== Modbus 서버 시작 중... ===")
            self.running = True # 서버 실행 상태 설정

            # Modbus 서버 시작 시 클라이언트 연결 핸들러 추가
            server = await StartAsyncTcpServer(
                context=self.context,
                address=("127.0.0.1", 5020),
            )
            print("\n=== Modbus 서버가 시작되었습니다! ===")
            print("클라이언트 연결 대기 중...")

            await server.serve_forever()

        except KeyboardInterrupt:
            print("\n=== 서버 종료 요청됨 ===")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.running = False  # 실행 상태 플래그 해제
            if server:
                await server.shutdown()
            self.data_socket.close()
            if os.path.exists(self.socket_path):
                os.unlink(self.socket_path)
            print("\n=== 서버가 종료되었습니다 ===")

async def main():
    server = ModbusServer()
    try:
       await server.run_server()
    except KeyboardInterrupt:
        logging.info("\n프로그램이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        logging.error(f"예기치 않은 오류 발생: {e}")

if __name__ == "__main__":
    asyncio.run(main())