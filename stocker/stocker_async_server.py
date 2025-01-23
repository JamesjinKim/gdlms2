import logging
import os
from pymodbus.server import StartAsyncTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSlaveContext, ModbusServerContext
import asyncio

# Ensure the log directory exists
log_dir = "./log"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "stocker.log")

# Configure logging
logger = logging.getLogger("StockerLogger")
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
logger.addHandler(file_handler)
logger.addHandler(logging.StreamHandler())

class CustomDataBlock(ModbusSequentialDataBlock):
    def __init__(self):
        super().__init__(0, [0] * 200)  # Initialize with 138 WORDs to include bit data

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
        """PLC data logging (addresses 0-99)"""
        logger.info("=== PLC Data Area ===")

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
        logger.info("\n=== Bit Area Data ===")

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

    async def run(self):
        try:
            logger.info("\n=== Modbus Server Starting... ===")
            await StartAsyncTcpServer(
                context=self.context,
                address=('127.0.0.1', 5020)
            )
            logger.info("Server started successfully")
        except Exception as e:
            logger.error(f"Server error: {e}")
        finally:
            self.running = False
            logger.info("Server shutdown complete")

async def main():
    server = ModbusServer()
    await server.run()

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