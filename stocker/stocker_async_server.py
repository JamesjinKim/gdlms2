from http import client
import logging
import os
import socket
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import asyncio, time, json, datetime
from logging.handlers import TimedRotatingFileHandler
from pymodbus.server import StartAsyncTcpServer
from pymodbus.device import ModbusDeviceIdentification

# 로그 디렉토리 설정
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
        super().__init__(0, [0] * 200)  # Initialize with 100 WORDs (200 bytes)
        self.last_log_time = 0
        self.LOG_INTERVAL = 1  # 1-second logging interval
        self._buffer = []  # Data buffer

    def setValues(self, address, values):
        # Append changed data to the buffer
        self._buffer.append((address, values))
        super().setValues(address, values)
        
        current_time = time.time()
        if current_time - self.last_log_time >= self.LOG_INTERVAL:
            self.last_log_time = current_time
            self.log_all_data()
            self._buffer.clear()  # Clear the buffer

    def log_all_data(self):
        """Log all data"""
        all_values = self.getValues(0, 100)
        self.log_plc_data(all_values)
        bit_values = self.getValues(100, 20)
        self.log_bit_data()

    def log_plc_data(self, all_values):
        """PLC 데이터 로깅 (주소 0-99)"""
        logger.info("\n=== Stocker PLC Data Area ===")
        logger.info(f"Bunker ID: {all_values[0]}")
        logger.info(f"Stocker ID: {all_values[1]}")
        logger.info(f"Gas Stocker 가스 종류: {all_values[2:7]}")
        logger.info(f"Stocker Alarm Code: {all_values[8]}")
        logger.info(f"X축 현재값: {all_values[10]}")
        logger.info(f"Z축 현재값: {all_values[11]}")
        logger.info(f"Cap Unit 축 보호캡 분리 Torque 설정값: {all_values[12]}")
        logger.info(f"Cap Unit 축 보호캡 체결 Torque 설정값: {all_values[13]}")
        barcode_a = ''.join([chr(x) if 32 <= x <= 126 else '?' for x in all_values[30:60]])
        logger.info(f"[A] Port Barcode Data: {barcode_a}")
        barcode_b = ''.join([chr(x) if 32 <= x <= 126 else '?' for x in all_values[60:90]])
        logger.info(f"[B] Port Barcode Data: {barcode_b}")
        logger.info(f"[A] Port 가스 종류: {all_values[90:95]}")
        logger.info(f"[B] Port 가스 종류: {all_values[95:100]}")
        logger.info("==================")

    def log_bit_data(self):
        """비트 데이터 로깅 (주소 100-116)"""
        logger.info("\n=== Stocker Bit Area Data ===")
        basic_signals = [
            "emg_signal", "heart_bit", "run_stop_signal", "server_connected",
            "t_lamp_red", "t_lamp_yellow", "t_lamp_green", "touch_manual"
        ]
        for i, name in enumerate(basic_signals):
            logger.info(f"{name}: {bool(self.getValues(100, 1)[0] & (1 << i))}")

        door_cylinder_status = [
            "[A]_cylinder", "[B]_cylinder",
            "[A]_worker_door_open", "[A]_worker_door_close",
            "[A]_bunker_door_open", "[A]_bunker_door_close",
            "[B]_worker_door_open", "[B]_worker_door_close",
            "[B]_bunker_door_open", "[B]_bunker_door_close"
        ]
        for i, name in enumerate(door_cylinder_status):
            logger.info(f"{name}: {bool(self.getValues(105, 1)[0] & (1 << i))}")

        a_port_operation_status = [
            "[A]_cap_open_complete", "[A]_cap_close_complete",
            "[A]_worker_door_open_complete", "[A]_worker_door_close_complete",
            "[A]_worker_input_ready", "[A]_worker_input_complete",
            "[A]_worker_output_ready", "[A]_worker_output_complete",
            "[A]_bunker_door_open_complete", "[A]_bunker_door_close_complete",
            "[A]_bunker_input_ready", "[A]_bunker_input_complete",
            "[A]_bunker_output_ready", "[A]_bunker_output_complete",
            "[A]_cylinder_align_in_progress", "[A]_cylinder_align_complete"
        ]
        for i, name in enumerate(a_port_operation_status):
            logger.info(f"{name}: {bool(self.getValues(110, 1)[0] & (1 << i))}")

        a_port_detailed_status = [
            "[A]_cap_opening", "[A]_cap_closing",
            "[A]_x_axis_moving", "[A]_x_axis_complete",
            "[A]_finding_cap", "[A]_finding_cylinder_neck",
            "[A]_worker_door_opening", "[A]_worker_door_closing",
            "[A]_bunker_door_opening", "[A]_bunker_door_closing"
        ]
        for i, name in enumerate(a_port_detailed_status):
            logger.info(f"{name}: {bool(self.getValues(111, 1)[0] & (1 << i))}")

        b_port_operation_status = [
            "[B]_cap_open_complete", "[B]_cap_close_complete",
            "[B]_worker_door_open_complete", "[B]_worker_door_close_complete",
            "[B]_worker_input_ready", "[B]_worker_input_complete",
            "[B]_worker_output_ready", "[B]_worker_output_complete",
            "[B]_bunker_door_open_complete", "[B]_bunker_door_close_complete",
            "[B]_bunker_input_ready", "[B]_bunker_input_complete",
            "[B]_bunker_output_ready", "[B]_bunker_output_complete",
            "[B]_cylinder_align_in_progress", "[B]_cylinder_align_complete"
        ]
        for i, name in enumerate(b_port_operation_status):
            logger.info(f"{name}: {bool(self.getValues(115, 1)[0] & (1 << i))}")

        b_port_detailed_status = [
            "[B]_cap_opening", "[B]_cap_closing",
            "[B]_x_axis_moving", "[B]_x_axis_complete",
            "[B]_finding_cap", "[B]_finding_cylinder_neck",
            "[B]_worker_door_opening", "[B]_worker_door_closing",
            "[B]_bunker_door_opening", "[B]_bunker_door_close"
        ]
        for i, name in enumerate(b_port_detailed_status):
            logger.info(f"{name}: {bool(self.getValues(116, 1)[0] & (1 << i))}")
        logger.info("==================")

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
        self.identity = ModbusDeviceIdentification()
        self.identity.VendorName = 'Pymodbus'
        self.identity.ProductCode = 'PM'
        self.identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
        self.identity.ProductName = 'Pymodbus Server'
        self.identity.ModelName = 'Pymodbus Server'

    async def run_server(self):
        """서버 실행"""
        server = None
        try:
            print("\n=== Modbus 서버 시작 중... ===")
            self.running = True  # 서버 실행 상태 설정

            # Modbus 서버 시작
            server = await StartAsyncTcpServer(
                context=self.context,
                identity=self.identity,
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
            print("\n=== 서버가 종료되었습니다 ===")

    async def handle_socket_client(self, client_socket, addr):
        """소켓 클라이언트 처리"""
        try:
            while True:
                # 데이터 요청을 받으면 현재 데이터 전송
                data = await self.get_current_data()
                await self.send_socket_data(client_socket, data)
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            logger.info(f"Socket client {addr} connection cancelled.")
        except Exception as e:
            logger.error(f"Socket client {addr} error: {e}")
        finally:
            client_socket.close()
            logger.info(f"Socket client {addr} connection closed.")

    async def get_current_data(self):
        """현재 모든 데이터 조회"""
        async with self.data_lock:
            # PLC 데이터 영역 (0-99)
            plc_data = self.datablock.getValues(0, 100)  # PLC 데이터는 0부터 99까지이므로 100으로 설정
            # 비트 데이터 영역 (100-117)
            bit_data = self.datablock.getValues(100, 20)
            
            print("\n=== 서버 데이터 읽기 ===")
            #print(f"PLC 데이터 첫 10개: {plc_data[:10]})
            #print(f"Bit 데이터 첫 5개: {bit_data[:5]})

            # PLC 데이터 처리
            plc_states = {
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
            }

            # Bit 데이터 처리
            bit_states = {}
            word_dict = {
                100: [
                    (0, "emg_signal"),
                    (1, "heart_bit"),
                    (2, "run_stop_signal"),
                    (3, "server_connected"),
                    (4, "t_lamp_red"),
                    (5, "t_lamp_yellow"),
                    (6, "t_lamp_green"),
                    (7, "touch_manual")
                ],
                105: [
                    (0, "[A]_cylinder"),
                    (1, "[B]_cylinder"),
                    (2, "[A]_worker_door_open"),
                    (3, "[A]_worker_door_close"),
                    (4, "[A]_bunker_door_open"),
                    (5, "[A]_bunker_door_close"),
                    (6, "[B]_worker_door_open"),
                    (7, "[B]_worker_door_close"),
                    (8, "[B]_bunker_door_open"),
                    (9, "[B]_bunker_door_close")
                ],
                110: [
                    (0, "[A]_cap_open_complete"),
                    (1, "[A]_cap_close_complete"),
                    (2, "[A]_worker_door_open_complete"),
                    (3, "[A]_worker_door_close_complete"),
                    (4, "[A]_worker_input_ready"),
                    (5, "[A]_worker_input_complete"),
                    (6, "[A]_worker_output_ready"),
                    (7, "[A]_worker_output_complete"),
                    (8, "[A]_bunker_door_open_complete"),
                    (9, "[A]_bunker_door_close_complete"),
                    (10, "[A]_bunker_input_ready"),
                    (11, "[A]_bunker_input_complete"),
                    (12, "[A]_bunker_output_ready"),
                    (13, "[A]_bunker_output_complete"),
                    (14, "[A]_cylinder_align_in_progress"),
                    (15, "[A]_cylinder_align_complete")
                ],
                111: [
                    (0, "[A]_cap_opening"),
                    (1, "[A]_cap_closing"),
                    (2, "[A]_x_axis_moving"),
                    (3, "[A]_x_axis_complete"),
                    (4, "[A]_finding_cap"),
                    (5, "[A]_finding_cylinder_neck"),
                    (6, "[A]_worker_door_opening"),
                    (7, "[A]_worker_door_closing"),
                    (8, "[A]_bunker_door_opening"),
                    (9, "[A]_bunker_door_closing")
                ],
                115: [
                    (0, "[B]_cap_open_complete"),
                    (1, "[B]_cap_close_complete"),
                    (2, "[B]_worker_door_open_complete"),
                    (3, "[B]_worker_door_close_complete"),
                    (4, "[B]_worker_input_ready"),
                    (5, "[B]_worker_input_complete"),
                    (6, "[B]_worker_output_ready"),
                    (7, "[B]_worker_output_complete"),
                    (8, "[B]_bunker_door_open_complete"),
                    (9, "[B]_bunker_door_close_complete"),
                    (10, "[B]_bunker_input_ready"),
                    (11, "[B]_bunker_input_complete"),
                    (12, "[B]_bunker_output_ready"),
                    (13, "[B]_bunker_output_complete"),
                    (14, "[B]_cylinder_align_in_progress"),
                    (15, "[B]_cylinder_align_complete")
                ],
                116: [
                    (0, "[B]_cap_opening"),
                    (1, "[B]_cap_closing"),
                    (2, "[B]_x_axis_moving"),
                    (3, "[B]_x_axis_complete"),
                    (4, "[B]_finding_cap"),
                    (5, "[B]_finding_cylinder_neck"),
                    (6, "[B]_worker_door_opening"),
                    (7, "[B]_worker_door_closing"),
                    (8, "[B]_bunker_door_opening"),
                    (9, "[B]_bunker_door_close")
                ]
            }

            for address, bits in word_dict.items():
                word = bit_data[address - 100]
                bit_states[address] = {}
                for bit, description in bits:
                    bit_states[address][description] = bool(word & (1 << bit))

            return {
                "plc_data": plc_states,
                "bit_data": bit_states
            }
        
    async def update_values(self, address, values):
        async with self.data_lock:
            self.datablock.setValues(address, values)

    async def on_client_connect(self, client_socket):
        """클라이언트 연결 시 호출되는 콜백"""
        print(f"새로운 클라이언트 연결됨: {client_socket.getpeername()}")
        await self.send_time_sync()  # 시간 동기화 데이터 전송

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

    async def send_socket_data(self, client_socket, data):
        """소켓을 통해 데이터 전송"""
        try:
            json_data = json.dumps(data)
            await asyncio.get_event_loop().sock_sendall(client_socket, json_data.encode('utf-8'))
        except Exception as e:
            print(f"Socket send error: {e}")

    async def accept_socket_clients(self):
        """소켓 클라이언트 연결 수락"""
        server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_socket.bind('/tmp/modbus_data.sock')
        server_socket.listen(1)
        server_socket.setblocking(False)
        while self.running:
            try:
                client_socket, addr = await asyncio.get_event_loop().sock_accept(server_socket)
                print(f"Socket client connected: {addr}")
                asyncio.create_task(self.handle_socket_client(client_socket, addr))
            except Exception as e:
                if self.running:
                    print(f"Socket accept error: {e}")
                await asyncio.sleep(1)

    async def handle_socket_client(self, client_socket, addr):
        """소켓 클라이언트 처리"""
        try:
            while True:
                # 데이터 요청을 받으면 현재 데이터 전송
                data = await self.get_current_data()
                await self.send_socket_data(client_socket, data)
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            logger.info(f"Socket client {addr} connection cancelled.")
        except Exception as e:
            logger.error(f"Socket client {addr} error: {e}")
        finally:
            client_socket.close()
            logger.info(f"Socket client {addr} connection closed.")

    async def get_current_data(self):
        """현재 모든 데이터 조회"""
        async with self.data_lock:
            # PLC 데이터 영역 (0-99)
            plc_data = self.datablock.getValues(0, 100)  # PLC 데이터는 0부터 99까지이므로 100으로 설정
            # 비트 데이터 영역 (100-117)
            bit_data = self.datablock.getValues(100, 20)
            print("\n=== 서버 데이터 읽기 ===")
            
            # PLC 데이터 처리
            plc_states = {
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
            }

            # Bit 데이터 처리
            bit_states = {}
            word_dict = {
                100: [
                    (0, "emg_signal"),
                    (1, "heart_bit"),
                    (2, "run_stop_signal"),
                    (3, "server_connected"),
                    (4, "t_lamp_red"),
                    (5, "t_lamp_yellow"),
                    (6, "t_lamp_green"),
                    (7, "touch_manual")
                ],
                105: [
                    (0, "[A]_cylinder"),
                    (1, "[B]_cylinder"),
                    (2, "[A]_worker_door_open"),
                    (3, "[A]_worker_door_close"),
                    (4, "[A]_bunker_door_open"),
                    (5, "[A]_bunker_door_close"),
                    (6, "[B]_worker_door_open"),
                    (7, "[B]_worker_door_close"),
                    (8, "[B]_bunker_door_open"),
                    (9, "[B]_bunker_door_close")
                ],
                110: [
                    (0, "[A]_cap_open_complete"),
                    (1, "[A]_cap_close_complete"),
                    (2, "[A]_worker_door_open_complete"),
                    (3, "[A]_worker_door_close_complete"),
                    (4, "[A]_worker_input_ready"),
                    (5, "[A]_worker_input_complete"),
                    (6, "[A]_worker_output_ready"),
                    (7, "[A]_worker_output_complete"),
                    (8, "[A]_bunker_door_open_complete"),
                    (9, "[A]_bunker_door_close_complete"),
                    (10, "[A]_bunker_input_ready"),
                    (11, "[A]_bunker_input_complete"),
                    (12, "[A]_bunker_output_ready"),
                    (13, "[A]_bunker_output_complete"),
                    (14, "[A]_cylinder_align_in_progress"),
                    (15, "[A]_cylinder_align_complete")
                ],
                111: [
                    (0, "[A]_cap_opening"),
                    (1, "[A]_cap_closing"),
                    (2, "[A]_x_axis_moving"),
                    (3, "[A]_x_axis_complete"),
                    (4, "[A]_finding_cap"),
                    (5, "[A]_finding_cylinder_neck"),
                    (6, "[A]_worker_door_opening"),
                    (7, "[A]_worker_door_closing"),
                    (8, "[A]_bunker_door_opening"),
                    (9, "[A]_bunker_door_closing")
                ],
                115: [
                    (0, "[B]_cap_open_complete"),
                    (1, "[B]_cap_close_complete"),
                    (2, "[B]_worker_door_open_complete"),
                    (3, "[B]_worker_door_close_complete"),
                    (4, "[B]_worker_input_ready"),
                    (5, "[B]_worker_input_complete"),
                    (6, "[B]_worker_output_ready"),
                    (7, "[B]_worker_output_complete"),
                    (8, "[B]_bunker_door_open_complete"),
                    (9, "[B]_bunker_door_close_complete"),
                    (10, "[B]_bunker_input_ready"),
                    (11, "[B]_bunker_input_complete"),
                    (12, "[B]_bunker_output_ready"),
                    (13, "[B]_bunker_output_complete"),
                    (14, "[B]_cylinder_align_in_progress"),
                    (15, "[B]_cylinder_align_complete")
                ],
                116: [
                    (0, "[B]_cap_opening"),
                    (1, "[B]_cap_closing"),
                    (2, "[B]_x_axis_moving"),
                    (3, "[B]_x_axis_complete"),
                    (4, "[B]_finding_cap"),
                    (5, "[B]_finding_cylinder_neck"),
                    (6, "[B]_worker_door_opening"),
                    (7, "[B]_worker_door_closing"),
                    (8, "[B]_bunker_door_opening"),
                    (9, "[B]_bunker_door_close")
                ]
            }

            for address, bits in word_dict.items():
                word = bit_data[address - 100]
                bit_states[address] = {}
                for bit, description in bits:
                    bit_states[address][description] = bool(word & (1 << bit))

            return {
                "plc_data": plc_states,
                "bit_data": bit_states
            }
        
    async def handle_client(self, client_socket):
        self.clients.add(client_socket)
        try:
            while True:
                await asyncio.sleep(0.1)
                if client_socket.is_closing():
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
    
    async def send_socket_data(self, client_socket, data):
        """소켓을 통해 데이터 전송"""
        try:
            json_data = json.dumps(data)
            await asyncio.get_event_loop().sock_sendall(client_socket, json_data.encode('utf-8'))
        except Exception as e:
            print(f"Socket send error: {e}")

    async def accept_socket_clients(self):
        """소켓 클라이언트 연결 수락"""
        server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server_socket.bind('/tmp/modbus_data.sock')
        server_socket.listen(1)
        server_socket.setblocking(False)
        while self.running:
            try:
                client_socket, addr = await asyncio.get_event_loop().sock_accept(server_socket)
                print(f"Socket client connected: {addr}")
                asyncio.create_task(self.handle_socket_client(client_socket, addr))
            except Exception as e:
                if self.running:
                    print(f"Socket accept error: {e}")
                await asyncio.sleep(1)
    
async def main():
    server = ModbusServer()
    try:
        await server.run_server()
    except KeyboardInterrupt:
        logging.info("\n프로그램이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        logging.error(f"예기치 않은 오류 발생: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("사용자가 서버를 중단했습니다.")
    except Exception as e:
        logger.error(f"예기치 않은 오류 발생: {e}")


#Word 100 (Basic signals):
# EMG Signal: word_100 |= random.choice([0, 1]) << 0
# Heart Bit: word_100 |= random.choice([0, 1]) << 1
# Run/Stop Signal: word_100 |= random.choice([0, 1]) << 2
# Server Connected Bit: word_100 |= random.choice([0, 1]) << 3
# T-LAMP RED: word_100 |= random.choice([0, 1]) << 4
# T-LAMP YELLOW: word_100 |= random.choice([0, 1]) << 5
# T-LAMP GREEN: word_100 |= random.choice([0, 1]) << 6
# Touch 수동동작中 Signal: word_100 |= random.choice([0, 1]) << 7

#Word 105 (Door and cylinder status):
# [A] Port 실린더 유무: word_105 |= random.choice([0, 1]) << 0
# [B] Port 실린더 유무: word_105 |= random.choice([0, 1]) << 1
# [A] Worker Door Open: word_105 |= random.choice([0, 1]) << 2
# [A] Worker Door Close: word_105 |= random.choice([0, 1]) << 3
# [A] Bunker Door Open: word_105 |= random.choice([0, 1]) << 4
# [A] Bunker Door Close: word_105 |= random.choice([0, 1]) << 5
# [B] Worker Door Open: word_105 |= random.choice([0, 1]) << 6
# [B] Worker Door Close: word_105 |= random.choice([0, 1]) << 7
# [B] Bunker Door Open: word_105 |= random.choice([0, 1]) << 8
# [B] Bunker Door Close: word_105 |= random.choice([0, 1]) << 9

#Word 110 ([A] Port operation status):
# [A] Port 보호캡 분리 완료: word_110 |= random.choice([0, 1]) << 0
# [A] Port 보호캡 체결 완료: word_110 |= random.choice([0, 1]) << 1
# [A] Worker Door Open 완료: word_110 |= random.choice([0, 1]) << 2
# [A] Worker Door Close 완료: word_110 |= random.choice([0, 1]) << 3
# [A] Worker 투입 Ready: word_110 |= random.choice([0, 1]) << 4
# [A] Worker 투입 Complete: word_110 |= random.choice([0, 1]) << 5
# [A] Worker 배출 Ready: word_110 |= random.choice([0, 1]) << 6
# [A] Worker 배출 Comlete: word_110 |= random.choice([0, 1]) << 7
# [A] Bunker Door Open 완료: word_110 |= random.choice([0, 1]) << 8
# [A] Bunker Door Close 완료: word_110 |= random.choice([0, 1]) << 9
# [A] Bunker 투입 Ready: word_110 |= random.choice([0, 1]) << 10
# [A] Bunker 투입 Complete: word_110 |= random.choice([0, 1]) << 11
# [A] Bunker 배출 Ready: word_110 |= random.choice([0, 1]) << 12
# [A] Bunker 배출 Comlete: word_110 |= random.choice([0, 1]) << 13
# [A] Cylinder Align 진행중: word_110 |= random.choice([0, 1]) << 14
# [A] Cylinder Align 완료: word_110 |= random.choice([0, 1]) << 15

#Word 111 ([A] Port detailed status):
# [A] Cap Open 진행중: word_111 |= random.choice([0, 1]) << 0
# [A] Cap Close 진행중: word_111 |= random.choice([0, 1]) << 1
# [A] Cylinder 위치로 X축 이동중: word_111 |= random.choice([0, 1]) << 2
# [A] Cylinder 위치로 X축 이동완료: word_111 |= random.choice([0, 1]) << 3
# [A] Cap 위치 찾는중: word_111 |= random.choice([0, 1]) << 4
# [A] Cylinder Neck 위치 찾는중: word_111 |= random.choice([0, 1]) << 5
# [A] Worker door Open 진행중: word_111 |= random.choice([0, 1]) << 6
# [A] Worker door Close 진행중: word_111 |= random.choice([0, 1]) << 7
# [A] Bunker door Open 진행중: word_111 |= random.choice([0, 1]) << 8
# [A] Bunker door Close 진행중: word_111 |= random.choice([0, 1]) << 9

# Word 115 ([B] Port operation status):
# [B] Port 보호캡 분리 완료: word_115 |= random.choice([0, 1]) << 0
# [B] Port 보호캡 체결 완료: word_115 |= random.choice([0, 1]) << 1
# [B] Worker Door Open 완료: word_115 |= random.choice([0, 1]) << 2
# [B] Worker Door Close 완료: word_115 |= random.choice([0, 1]) << 3
# [B] Worker 투입 Ready: word_115 |= random.choice([0, 1]) << 4
# [B] Worker 투입 Complete: word_115 |= random.choice([0, 1]) << 5
# [B] Worker 배출 Ready: word_115 |= random.choice([0, 1]) << 6
# [B] Worker 배출 Comlete: word_115 |= random.choice([0, 1]) << 7
# [B] Bunker Door Open 완료: word_115 |= random.choice([0, 1]) << 8
# [B] Bunker Door Close 완료: word_115 |= random.choice([0, 1]) << 9
# [B] Bunker 투입 Ready: word_115 |= random.choice([0, 1]) << 10
# [B] Bunker 투입 Complete: word_115 |= random.choice([0, 1]) << 11
# [B] Bunker 배출 Ready: word_115 |= random.choice([0, 1]) << 12
# [B] Bunker 배출 Comlete: word_115 |= random.choice([0, 1]) << 13
# [B] Cylinder Align 진행중: word_115 |= random.choice([0, 1]) << 14
# [B] Cylinder Align 완료: word_115 |= random.choice([0, 1]) << 15

# Word 116 ([B] Port detailed status):
# [B] Cap Open 진행중: word_116 |= random.choice([0, 1]) << 0
# [B] Cap Close 진행중: word_116 |= random.choice([0, 1]) << 1
# [B] Cylinder 위치로 X축 이동중: word_116 |= random.choice([0, 1]) << 2
# [B] Cylinder 위치로 X축 이동완료: word_116 |= random.choice([0, 1]) << 3
# [B] Cap 위치 찾는중: word_116 |= random.choice([0, 1]) << 4
# [B] Cylinder Neck 위치 찾는중: word_116 |= random.choice([0, 1]) << 5
# [B] Worker door Open 진행중: word_116 |= random.choice([0, 1]) << 6
# [B] Worker door Close 진행중: word_116 |= random.choice([0, 1]) << 7
# [B] Bunker door Open 진행중: word_116 |= random.choice([0, 1]) << 8
# [B] Bunker door Close 진행중: word_116 |= random.choice([0, 1]) << 9