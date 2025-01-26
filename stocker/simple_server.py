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
log_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
log_handler.setLevel(logging.INFO)

# 로거 설정
logger = logging.getLogger("StockerLogger")
logger.setLevel(logging.INFO)
logger.addHandler(log_handler)
logger.addHandler(logging.StreamHandler())

# Custom Data Block 클래스
class CustomModbusSequentialDataBlock(ModbusSequentialDataBlock):
   def __init__(self, address, values):
       super().__init__(address, values)
       self.last_log_time = 0
       self.LOG_INTERVAL = 1
       self._buffer = []

   def setValues(self, address, values):
       self._buffer.append((address, values))
       super().setValues(address, values)
       
       current_time = time.time()
       if current_time - self.last_log_time >= self.LOG_INTERVAL:
           if self._buffer:
               self.last_log_time = current_time
               self.log_all_data()
               self._buffer.clear()

   def log_all_data(self):
        """모든 데이터 로깅"""
        with open("./log/stocker.log", "a") as f:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # PLC 데이터 영역
            f.write(f"{current_time} | ========= plc_data 시작 =========\n")
            values = self.getValues(0, 100)
            
            # 기본 정보
            f.write(f"{current_time} | Bunker ID: {values[0]}\n")
            f.write(f"{current_time} | Stocker ID: {values[1]}\n")
            for i in range(2, 7):
                f.write(f"{current_time} | Gas Stocker 가스 종류 {i-1}: {values[i]}\n")
            
            # X, Z축 및 Torque 값
            f.write(f"{current_time} | Stocker Alarm Code: {values[8]}\n")
            f.write(f"{current_time} | X축 현재값: {values[10]}\n")
            f.write(f"{current_time} | Z축 현재값: {values[11]}\n")
            f.write(f"{current_time} | Cap Unit 축 보호캡 분리 Torque: {values[12]}\n")
            f.write(f"{current_time} | Cap Unit 축 보호캡 체결 Torque: {values[13]}\n")

            # Port A Barcode
            barcode_a = ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' for i in range(30, 60)])
            f.write(f"{current_time} | [A] Port Barcode: {barcode_a}\n")

            # Port B Barcode
            barcode_b = ''.join([chr(values[i]) if 32 <= values[i] <= 126 else ' ' for i in range(60, 90)])
            f.write(f"{current_time} | [B] Port Barcode: {barcode_b}\n")

            # Port 가스 종류
            for i in range(90, 95):
                f.write(f"{current_time} | [A] Port 가스 종류 {i-89}: {values[i]}\n")
            for i in range(95, 100):
                f.write(f"{current_time} | [B] Port 가스 종류 {i-94}: {values[i]}\n")

            # 비트 데이터 영역
            f.write(f"{current_time} | ========= bit_data 시작 =========\n")
            bit_values = self.getValues(100, 18)
            
            # Word 100 - 기본 신호
            signals = ["EMG Signal", "Heart Bit", "Run/Stop Signal", "Server Connected Bit",
                        "T-LAMP RED", "T-LAMP YELLOW", "T-LAMP GREEN", "Touch 수동동작中 Signal"]
            for i, name in enumerate(signals):
                value = bool(bit_values[0] & (1 << i))
                f.write(f"{current_time} | {name}: {value}\n")

            # Word 105 - 실린더 및 도어 상태
            cylinder_door = [
                "[A] Port 실린더 유무", "[B] Port 실린더 유무",
                "[A] Worker Door Open", "[A] Worker Door Close",
                "[A] Bunker Door Open", "[A] Bunker Door Close",
                "[B] Worker Door Open", "[B] Worker Door Close",
                "[B] Bunker Door Open", "[B] Bunker Door Close"
            ]
            for i, name in enumerate(cylinder_door):
                value = bool(bit_values[5] & (1 << i))
                f.write(f"{current_time} | {name}: {value}\n")

            # Word 110 - A Port 상태
            a_port_status = [
                "[A] Port 보호캡 분리 완료", "[A] Port 보호캡 체결 완료",
                "[A] Worker Door Open 완료", "[A] Worker Door Close 완료",
                "[A] Worker 투입 Ready", "[A] Worker 투입 Complete",
                "[A] Worker 배출 Ready", "[A] Worker 배출 Comlete",
                "[A] Bunker Door Open 완료", "[A] Bunker Door Close 완료",
                "[A] Bunker 투입 Ready", "[A] Bunker 투입 Complete",
                "[A] Bunker 배출 Ready", "[A] Bunker 배출 Comlete",
                "[A] Cylinder Align 진행중", "[A] Cylinder Align 완료"
            ]
            for i, name in enumerate(a_port_status):
                value = bool(bit_values[10] & (1 << i))
                f.write(f"{current_time} | {name}: {value}\n")

            # Word 111 - A Port 진행상태
            a_port_progress = [
                "[A] Cap Open 진행중", "[A] Cap Close 진행중",
                "[A] Cylinder 위치로 X축 이동중", "[A] Cylinder 위치로 X축 이동완료",
                "[A] Cap 위치 찾는중", "[A] Cylinder Neck 위치 찾는중",
                "[A] Worker door Open 진행중", "[A] Worker door Close 진행중",
                "[A] Bunker door Open 진행중", "[A] Bunker door Close 진행중"
            ]
            for i, name in enumerate(a_port_progress):
                value = bool(bit_values[11] & (1 << i))
                f.write(f"{current_time} | {name}: {value}\n")
                # Word 115 - B Port 상태
            b_port_status = [
                "[B] Port 보호캡 분리 완료", "[B] Port 보호캡 체결 완료",
                "[B] Worker Door Open 완료", "[B] Worker Door Close 완료",
                "[B] Worker 투입 Ready", "[B] Worker 투입 Complete",
                "[B] Worker 배출 Ready", "[B] Worker 배출 Comlete",
                "[B] Bunker Door Open 완료", "[B] Bunker Door Close 완료",
                "[B] Bunker 투입 Ready", "[B] Bunker 투입 Complete",
                "[B] Bunker 배출 Ready", "[B] Bunker 배출 Comlete",
                "[B] Cylinder Align 진행중", "[B] Cylinder Align 완료"
            ]
            for i, name in enumerate(b_port_status):
                value = bool(bit_values[15] & (1 << i))
                f.write(f"{current_time} | {name}: {value}\n")

            # Word 116 - B Port 진행상태
            b_port_progress = [
                "[B] Cap Open 진행중", "[B] Cap Close 진행중",
                "[B] Cylinder 위치로 X축 이동중", "[B] Cylinder 위치로 X축 이동완료",
                "[B] Cap 위치 찾는중", "[B] Cylinder Neck 위치 찾는중",
                "[B] Worker door Open 진행중", "[B] Worker door Close 진행중",
                "[B] Bunker door Open 진행중", "[B] Bunker door Close 진행중"
            ]
            for i, name in enumerate(b_port_progress):
                value = bool(bit_values[16] & (1 << i))
                f.write(f"{current_time} | {name}: {value}\n")

# Custom Slave Context 클래스
class CustomModbusSlaveContext(ModbusSlaveContext):
    def __init__(self):
        super().__init__(
            di=CustomModbusSequentialDataBlock(0, [0]*1000),
            co=CustomModbusSequentialDataBlock(0, [0]*1000),
            hr=CustomModbusSequentialDataBlock(0, [0]*1000),
            ir=CustomModbusSequentialDataBlock(0, [0]*1000)
        )
        self.update_time()
    
    def update_time(self):
        now = datetime.datetime.now()
        self.setValues(3, 0, [
            now.year,
            now.month,
            now.day,
            now.hour,
            now.minute,
            now.second
        ])

# 서버 실행 함수
async def run_server():
   store = CustomModbusSlaveContext()
   context = ModbusServerContext(slaves=store, single=True)
   
   identity = ModbusDeviceIdentification()
   identity.VendorName = 'Pymodbus'
   identity.ProductCode = 'Stocker'
   identity.ModelName = 'Stocker Server'
   identity.MajorMinorRevision = '1.0'

   logger.info("Starting Modbus TCP Server...")
   await StartAsyncTcpServer(
       context=context,
       identity=identity,
       address=("127.0.0.1", 5020)
   )

if __name__ == "__main__":
   try:
       asyncio.run(run_server())
   except KeyboardInterrupt:
       logger.info("Server stopped by user")
   except Exception as e:
       logger.error(f"Server error: {e}")