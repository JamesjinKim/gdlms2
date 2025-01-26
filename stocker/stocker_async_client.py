from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusIOException
import random
import asyncio
import logging

# Logging setup
logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger("StockerClient")

def generate_plc_data() -> list:
    """Generate random data for registers."""
    data = [0] * 120  # Initialize with zeros, covering all 120 WORDs

    # Fill data with random values as per your specification
    data[0] = random.randint(1, 100)  # Bunker ID
    data[1] = random.randint(1, 100)  # Stocker ID
    for i in range(2, 7):  # Gas Stocker 가스 종류
        data[i] = random.randint(1, 10)
    data[8] = random.randint(0, 500)  # Stocker Alarm Code
    data[10] = random.randint(0, 1000)  # X축 현재값
    data[11] = random.randint(0, 1000)  # Z축 현재값
    data[12] = random.randint(0, 100)  # Cap Unit 축 보호캡 분리 Torque 설정값
    data[13] = random.randint(0, 100)  # Cap Unit 축 보호캡 체결 Torque 설정값

    data[30:60] = [ord(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')) for _ in range(30)]
    data[60:90] = [ord(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')) for _ in range(30)]
    
    for i in range(90, 95):  # [A] Port 가스 종류
        data[i] = random.randint(1, 10)
    for i in range(95, 100):  # [B] Port 가스 종류
        data[i] = random.randint(1, 10)

    return data

def generate_bit_data() -> list:
    """Generate bit data for PLC Bit area based on the provided Modbus addresses and bit indices."""
    bit_data = []
    word_dict = {
        100: [
            (0, "EMG Signal"),
            (1, "Heart Bit"),
            (2, "Run/Stop Signal"),
            (3, "Server Connected Bit"),
            (4, "T-LAMP RED"),
            (5, "T-LAMP YELLOW"),
            (6, "T-LAMP GREEN"),
            (7, "Touch 수동동작中 Signal")
        ],
        105: [
            (0, "[A] Port 실린더 유무"),
            (1, "[B] Port 실린더 유무"),
            (2, "[A] Worker Door Open"),
            (3, "[A] Worker Door Close"),
            (4, "[A] Bunker Door Open"),
            (5, "[A] Bunker Door Close"),
            (6, "[B] Worker Door Open"),
            (7, "[B] Worker Door Close"),
            (8, "[B] Bunker Door Open"),
            (9, "[B] Bunker Door Close")
        ],
        110: [
            (0, "[A] Port 보호캡 분리 완료"),
            (1, "[A] Port 보호캡 체결 완료"),
            (2, "[A] Worker Door Open 완료"),
            (3, "[A] Worker Door Close 완료"),
            (4, "[A] Worker 투입 Ready"),
            (5, "[A] Worker 투입 Complete"),
            (6, "[A] Worker 배출 Ready"),
            (7, "[A] Worker 배출 Complete"),
            (8, "[A] Bunker Door Open 완료"),
            (9, "[A] Bunker Door Close 완료"),
            (10, "[A] Bunker 투입 Ready"),
            (11, "[A] Bunker 투입 Complete"),
            (12, "[A] Bunker 배출 Ready"),
            (13, "[A] Bunker 배출 Complete"),
            (14, "[A] Cylinder Align 진행중"),
            (15, "[A] Cylinder Align 완료")
        ],
        111: [
            (0, "[A] Cap Open 진행중"),
            (1, "[A] Cap Close 진행중"),
            (2, "[A] Cylinder 위치로 X축 이동중"),
            (3, "[A] Cylinder 위치로 X축 이동완료"),
            (4, "[A] Cap 위치 찾는중"),
            (5, "[A] Cylinder Neck 위치 찾는중"),
            (6, "[A] Worker door Open 진행중"),
            (7, "[A] Worker door Close 진행중"),
            (8, "[A] Bunker door Open 진행중"),
            (9, "[A] Bunker door Close 진행중")
        ],
        115: [
            (0, "[B] Port 보호캡 분리 완료"),
            (1, "[B] Port 보호캡 체결 완료"),
            (2, "[B] Worker Door Open 완료"),
            (3, "[B] Worker Door Close 완료"),
            (4, "[B] Worker 투입 Ready"),
            (5, "[B] Worker 투입 Complete"),
            (6, "[B] Worker 배출 Ready"),
            (7, "[B] Worker 배출 Complete"),
            (8, "[B] Bunker Door Open 완료"),
            (9, "[B] Bunker Door Close 완료"),
            (10, "[B] Bunker 투입 Ready"),
            (11, "[B] Bunker 투입 Complete"),
            (12, "[B] Bunker 배출 Ready"),
            (13, "[B] Bunker 배출 Complete"),
            (14, "[B] Cylinder Align 진행중"),
            (15, "[B] Cylinder Align 완료")
        ],
        116: [
            (0, "[B] Cap Open 진행중"),
            (1, "[B] Cap Close 진행중"),
            (2, "[B] Cylinder 위치로 X축 이동중"),
            (3, "[B] Cylinder 위치로 X축 이동완료"),
            (4, "[B] Cap 위치 찾는중"),
            (5, "[B] Cylinder Neck 위치 찾는중"),
            (6, "[B] Worker door Open 진행중"),
            (7, "[B] Worker door Close 진행중"),
            (8, "[B] Bunker door Open 진행중"),
            (9, "[B] Bunker door Close 진행중")
        ]
    }

    for address, bits in word_dict.items():
        word = 0
        for bit, description in bits:
            bit_value = random.choice([0, 1])
            word |= bit_value << bit
        bit_data.append(word)

    return bit_data

async def run_client():
    client = None
    try:
        client = AsyncModbusTcpClient('127.0.0.1', port=5020)  # 'unit' 인자 제거
        connected = await client.connect()
        if not connected:
            logger.error("Server connection failed!")
            return

        logger.info("Server connection successful!")

        while True:
            try:
                # Generate and combine data
                plc_data = generate_plc_data()
                bit_data = generate_bit_data()

                # Combine register data and bit_data
                combined_data = plc_data + bit_data
                logger.info("=== Generated Stocker Data ===")
                logger.info(f"Bunker ID: {combined_data[0]}")
                logger.info(f"Stocker ID: {combined_data[1]}")

                # Send bit data using write_coils 
                BLOCK_SIZE = 50
                for i in range(0, len(bit_data), BLOCK_SIZE):
                    block = bit_data[i:i + BLOCK_SIZE]
                    response = await client.read_coils(address=i, values=block, unit=1)  # 'unit' 인자 명시
                    if not response.isError():
                        logger.info(f"Block {i} bit data transmission successful")
                    else:
                        logger.error(f"Block {i} bit data transmission failed: {response}")
                logger.info("Bit data transmission successful")

                # Send register data using write_registers 
                for i in range(0, len(plc_data), BLOCK_SIZE):
                    block = plc_data[i:i + BLOCK_SIZE]
                    response = await client.write_registers(address=i, values=block, unit=1)  # 'unit' 인자 명시
                    if not response.isError():
                        logger.info(f"Block {i} register data transmission successful")
                    else:
                        logger.error(f"Block {i} register data transmission failed: {response}")
                logger.info("Register data transmission successful")

                # Wait before sending the next set of data
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                logger.info("Operation cancelled.")
                break
            except Exception as e:
                logger.error(f"Data transmission error: {e}")
                break
    except Exception as e:
        logger.error(f"Connection error: {e}")
    finally:
        if client:
            await client.close()  # 'await' 키워드 사용
            logger.info("Client connection closed.")

if __name__ == "__main__":
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        logger.info("사용자가 프로그램을 중단했습니다.")
    except Exception as e:
        logger.error(f"프로그램 실행 중 오류 발생: {e}")
