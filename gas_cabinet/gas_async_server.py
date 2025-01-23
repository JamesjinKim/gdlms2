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
        print(f"\n데이터 수신: address={address}, values={values}")
        super().setValues(address, values)
        
        # PLC 데이터 영역 (0-99)
        if 0 <= address < 100:
            all_values = self.getValues(0, 100)  # 전체 PLC 데이터 영역 읽기
            self.log_plc_data(all_values)
            
        # 비트 데이터 영역 (100-117)
        elif 100 <= address <= 117:
            bit_values = self.getValues(100, 18)  # 비트 데이터 영역 읽기
            self.log_bit_data(bit_values)
            
    def log_plc_data(self, all_values):
        """PLC 데이터 로깅 (0-99 주소)"""
        logger.info("=== PLC Data Area ===")
        
        # 기본 정보 (0-6)
        logger.info(f"Bunker ID: {all_values[0]}")
        logger.info(f"Gas Cabinet ID: {all_values[1]}")
        logger.info(f"Gas Cabinet 가스 종류: {all_values[2:7]}")
        
        # 시스템 상태 (7-8)
        logger.info(f"\n=== 시스템 상태 ===")
        logger.info(f"SEND AND RECEIVE FOR MACHINE CODE: {all_values[7]}")
        logger.info(f"Gas Cabinet Alarm Code: {all_values[8]}")
        logger.info(f"Gas Cabinet Alarm Message: {gas_cabinet_alarm_code.get_description(all_values[8])}")
        
        # 센서 데이터 (10-17)
        logger.info(f"\n=== 센서 데이터 ===")
        logger.info(f"PT1A: {all_values[10]} PSI")
        logger.info(f"PT2A: {all_values[11]} PSI")
        logger.info(f"PT1B: {all_values[12]} PSI")
        logger.info(f"PT2B: {all_values[13]} PSI")
        logger.info(f"PT3: {all_values[14]} PSI")
        logger.info(f"PT4: {all_values[15]} PSI")
        logger.info(f"WA (A Port Weight): {all_values[16]} kg")
        logger.info(f"WB (B Port Weight): {all_values[17]} kg")
        
        # 히터 상태 (18-21)
        logger.info(f"\n=== 히터 상태 ===")
        logger.info(f"[A] JACKET HEATER: {all_values[18]}°C")
        logger.info(f"[A] LINE HEATER: {all_values[19]}°C")
        logger.info(f"[B] JACKET HEATER: {all_values[20]}°C")
        logger.info(f"[B] LINE HEATER: {all_values[21]}°C")
        
        # A Port 데이터 (24-29, 30-59, 90-94)
        logger.info(f"\n=== A Port 데이터 ===")
        logger.info(f"[A] CGA 체결 Torque 설정값: {all_values[24]} kgf·cm")
        logger.info(f"[A] CAP 체결 Torque 설정값: {all_values[25]} kgf·cm")
        logger.info(f"[A] 실린더 Up/Down Pos 현재값: {all_values[26]} mm")
        
        # A Port Barcode 데이터
        barcode_a = ''.join([chr(x) if 32 <= x <= 126 else '?' for x in all_values[30:60]])
        logger.info(f"[A] 실린더 Barcode Data: {barcode_a}")
        logger.info(f"[A] Port 가스 종류: {all_values[90:95]}")
        
        # B Port 데이터 (27-29, 60-89, 95-99)
        logger.info(f"\n=== B Port 데이터 ===")
        logger.info(f"[B] CGA 체결 Torque 설정값: {all_values[27]} kgf·cm")
        logger.info(f"[B] CAP 체결 Torque 설정값: {all_values[28]} kgf·cm")
        logger.info(f"[B] 실린더 Up/Down Pos 현재값: {all_values[29]} mm")
        
        # B Port Barcode 데이터
        barcode_b = ''.join([chr(x) if 32 <= x <= 126 else '?' for x in all_values[60:90]])
        logger.info(f"[B] 실린더 Barcode Data: {barcode_b}")
        logger.info(f"[B] Port 가스 종류: {all_values[95:100]}")

    def log_bit_data(self, bit_values):
        """비트 데이터 로깅 (100-117 주소)"""
        logger.info("\n=== Bit Area Data ===")
        
        # 기본 신호 (100)
        word_100 = bit_values[0]
        logger.info("\n[100] 기본 신호:")
        basic_signals = [
            "EMG Signal", "Heart Bit", "Run/Stop Signal", "Server Connected Bit",
            "T-LAMP RED", "T-LAMP YELLOW", "T-LAMP GREEN", "Touch 수동동작中 Signal"
        ]
        for i, name in enumerate(basic_signals):
            logger.info(f"{name}: {bool(word_100 & (1<<i))}")

        # 밸브 상태 (101)
        word_101 = bit_values[1]
        logger.info("\n[101] 밸브 상태:")
        valves = ["AV1A", "AV2A", "AV3A", "AV4A", "AV5A", 
                 "AV1B", "AV2B", "AV3B", "AV4B", "AV5B",
                 "AV7", "AV8", "AV9"]
        for i, name in enumerate(valves):
            logger.info(f"{name}: {bool(word_101 & (1<<i))}")

        # 센서 및 릴레이 상태 (102)
        word_102 = bit_values[2]
        logger.info("\n[102] 센서 및 릴레이 상태:")
        sensors = [
            "JACKET HEATER A RELAY", "LINE HEATER A RELAY",
            "JACKET HEATER B RELAY", "LINE HEATER B RELAY",
            "GAS LEAK SHUT DOWN", "VMB STOP SIGNAL",
            "UV/IR SENSOR", "HIGH TEMP SENSOR", "SMOKE SENSOR"
        ]
        for i, name in enumerate(sensors):
            logger.info(f"{name}: {bool(word_102 & (1<<i))}")

        # Port 요청 상태 (103)
        word_103 = bit_values[3]
        logger.info("\n[103] Port 요청 상태:")
        port_requests = [
            "[A] Port Insert Request", "[A] Port Insert Complete",
            "[A] Port Remove Request", "[A] Port Remove Complete",
            "[B] Port Insert Request", "[B] Port Insert Complete",
            "[B] Port Remove Request", "[B] Port Remove Complete"
        ]
        for i, name in enumerate(port_requests):
            if i < 4 or (8 <= i < 12):  # A Port (0-3) and B Port (8-11)
                logger.info(f"{name}: {bool(word_103 & (1<<i))}")

        # 실린더 및 도어 상태 (105)
        word_105 = bit_values[5]
        logger.info("\n[105] 실린더 및 도어 상태:")
        status = [
            "[A] Port 실린더 유무", "[B] Port 실린더 유무",
            "Door Open 완료", "Door Close 완료"
        ]
        for i, name in enumerate(status):
            logger.info(f"{name}: {bool(word_105 & (1<<i))}")

        # A Port 작업 상태 (110)
        word_110 = bit_values[10]
        logger.info("\n[110] A Port 작업 상태:")
        port_a_ops = [
            "Close the Cylinder", "1st Purge before Exchange",
            "Decompression Test", "2nd Purge before Exchange",
            "Exchange Cylinder", "1st Purge after Exchange",
            "Pressure Test", "2nd Purge after Exchange",
            "Purge Completed", "Prepare to Supply",
            "Gas Supply AV3 Open/Close Choose", "Gas Supply",
            "Ready to Supply"
        ]
        for i, name in enumerate(port_a_ops):
            logger.info(f"[A] {name}: {bool(word_110 & (1<<i))}")

        # B Port 작업 상태 (115)
        word_115 = bit_values[15]
        logger.info("\n[115] B Port 작업 상태:")
        for i, name in enumerate(port_a_ops):  # 같은 상태 이름 사용
            logger.info(f"[B] {name}: {bool(word_115 & (1<<i))}")

        # B Port 상세 상태 (116)
        word_116 = bit_values[16]
        logger.info("\n[116] B Port 상세 상태:")
        b_port_details = [
            "Cylinder Ready",
            "CGA Disconnect Complete",
            "CGA Connect Complete",
            "Cylinder Valve Open Complete",
            "Cylinder Valve Close Complete",
            "Cylinder Valve Open Status",
            "Cylinder Lift Unit Ready",
            "Cylinder Lift Unit Moving Up",
            "Cylinder Lift Unit Moving Down",
            "CGA Separation In Progress",
            "CGA Connection In Progress",
            "Cylinder Cap Separation In Progress",
            "Cylinder Valve Open In Progress",
            "Cylinder Valve Close In Progress",
            "Cylinder Alignment In Progress",
            "Cylinder Turn In Progress"
        ]
        for i, name in enumerate(b_port_details):
            logger.info(f"[B] {name}: {bool(word_116 & (1<<i))}")

        # B Port 추가 상태 (117)
        word_117 = bit_values[17]
        logger.info("\n[117] B Port 추가 상태:")
        b_port_additional = [
            "Cylinder Turn Complete",
            "Cylinder Clamp Complete",
            "CGA Connect Complete Status"
        ]
        for i, name in enumerate(b_port_additional):
            logger.info(f"[B] {name}: {bool(word_117 & (1<<i))}")

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

    #Gas Cabinet의 전체 상태 데이터를 JSON 형식으로 구조화 
    # 현재 상태를 Web 시스템에 제공하는 데이터 인터페이스 역할 제공    
    async def get_current_data(self):
        """현재 모든 데이터 조회"""
        async with self.data_lock:
            # PLC 데이터 영역 (0-99)
            plc_data = self.datablock.getValues(0, 100)
            # 비트 데이터 영역 (100-117)
            bit_data = self.datablock.getValues(100, 18)
            
            print("\n=== 서버 데이터 읽기 ===")
            print(f"PLC 데이터 첫 10개: {plc_data[:10]}")
            print(f"Bit 데이터 첫 5개: {bit_data[:5]}")

            return {
                "plc_data": {
                    "bunker_id": plc_data[0],
                    "cabinet_id": plc_data[1],
                    "gas_type": plc_data[2:7],
                    "system_status": {
                        "machine_code": plc_data[7],
                        "alarm_code": plc_data[8]
                    },
                    "sensors": {
                        "pt1a": plc_data[10],
                        "pt2a": plc_data[11],
                        "pt1b": plc_data[12],
                        "pt2b": plc_data[13],
                        "pt3": plc_data[14],
                        "pt4": plc_data[15],
                        "weight_a": plc_data[16],
                        "weight_b": plc_data[17]
                    },
                    "heaters": {
                        "jacket_heater_a": plc_data[18],
                        "line_heater_a": plc_data[19],
                        "jacket_heater_b": plc_data[20],
                        "line_heater_b": plc_data[21]
                    },
                    "port_a": {
                        "torque": {
                            "cga_set": plc_data[24],
                            "cap_set": plc_data[25],
                            "cylinder_pos": plc_data[26]
                        },
                        "barcode": plc_data[30:60],
                        "gas_type": plc_data[90:95]
                    },
                    "port_b": {
                        "torque": {
                            "cga_set": plc_data[27],
                            "cap_set": plc_data[28],
                            "cylinder_pos": plc_data[29]
                        },
                        "barcode": plc_data[60:90],
                        "gas_type": plc_data[95:100]
                    }
                },
                "bit_data": {
                    "basic_signals": {
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
                    "valves": {
                        "raw": bit_data[1],
                        "states": {
                            "av1a": bool(bit_data[1] & (1 << 0)),
                            "av2a": bool(bit_data[1] & (1 << 1)),
                            "av3a": bool(bit_data[1] & (1 << 2)),
                            "av4a": bool(bit_data[1] & (1 << 3)),
                            "av5a": bool(bit_data[1] & (1 << 4)),
                            "av1b": bool(bit_data[1] & (1 << 5)),
                            "av2b": bool(bit_data[1] & (1 << 6)),
                            "av3b": bool(bit_data[1] & (1 << 7)),
                            "av4b": bool(bit_data[1] & (1 << 8)),
                            "av5b": bool(bit_data[1] & (1 << 9)),
                            "av7": bool(bit_data[1] & (1 << 10)),
                            "av8": bool(bit_data[1] & (1 << 11)),
                            "av9": bool(bit_data[1] & (1 << 12))
                        }
                    },
                    "sensors_relays": {
                        "raw": bit_data[2],
                        "states": {
                            "jacket_heater_a": bool(bit_data[2] & (1 << 0)),
                            "line_heater_a": bool(bit_data[2] & (1 << 1)),
                            "jacket_heater_b": bool(bit_data[2] & (1 << 2)),
                            "line_heater_b": bool(bit_data[2] & (1 << 3)),
                            "gas_leak_shutdown": bool(bit_data[2] & (1 << 4)),
                            "vmb_stop": bool(bit_data[2] & (1 << 5)),
                            "uv_ir_sensor": bool(bit_data[2] & (1 << 6)),
                            "high_temp_sensor": bool(bit_data[2] & (1 << 7)),
                            "smoke_sensor": bool(bit_data[2] & (1 << 8))
                        }
                    },
                    "port_status": {
                        "raw": bit_data[3],
                        "states": {
                            "port_a": {
                                "insert_request": bool(bit_data[3] & (1 << 0)),
                                "insert_complete": bool(bit_data[3] & (1 << 1)),
                                "remove_request": bool(bit_data[3] & (1 << 2)),
                                "remove_complete": bool(bit_data[3] & (1 << 3))
                            },
                            "port_b": {
                                "insert_request": bool(bit_data[3] & (1 << 8)),
                                "insert_complete": bool(bit_data[3] & (1 << 9)),
                                "remove_request": bool(bit_data[3] & (1 << 10)),
                                "remove_complete": bool(bit_data[3] & (1 << 11))
                            }
                        }
                    },
                    "cylinder_door": {
                        "raw": bit_data[5],
                        "states": {
                            "port_a_cylinder": bool(bit_data[5] & (1 << 0)),
                            "port_b_cylinder": bool(bit_data[5] & (1 << 1)),
                            "door_open": bool(bit_data[5] & (1 << 2)),
                            "door_close": bool(bit_data[5] & (1 << 3))
                        }
                    },
                    "port_a_operation": {
                        "raw": bit_data[10],
                        "progress": {
                            "close_cylinder": bool(bit_data[10] & (1 << 0)),
                            "first_purge_before": bool(bit_data[10] & (1 << 1)),
                            "decompression_test": bool(bit_data[10] & (1 << 2)),
                            "second_purge_before": bool(bit_data[10] & (1 << 3)),
                            "exchange_cylinder": bool(bit_data[10] & (1 << 4)),
                            "first_purge_after": bool(bit_data[10] & (1 << 5)),
                            "pressure_test": bool(bit_data[10] & (1 << 6)),
                            "second_purge_after": bool(bit_data[10] & (1 << 7)),
                            "purge_completed": bool(bit_data[10] & (1 << 8)),
                            "prepare_supply": bool(bit_data[10] & (1 << 9)),
                            "av3_control": bool(bit_data[10] & (1 << 10)),
                            "gas_supply": bool(bit_data[10] & (1 << 11)),
                            "ready_supply": bool(bit_data[10] & (1 << 12))
                        }
                    },
                    "port_b_operation": {
                        "raw": bit_data[15],
                        "progress": {
                            "close_cylinder": bool(bit_data[15] & (1 << 0)),
                            "first_purge_before": bool(bit_data[15] & (1 << 1)),
                            "decompression_test": bool(bit_data[15] & (1 << 2)),
                            "second_purge_before": bool(bit_data[15] & (1 << 3)),
                            "exchange_cylinder": bool(bit_data[15] & (1 << 4)),
                            "first_purge_after": bool(bit_data[15] & (1 << 5)),
                            "pressure_test": bool(bit_data[15] & (1 << 6)),
                            "second_purge_after": bool(bit_data[15] & (1 << 7)),
                            "purge_completed": bool(bit_data[15] & (1 << 8)),
                            "prepare_supply": bool(bit_data[15] & (1 << 9)),
                            "av3_control": bool(bit_data[15] & (1 << 10)),
                            "gas_supply": bool(bit_data[15] & (1 << 11)),
                            "ready_supply": bool(bit_data[15] & (1 << 12))
                        }
                    },
                    "port_b_details": {
                        "raw": bit_data[16],
                        "states": {
                            "cylinder_ready": bool(bit_data[16] & (1 << 0)),
                            "cga_disconnect": bool(bit_data[16] & (1 << 1)),
                            "cga_connect": bool(bit_data[16] & (1 << 2)),
                            "valve_open_complete": bool(bit_data[16] & (1 << 3)),
                            "valve_close_complete": bool(bit_data[16] & (1 << 4)),
                            "valve_open_status": bool(bit_data[16] & (1 << 5)),
                            "lift_ready": bool(bit_data[16] & (1 << 6)),
                            "lift_moving_up": bool(bit_data[16] & (1 << 7)),
                            "lift_moving_down": bool(bit_data[16] & (1 << 8)),
                            "cga_separating": bool(bit_data[16] & (1 << 9)),
                            "cga_connecting": bool(bit_data[16] & (1 << 10)),
                            "cap_separating": bool(bit_data[16] & (1 << 11)),
                            "valve_opening": bool(bit_data[16] & (1 << 12)),
                            "valve_closing": bool(bit_data[16] & (1 << 13)),
                            "cylinder_aligning": bool(bit_data[16] & (1 << 14)),
                            "cylinder_turning": bool(bit_data[16] & (1 << 15))
                        }
                    },
                    "port_b_additional": {
                        "raw": bit_data[17],
                        "states": {
                            "cylinder_turn_complete": bool(bit_data[17] & (1 << 0)),
                            "cylinder_clamp_complete": bool(bit_data[17] & (1 << 1)),
                            "cga_connect_status": bool(bit_data[17] & (1 << 2))
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