from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext
import logging
import asyncio
import os
import socket
import json
from gas_cabinet_alarm_code import gas_cabinet_alarm_code
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

# 로그 파일 경로 설정
log_dir = "./log"
log_file = os.path.join(log_dir, "gas_cabinet.log")

# 로그 디렉토리 생성
os.makedirs(log_dir, exist_ok=True)

# 로깅 설정
log_handler = TimedRotatingFileHandler(
    log_file, when="M", interval=1, backupCount=10
)
log_handler.suffix = "%Y%m%d%H%M"
log_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
log_handler.setLevel(logging.INFO)

# 로거 설정
logger = logging.getLogger("GasCabinetLogger")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.addHandler(logging.StreamHandler())

class CustomDataBlock(ModbusSequentialDataBlock):
    def setValues(self, address, values):
        print(f"\n데이터 수신: address={address}, values={values}")  # 추가
        super().setValues(address, values)
        
        # PLC 데이터 영역 (0-199)
        if address < 200:
            all_values = self.getValues(0, 140)
            # print(f"현재 저장된 PLC 데이터: {all_values[:10]}")  # 처음 10개 값만 출력 
            # logger.info(f"PLC ALL DATA: {all_values}") 
            self.log_plc_data(all_values)
            
        # 비트 데이터 영역 (200-226)
        elif address >= 200:
            bit_values = self.getValues(200, 27)
            self.log_bit_data(bit_values)
            
    def log_plc_data(self, all_values):
        """PLC 데이터 로깅"""
        logger.info("=== PLC Data Area ===")
        
        # 기본 정보
        logger.info(f"Bunker ID: {all_values[0]}")
        logger.info(f"Gas Cabinet ID: {all_values[1]}")
        logger.info(f"Gas Cabinet 기체 종류: {all_values[2:7]}")
        
        # 센서 데이터
        logger.info(f"\n=== 센서 데이터 ===")
        logger.info(f"PT1A: {all_values[17]}")
        logger.info(f"PT2A: {all_values[18]}")
        logger.info(f"PT1B: {all_values[19]}")
        logger.info(f"PT2B: {all_values[20]}")
        logger.info(f"PT3: {all_values[21]}")
        logger.info(f"PT4: {all_values[22]}")
        logger.info(f"WA (A Port Weight): {all_values[23]}")
        logger.info(f"WB (B Port Weight): {all_values[24]}")
        
        # 히터 상태
        logger.info(f"\n=== 히터 상태 ===")
        logger.info(f"[A] JACKET HEATER: {all_values[25]}")
        logger.info(f"[A] LINE HEATER: {all_values[26]}")
        logger.info(f"[B] JACKET HEATER: {all_values[27]}")
        logger.info(f"[B] LINE HEATER: {all_values[28]}")
        
        # 머신 코드 및 알람
        logger.info(f"\n=== 시스템 상태 ===")
        logger.info(f"SEND AND RECEIVE FOR MACHINE CODE: {all_values[29]}")
        logger.info(f"Gas Cabinet Alarm Code: {all_values[30]}")
        logger.info(f"Gas Cabinet Alarm Message: {gas_cabinet_alarm_code.get_description(all_values[30])}")
        
        # A 실린더 데이터
        logger.info(f"\n=== A 실린더 데이터 ===")
        logger.info(f"[A] CGA 체결 Torque 설정값: {all_values[40]}")
        logger.info(f"[A] CGA 분리 Torque 설정값: {all_values[41]}")
        logger.info(f"[A] CGA 체결 Torque 현재값: {all_values[42]}")
        logger.info(f"[A] CGA 분리 Torque 현재값: {all_values[43]}")
        logger.info(f"[A] 실린더 Down Pos 설정값: {all_values[45]}")
        logger.info(f"[A] 실린더 Up Pos 설정값: {all_values[46]}")
        logger.info(f"[A] 실린더 Up/Down Pos 현재값: {all_values[47]}")
        logger.info(f"[A] 실린더 Barcode Data: {all_values[50:80]}")
        
        # B 실린더 데이터
        logger.info(f"\n=== B 실린더 데이터 ===")
        logger.info(f"[B] CGB 체결 Torque 설정값: {all_values[100]}")
        logger.info(f"[B] CGB 분리 Torque 설정값: {all_values[101]}")
        logger.info(f"[B] CGB 체결 Torque 현재값: {all_values[102]}")
        logger.info(f"[B] CGB 분리 Torque 현재값: {all_values[103]}")
        logger.info(f"[B] 실린더 Down Pos 설정값: {all_values[105]}")
        logger.info(f"[B] 실린더 Up Pos 설정값: {all_values[106]}")
        logger.info(f"[B] 실린더 Up/Down Pos 현재값: {all_values[107]}")
        logger.info(f"[B] 실린더 Barcode Data: {all_values[110:140]}")

    def log_bit_data(self, bit_values):
        """비트 데이터 로깅"""
        logger.info("\n=== Bit Area Data ===")
        
        if len(bit_values) > 0:
            # 200번 워드 로깅
            word_200 = bit_values[0]
            logger.info("\n[200] 기본 상태 비트:")
            for i, name in enumerate([
                "EMG Signal", "Heart Bit", "Run/Stop Signal", "Server Connected Bit",
                "A Port 실린더 유무", "B Port 실린더 유무", "[A] Touch 수동동작中 Signal",
                "[B] Touch 수동동작中 Signal", "Door Open 완료", "Door Close 완료"
            ]):
                logger.info(f"{name}: {bool(word_200 & (1<<i))}")

            # 201번 워드 (센서 및 릴레이 상태)
            word_201 = bit_values[1]
            logger.info("\n[201] 센서 및 릴레이 상태:")
            for i, name in enumerate([
                "T-LAMP RED", "T-LAMP YELLOW", "T-LAMP GREEN",
                "JACKET HEATER A RELAY", "LINE HEATER A RELAY",
                "JACKET HEATER B RELAY", "LINE HEATER B RELAY",
                "GAS LEAK SHUT DOWN", "VMB STOP SIGNAL",
                "UV/IR SENSOR", "HIGH TEMP SENSOR", "SMOKE SENSOR"
            ]):
                logger.info(f"{name}: {bool(word_201 & (1<<i))}")

            # 210번 워드 ([A] Port 진행 상태)
            word_210 = bit_values[10]
            logger.info("\n[210] [A] Port 진행 상태:")
            for i, name in enumerate([
                "Close the Cylinder", "1st Purge before Exchange Cylinder",
                "Decompression Test", "2nd Purge before Exchange Cylinder",
                "Exchange Cylinder", "1st Purge after Exchange Cylinder",
                "Pressure Test", "2nd Purge after Exchange Cylinder",
                "Purge Completed", "Prepare to Supply",
                "Gas Supply AV3 Open/Close Choose", "Gas Supply",
                "Ready to Supply"
            ]):
                logger.info(f"{name}: {bool(word_210 & (1<<i))}")

            # 211번 워드 (AV1A-AV5A 밸브 상태)
            word_211 = bit_values[11]
            logger.info("\n[211] A Port 밸브 상태:")
            for i in range(5):
                logger.info(f"AV{i+1}A: {bool(word_211 & (1<<i))}")

            # 215번 워드 ([A] Port 상세 상태)
            word_215 = bit_values[15]
            logger.info("\n[215] [A] Port 상세 상태:")
            state_names = [
                "Cylinder Ready", "CGA 분리완료", "CGA 체결완료", "실린더 밸브 Open 완료",
                "실린더 밸브 Close 완료", "실린더 밸브 Open 상태", "실린더 리프트 준비 완료",
                "리프트 상승 진행중", "리프트 하강 진행중", "CGA 분리 진행중", "CGA 체결 진행중",
                "실린더 Cap 분리중", "실린더 밸브 Open 중", "실린더 밸브 Close 중",
                "실린더 얼라이먼트 중", "리프트 회전 중"
            ]
            for i, name in enumerate(state_names):
                logger.info(f"{name}: {bool(word_215 & (1<<i))}")
            
            # 216번 워드 ([A] Port 추가 상태)
            word_216 = bit_values[16]
            logger.info("\n[216] [A] Port 추가 상태:")
            for i, name in enumerate([
                "리프트 회전 완료", "실린더 클램프 닫힘 완료", "CGA 체결완료 상태",
                "Port 투입 Request", "Port 투입 Complete", "Port 배출 Request",
                "Port 배출 Comlete"
            ]):
                logger.info(f"[A] {name}: {bool(word_216 & (1<<i))}")

            # 220번 워드 ([B] Port 진행 상태)
            word_220 = bit_values[20]
            logger.info("\n[220] [B] Port 진행 상태:")
            for i, name in enumerate([
                "Close the Cylinder", "1st Purge before Exchange Cylinder",
                "Decompression Test", "2nd Purge before Exchange Cylinder",
                "Exchange Cylinder", "1st Purge after Exchange Cylinder",
                "Pressure Test", "2nd Purge after Exchange Cylinder",
                "Purge Completed", "Prepare to Supply",
                "Gas Supply AV3 Open/Close Choose", "Gas Supply",
                "Ready to Supply"
            ]):
                logger.info(f"[B] {name}: {bool(word_220 & (1<<i))}")

            # 221번 워드 (B Port 밸브 상태)
            word_221 = bit_values[21]
            logger.info("\n[221] B Port 밸브 상태:")
            # AV1B-AV5B (0-4)
            for i in range(5):
                logger.info(f"AV{i+1}B: {bool(word_221 & (1<<i))}")
            # AV7-AV9 (13-15)
            for i, num in enumerate(range(13, 16)):
                logger.info(f"AV{7+i}: {bool(word_221 & (1<<num))}")

            # 225번 워드 ([B] Port 상세 상태)
            word_225 = bit_values[25]
            logger.info("\n[225] [B] Port 상세 상태:")
            for i, name in enumerate([
                "Cylinder Ready", "CGA 분리완료", "CGA 체결완료",
                "실린더 밸브 Open 완료", "실린더 밸브 Close 완료", "실린더 밸브 Open 상태",
                "실린더 리프트 준비 완료", "리프트 상승 진행중", "리프트 하강 진행중",
                "CGA 분리 진행중", "CGA 체결 진행중", "실린더 Cap 분리중",
                "실린더 밸브 Open 중", "실린더 밸브 Close 중", "실린더 얼라이먼트 중",
                "리프트 회전 중"
            ]):
                logger.info(f"[B] {name}: {bool(word_225 & (1<<i))}")

            # 226번 워드 ([B] Port 추가 상태)
            word_226 = bit_values[26]
            logger.info("\n[226] [B] Port 추가 상태:")
            for i, name in enumerate([
                "리프트 회전 완료", "실린더 클램프 닫힘 완료", "CGA 체결완료 상태",
                "Port 투입 Request", "Port 투입 Complete", "Port 배출 Request",
                "Port 배출 Comlete"
            ]):
                logger.info(f"[B] {name}: {bool(word_226 & (1<<i))}")

class ModbusServer:
    def __init__(self):
        self.clients = set()
        self.data_lock = asyncio.Lock()
        self.running = True  # 서버 실행 상태 플래그 추가

        
        # 데이터 블록 초기화 시 시간 동기화 영역 추가 (0-5 주소)
        self.datablock = CustomDataBlock(0, [0] * 300)  # 더 큰 범위로 수정
        store = ModbusSlaveContext(
            hr=self.datablock,
            ir=self.datablock
        )
        self.context = ModbusServerContext(slaves={1: store}, single=False)

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
                print(f"시간 동기화 데이터 전송: {time_data}")
    
    async def update_time_periodically(self):
        """주기적으로 시간 업데이트"""
        while self.running:  # 실행 상태 확인
            await self.send_time_sync()
            await asyncio.sleep(1)

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

    async def stop_gas_supply(self, cabinet_id):  # 수정
        try:
            async with self.data_lock:
                # 예: 특정 주소에 가스 공급 중지 명령 쓰기
                self.datablock.setValues(211, [0])  # A Port 밸브 닫기
                self.datablock.setValues(221, [0])  # B Port 밸브 닫기
            return True
        except Exception as e:
            logging.error(f"가스 공급 중지 중 오류: {str(e)}")
            return False

    async def emergency_stop_all(self):
        """모든 캐비닛 긴급 정지"""
        try:
            async with self.data_lock:
                # EMG Signal 설정 (200번 워드의 0번 비트)
                self.datablock.setValues(200, [1])  # EMG 비트 설정
                # 모든 밸브 닫기
                self.datablock.setValues(211, [0])  # A Port
                self.datablock.setValues(221, [0])  # B Port
            return True
        except Exception as e:
            logging.error(f"긴급 정지 중 오류: {str(e)}")
            return False
    async def get_current_data(self):
        """현재 모든 데이터 조회"""
        async with self.data_lock:
            # PLC 데이터 영역
            plc_data = self.datablock.getValues(0, 140)
            # 비트 데이터 영역
            bit_data = self.datablock.getValues(200, 27)
            
            print("\n=== 서버 데이터 읽기 ===")
            print(f"PLC 데이터 첫 10개: {plc_data[:10]}")
            print(f"Bit 데이터 첫 5개: {bit_data[:5]}")

            return {
                "plc_data": {
                    "bunker_id": plc_data[0],
                    "cabinet_id": plc_data[1],
                    "gas_type": plc_data[2:7],
                    "sensors": {
                        "pt1a": plc_data[17],
                        "pt2a": plc_data[18],
                        "pt1b": plc_data[19],
                        "pt2b": plc_data[20],
                        "pt3": plc_data[21],
                        "pt4": plc_data[22],
                        "weight_a": plc_data[23],
                        "weight_b": plc_data[24]
                    },
                    "heaters": {
                        "jacket_heater_a": plc_data[25],
                        "line_heater_a": plc_data[26],
                        "jacket_heater_b": plc_data[27],
                        "line_heater_b": plc_data[28]
                    },
                    "status": {
                        "machine_code": plc_data[29],
                        "alarm_code": plc_data[30]
                    },
                    "port_a": {
                        "cga_torque": {
                            "connect_set": plc_data[40],
                            "disconnect_set": plc_data[41],
                            "connect_current": plc_data[42],
                            "disconnect_current": plc_data[43]
                        },
                        "cylinder_position": {
                            "down_pos_set": plc_data[45],
                            "up_pos_set": plc_data[46],
                            "current_pos": plc_data[47]
                        },
                        "barcode": plc_data[50:80]
                    },
                    "port_b": {
                        "cga_torque": {
                            "connect_set": plc_data[100],
                            "disconnect_set": plc_data[101],
                            "connect_current": plc_data[102],
                            "disconnect_current": plc_data[103]
                        },
                        "cylinder_position": {
                            "down_pos_set": plc_data[105],
                            "up_pos_set": plc_data[106],
                            "current_pos": plc_data[107]
                        },
                        "barcode": plc_data[110:140]
                    }
                },
                "bit_data": {
                    "word_200": {
                        "raw": bit_data[0],
                        "states": {
                            "emg_signal": bool(bit_data[0] & (1 << 0)),
                            "heart_bit": bool(bit_data[0] & (1 << 1)),
                            "run_stop_signal": bool(bit_data[0] & (1 << 2)),
                            "server_connected": bool(bit_data[0] & (1 << 3)),
                            "port_a_cylinder": bool(bit_data[0] & (1 << 4)),
                            "port_b_cylinder": bool(bit_data[0] & (1 << 5)),
                            "port_a_manual": bool(bit_data[0] & (1 << 6)),
                            "port_b_manual": bool(bit_data[0] & (1 << 7)),
                            "door_open": bool(bit_data[0] & (1 << 8)),
                            "door_close": bool(bit_data[0] & (1 << 9))
                        }
                    },
                    "word_201": {
                        "raw": bit_data[1],
                        "states": {
                            "lamp_red": bool(bit_data[1] & (1 << 0)),
                            "lamp_yellow": bool(bit_data[1] & (1 << 1)),
                            "lamp_green": bool(bit_data[1] & (1 << 2)),
                            "jacket_heater_a": bool(bit_data[1] & (1 << 3)),
                            "line_heater_a": bool(bit_data[1] & (1 << 4)),
                            "jacket_heater_b": bool(bit_data[1] & (1 << 5)),
                            "line_heater_b": bool(bit_data[1] & (1 << 6)),
                            "gas_leak_shutdown": bool(bit_data[1] & (1 << 7)),
                            "vmb_stop": bool(bit_data[1] & (1 << 8)),
                            "uv_ir_sensor": bool(bit_data[1] & (1 << 9)),
                            "high_temp_sensor": bool(bit_data[1] & (1 << 10)),
                            "smoke_sensor": bool(bit_data[1] & (1 << 11))
                        }
                    },
                    "port_a_status": {
                        "progress": bit_data[10],  # word_210
                        "valves": bit_data[11],    # word_211
                        "details": bit_data[15],   # word_215
                        "additional": bit_data[16]  # word_216
                    },
                    "port_b_status": {
                        "progress": bit_data[20],  # word_220
                        "valves": bit_data[21],    # word_221
                        "details": bit_data[25],   # word_225
                        "additional": bit_data[26]  # word_226
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
        await self.broadcast_update(address, values)

    async def broadcast_update(self, address, value):
        for client in self.clients:
            try:
                pass  # 실제 브로드캐스트 로직 구현 필요
                #await self.send_socket_data(client, data)
            except Exception as e:
                logging.error(f"브로드캐스트 오류: {e}")

    async def run_server(self):
        """서버 실행"""
        server = None
        try:
            print("\n=== Modbus 서버 시작 중... ===")
            self.running = True  # 서버 실행 상태 설정

            # Modbus 서버 시작 시 클라이언트 연결 핸들러 추가
            server = await StartAsyncTcpServer(
                context=self.context,
                address=("127.0.0.1", 5020),
            )
            
            print("\n=== Modbus 서버가 시작되었습니다! ===")
            print("클라이언트 연결 대기 중...")

            # 시간 업데이트 태스크 시작
            time_update_task = asyncio.create_task(self.update_time_periodically())
            socket_task = asyncio.create_task(self.accept_socket_clients())
            
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