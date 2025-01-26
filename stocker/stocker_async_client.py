from pymodbus.client import AsyncModbusTcpClient
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
    bit_data = []
    
    # Word 100 (Basic signals)
    word_100 = (1 << 3)  # Server Connected Bit
    word_100 |= (1 << 0)  # EMG Signal
    word_100 |= (1 << 1)  # Heart Bit
    word_100 |= (1 << 2)  # Run/Stop Signal
    bit_data.append(word_100)

    # Word 101-104 (Empty)
    bit_data.extend([0] * 4)

    # Word 105 (Door status)
    word_105 = 0b1111111111  # All 10 bits True
    bit_data.append(word_105)

    # Word 106-109 (Empty)
    bit_data.extend([0] * 4)

    # Word 110 (A Port status)
    word_110 = 0b1111111111111111  # All 16 bits True
    bit_data.append(word_110)

    # Word 111 (A Port detailed status)
    word_111 = 0b1111111111  # All 10 bits True
    bit_data.append(word_111)

    # Word 112-114 (Empty)
    bit_data.extend([0] * 3)

    # Word 115 (B Port status)
    word_115 = 0b1111111111111111  # All 16 bits True
    bit_data.append(word_115)

    # Word 116 (B Port detailed status)
    word_116 = 0b1111111111  # All 10 bits True
    bit_data.append(word_116)
   
    return bit_data

async def run_client():
    client = None
    try:
        client = AsyncModbusTcpClient('127.0.0.1', port=5020)
        await client.connect()
        logger.info("서버 연결 성공!")

        while True:
            try:
                # Generate and combine data
                register_data = generate_plc_data()
                bit_data = generate_bit_data()

                # Combine register data and bit data
                combined_data = register_data + bit_data
                logger.info("=== 생성된 Stocker 데이터 ===")
                logger.info(f"Bunker ID: {combined_data[0]}")
                logger.info(f"Stocker ID: {combined_data[1]}")

                # Send data in blocks
                BLOCK_SIZE = 50
                for i in range(0, len(combined_data), BLOCK_SIZE):
                    block = combined_data[i:i + BLOCK_SIZE]
                    await client.write_registers(address=i, values=block, slave=1)
                logger.info("데이터 전송 성공")

                # Wait before sending the next set of data
                await asyncio.sleep(5)
            except asyncio.CancelledError:
                logger.info("작업이 취소되었습니다.")
                break
            except Exception as e:
                logger.error(f"데이터 전송 중 오류 발생: {e}")
                break

    except Exception as e:
        logger.error(f"연결 오류: {e}")
    finally:
        if client and client.connected:
            await client.close()
        logger.info("클라이언트 연결 종료 완료")

if __name__ == "__main__":
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        logger.info("사용자가 프로그램을 중단했습니다.")
