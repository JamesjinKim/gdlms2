from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ModbusIOException
import random
import asyncio
import logging
import datetime

logging.basicConfig(
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger("StockerClient")

def generate_plc_data() -> list:
    """Generate random data for registers."""
    data = [0] * 120  # Initialize with zeros, covering all 120 WORDs

    # Fill data with random values as per your specification
    data[0] = random.randint(1, 1)  # Bunker ID
    data[1] = random.randint(1, 1)  # Stocker ID
    for i in range(2, 7):  # Gas Stocker 가스 종류
        data[i] = random.randint(1, 5)
    data[8] = random.randint(0, 500)  # Stocker Alarm Code
    data[10] = random.randint(0, 100)  # X축 현재값
    data[11] = random.randint(0, 100)  # Z축 현재값
    data[12] = random.randint(0, 100)  # Cap Unit 축 보호캡 분리 Torque 설정값
    data[13] = random.randint(0, 100)  # Cap Unit 축 보호캡 체결 Torque 설정값

    data[30:60] = [ord(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')) for _ in range(30)]
    data[60:90] = [ord(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')) for _ in range(30)]
    
    for i in range(90, 95):  # [A] Port 가스 종류
        data[i] = random.randint(1, 5)
    for i in range(95, 100):  # [B] Port 가스 종류
        data[i] = random.randint(1, 5)

    return data

def generate_bit_data() -> list:
    bit_data = []
    word_dict = {
        100: [
            (0, "EMG Signal"), (1, "Heart Bit"), (2, "Run/Stop Signal"),
            (3, "Server Connected Bit"), (4, "T-LAMP RED"), (5, "T-LAMP YELLOW"),
            (6, "T-LAMP GREEN"), (7, "Touch 수동동작中 Signal")
        ],
        105: [
            (0, "[A] Port 실린더 유무"), (1, "[B] Port 실린더 유무"),
            (2, "[A] Worker Door Open"), (3, "[A] Worker Door Close"),
            (4, "[A] Bunker Door Open"), (5, "[A] Bunker Door Close"),
            (6, "[B] Worker Door Open"), (7, "[B] Worker Door Close"),
            (8, "[B] Bunker Door Open"), (9, "[B] Bunker Door Close")
        ],
        110: [(i, f"Signal {i}") for i in range(16)],
        111: [(i, f"Signal {i}") for i in range(10)],
        115: [(i, f"Signal {i}") for i in range(16)],
        116: [(i, f"Signal {i}") for i in range(10)]
    }

    for address in range(100, 118):
        word = 0
        if address in word_dict:
            for bit, _ in word_dict[address]:
                bit_value = random.choice([0, 1])
                word |= bit_value << bit
        else:
            word = random.randint(0, 65535)
        bit_data.append(word)

    return bit_data


async def run_client():
    client = None
    try:
        client = AsyncModbusTcpClient('127.0.0.1', port=5020)
        connected = await client.connect()
        if not connected:
            logger.error("Server connection failed!")
            return
        logger.info("Server connection successful!")

        # 연결 후 바로 서버의 시간 읽기
        time_response = await client.read_holding_registers(0, count=6)
        if not time_response.isError():
            server_time = datetime.datetime(
                year=time_response.registers[0],
                month=time_response.registers[1],
                day=time_response.registers[2],
                hour=time_response.registers[3],
                minute=time_response.registers[4],
                second=time_response.registers[5]
            )
            logger.info(f"서버 시간: {server_time}")

        while True:
            try:
                #PLC 데이터
                plc_data = generate_plc_data()
                #랜덤 비트 데이터 생성
                bit_data = generate_bit_data()
                # Combine register data and bit_data
                combined_data = plc_data + bit_data
                logger.info("\n=== Generated Stocker Data ===")
                logger.info(f"Bunker ID: {combined_data[0]}")
                logger.info(f"Stocker ID: {combined_data[1]}")
                
                # PLC data 전송 (0-99 주소)
                plc_block = plc_data[:100]  # PLC 데이터만 분리
                try:
                    response = await client.write_registers(0, plc_block)
                    if response.isError():
                        logger.error(f"PLC data 전송 실패")
                    else:
                        logger.info(f"PLC data 전송 성공")
                except Exception as e:
                    logger.error(f"PLC data 전송 오류: {e}")

                # Bit data 전송 (100-117 주소)
                for i, word in enumerate(bit_data):
                    try:
                        response = await client.write_register(address=i+100, value=word)
                        if response.isError():
                            logger.error(f"Bit data 전송 실패 (주소 {i+100})")
                        else:
                            logger.info(f"Bit data 전송 성공 (주소 {i+100})")
                    except Exception as e:
                        logger.error(f"Bit data 전송 오류: {e}")

                # 전송한 데이터 확인
                result_word = await client.read_holding_registers(address=0, count=len(plc_data))
                result_bit = await client.read_coils(address=100, count=160)

                if not result_word.isError() and not result_bit.isError():
                    logger.info("전송된 데이터:")
                    logger.info(f"Word data: {result_word.registers}")
                    for i in range(0, 160, 16):
                        word = result_bit.bits[i:i+16]
                        binary = ''.join(['1' if bit else '0' for bit in word])
                        logger.info(f"Bit data (워드 {i//16}): {binary}")
                else:
                    logger.error("데이터 읽기 오류")

                # Add delay to prevent CPU overload
                await asyncio.sleep(1)

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
            await client.close()
            logger.info("Client connection closed.")
         
if __name__ == "__main__":
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        logger.info("사용자가 프로그램을 중단했습니다.")
    except Exception as e:
        logger.error(f"프로그램 실행 중 오류 발생: {e}")
