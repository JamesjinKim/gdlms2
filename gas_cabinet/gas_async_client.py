from pymodbus.client import AsyncModbusTcpClient
import random
import asyncio
import logging
import signal

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s %(message)s',
    level=logging.INFO,
)

def generate_plc_data():
    """PLC 데이터 생성 함수 - 모든 값을 0-255 범위로 제한"""
    data = []

    # Basic Information (0-6)
    data.append(1)  # Bunker ID (0)
    data.append(random.randint(1, 26))  # Gas Cabinet ID (1)
    data.extend([random.randint(1, 50) for _ in range(5)])  # Gas Type (2-6)

    # Empty space (7-16)
    data.extend([0 for _ in range(10)])  # 주석 해제

    # Pressure Sensors (17-24)
    for _ in range(8):  # PT1A - WB
        data.append(random.randint(0, 255))

    # Heater Values (25-28)
    for _ in range(4):
        data.append(random.randint(0, 100))

    # Status Codes (29-30)
    data.append(random.randint(0, 22))  # Machine Code
    data.append(random.randint(0, 22))  # Alarm Code

    # Empty space (31-39)
    data.extend([0 for _ in range(9)])  # 주석 해제

    # A Port CGA Torque Data (40-43)
    for _ in range(4):
        data.append(random.randint(0, 100))

    # Empty space (44)
    data.append(0)  # 주석 해제

    # A Port Cylinder Position Data (45-47)
    for _ in range(3):
        data.append(random.randint(0, 255))

    # Empty space (48-49)
    data.extend([0 for _ in range(2)])  # 주석 해제

    # A Port Cylinder Barcode Data (50-79)
    data.extend([random.randint(0, 255) for _ in range(30)])

    # Empty space (80-99)
    data.extend([0 for _ in range(20)])  # 주석 해제

    # B Port CGA Torque Data (100-103)
    for _ in range(4):
        data.append(random.randint(0, 100))

    # Empty space (104)
    data.append(0)  # 주석 해제

    # B Port Cylinder Position Data (105-107)
    for _ in range(3):
        data.append(random.randint(0, 255))

    # Empty space (108-109)
    data.extend([0 for _ in range(2)])  # 주석 해제

    # B Port Cylinder Barcode Data (110-139)
    data.extend([random.randint(0, 255) for _ in range(30)])

    # 데이터 길이 확인
    if len(data) != 140:
        print(f"Warning: 잘못된 데이터 길이: {len(data)}")
    
    return data

def generate_bit_data():
    """PLC Bit area 데이터 생성 함수"""
    bit_data = []

    # 200.00 - 200.09 (기본 상태 비트)
    word_200 = 0
    word_200 |= random.choice([0, 1]) << 0  # EMG Signal
    word_200 |= random.choice([0, 1]) << 1  # Heart Bit
    word_200 |= random.choice([0, 1]) << 2  # Run/Stop Signal
    word_200 |= random.choice([0, 1]) << 3  # Server Connected Bit
    word_200 |= random.choice([0, 1]) << 4  # A Port 실린더 유무
    word_200 |= random.choice([0, 1]) << 5  # B Port 실린더 유무
    word_200 |= random.choice([0, 1]) << 6  # [A] Touch 수동동작中 Signal
    word_200 |= random.choice([0, 1]) << 7  # [B] Touch 수동동작中 Signal
    word_200 |= random.choice([0, 1]) << 8  # Door Open 완료
    word_200 |= random.choice([0, 1]) << 9  # Door Close 완료
    bit_data.append(word_200)

    # 201.00 - 201.11 (센서 및 릴레이 상태)
    word_201 = 0
    word_201 |= random.choice([0, 1]) << 0  # T-LAMP RED
    word_201 |= random.choice([0, 1]) << 1  # T-LAMP YELLOW
    word_201 |= random.choice([0, 1]) << 2  # T-LAMP GREEN
    word_201 |= random.choice([0, 1]) << 3  # JACKET HEATER A RELAY
    word_201 |= random.choice([0, 1]) << 4  # LINE HEATER A RELAY
    word_201 |= random.choice([0, 1]) << 5  # JACKET HEATER B RELAY
    word_201 |= random.choice([0, 1]) << 6  # LINE HEATER B RELAY
    word_201 |= random.choice([0, 1]) << 7  # GAS LEAK SHUT DOWN
    word_201 |= random.choice([0, 1]) << 8  # VMB STOP SIGNAL
    word_201 |= random.choice([0, 1]) << 9  # UV/IR SENSOR
    word_201 |= random.choice([0, 1]) << 10  # HIGH TEMP SENSOR
    word_201 |= random.choice([0, 1]) << 11  # SMOKE SENSOR
    bit_data.append(word_201)

    # 210.00 - 210.12 ([A] Port 진행 상태)
    word_210 = 0
    for i in range(13):  # 13개 비트 사용
        word_210 |= random.choice([0, 1]) << i
    bit_data.append(word_210)

    # 211.00 - 211.04 (AV1A-AV5A 밸브 상태)
    word_211 = 0
    for i in range(5):  # 5개 비트 사용
        word_211 |= random.choice([0, 1]) << i
    bit_data.append(word_211)

    # 215.00 - 215.15 ([A] Port 상세 상태)
    word_215 = 0
    for i in range(16):  # 16개 비트 모두 사용
        word_215 |= random.choice([0, 1]) << i
    bit_data.append(word_215)

    # 216.00 - 216.06 ([A] Port 추가 상태)
    word_216 = 0
    for i in range(7):  # 7개 비트 사용
        word_216 |= random.choice([0, 1]) << i
    bit_data.append(word_216)

    # 220.00 - 220.12 ([B] Port 진행 상태)
    word_220 = 0
    for i in range(13):  # 13개 비트 사용
        word_220 |= random.choice([0, 1]) << i
    bit_data.append(word_220)

    # 221.00 - 221.15 (B Port 밸브 상태)
    word_221 = 0
    # AV1B-AV5B (0-4)
    for i in range(5):
        word_221 |= random.choice([0, 1]) << i
    # AV7-AV9 (13-15)
    for i in range(13, 16):
        word_221 |= random.choice([0, 1]) << i
    bit_data.append(word_221)

    # 225.00 - 225.15 ([B] Port 상세 상태)
    word_225 = 0
    for i in range(16):  # 16개 비트 모두 사용
        word_225 |= random.choice([0, 1]) << i
    bit_data.append(word_225)

    # 226.00 - 226.06 ([B] Port 추가 상태)
    word_226 = 0
    for i in range(7):  # 7개 비트 사용
        word_226 |= random.choice([0, 1]) << i
    bit_data.append(word_226)

    return bit_data

async def run_client():
    # 클라이언트 설정
    client = None
    loop = asyncio.get_running_loop()
    should_exit = asyncio.Event()

    async def read_time_sync_data():
        """시간 동기화 데이터 읽기"""
        try:
            if client and client.connected:
                # 주소 0-5에서 시간 데이터 읽기
                result = await client.read_holding_registers(
                    address=0,
                    count=6,
                    slave=1
                )
                if result and not result.isError():
                    time_data = result.registers
                    print("\n=== 수신된 시간 동기화 데이터 ===")
                    print(f"날짜: {time_data[0]:04d}년 {time_data[1]:02d}월 {time_data[2]:02d}일")
                    print(f"시간: {time_data[3]:02d}시 {time_data[4]:02d}분 {time_data[5]:02d}초")
                    return time_data
        except Exception as e:
            print(f"시간 동기화 데이터 읽기 오류: {e}")
        return None
    
    async def connect_client():
        nonlocal client
        try:
            if client is None or not client.connected:
                print("\n=== Modbus TCP 클라이언트 연결 시도 ===")
                client = AsyncModbusTcpClient('127.0.0.1', port=5020)
                connected = await client.connect()
                if connected:
                    print("서버 연결 성공!")
                    # 연결 직후 시간 동기화 데이터 읽기
                    await read_time_sync_data()
                else:
                    print("서버 연결 실패!")
                return connected
            return client.connected
        except Exception as e:
            print(f"연결 오류: {e}")
            return False

    async def send_data():
        if not await connect_client():
            print("서버에 연결할 수 없습니다. 재시도 중...")
            return
                
        try:
            # 시간 동기화 데이터 읽기
            await read_time_sync_data()

            # Data area (0-199) 데이터 전송
            data = generate_plc_data()
            print("\n=== 생성된 PLC 데이터 ===")  # 추가
            print(f"Bunker ID: {data[0]}")      # 추가
            print(f"Cabinet ID: {data[1]}")     # 추가
            #print(f"첫 10개 값: {data[:10]}")
            
            # 각 레지스터를 개별적으로 전송
            for i, value in enumerate(data):
                try:
                    if client and client.connected:
                        result = await client.write_register(
                            address=i,
                            value=value,
                            slave=1
                        )
                        if result and hasattr(result, 'isError') and result.isError():
                            print(f"데이터 전송 실패: address={i}, value={value}")
                    else:
                        print("클라이언트 연결이 끊어졌습니다.")
                        break
                except Exception as e:
                    print(f"레지스터 쓰기 오류 - address={i}: {e}")

            # Bit area (200-226) 데이터 전송
            bit_data = generate_bit_data()
            print(f"\n=== 생성된 Bit 데이터 ===")
            print(f"Bit data length: {len(bit_data)}")
            
            # 각 비트 데이터를 개별적으로 전송
            for i, value in enumerate(bit_data):
                try:
                    if client and client.connected:
                        result = await client.write_register(
                            address=200 + i,
                            value=value,
                            slave=1
                        )
                        if result and hasattr(result, 'isError') and result.isError():
                            print(f"비트 데이터 전송 실패: address={200+i}, value={value}")
                    else:
                        print("클라이언트 연결이 끊어졌습니다.")
                        break
                except Exception as e:
                    print(f"비트 레지스터 쓰기 오류 - address={200+i}: {e}")

        except Exception as e:
            print(f"데이터 전송 중 오류 발생: {e}")

    async def client_loop():
        try:
            while not should_exit.is_set():
                await send_data()
                await asyncio.sleep(5)
        except asyncio.CancelledError:
            print("클라이언트 루프가 취소되었습니다.")
        except Exception as e:
            print(f"클라이언트 루프 오류: {e}")

    def signal_handler():
        print("\n프로그램 종료 시작...")
        should_exit.set()
        for task in asyncio.all_tasks(loop):
            if task is not asyncio.current_task():
                task.cancel()

    try:
        loop.add_signal_handler(signal.SIGINT, signal_handler)
        print("\n=== Modbus TCP 클라이언트 시작 ===")
        await client_loop()
    except asyncio.CancelledError:
        print("프로그램이 취소되었습니다.")
    except Exception as e:
        print(f"예기치 않은 오류: {e}")
    finally:
        # 클라이언트 종료 부분 수정
        if client and hasattr(client, 'connected'):
            try:
                if client.connected:
                    await client.close()
                    print("클라이언트 연결 종료 완료")
                else:
                    print("클라이언트가 이미 연결 해제된 상태입니다.")
            except Exception as e:
                print(f"클라이언트 종료 중 오류 발생: {e}")
        else:
            print("클라이언트가 초기화되지 않았거나 이미 종료되었습니다.")
        print("클라이언트 프로그램 종료")


if __name__ == "__main__":
    try:
        asyncio.run(run_client())
    except KeyboardInterrupt:
        #pass
        print("\n사용자가 프로그램을 중단했습니다.")
    except Exception as e:
        print(f"\n예기치 않은 오류 발생: {e}")