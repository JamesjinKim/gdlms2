import random

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

# 예시로 데이터를 출력합니다.
if __name__ == "__main__":
    data = generate_bit_data()
    address_list = [100, 105, 110, 111, 115, 116]
    for i, word in enumerate(data):
        current_address = address_list[i]
        print(f"\nWord {current_address}:")
        if current_address == 100:
            bits = [
                "EMG Signal", "Heart Bit", "Run/Stop Signal", "Server Connected Bit",
                "T-LAMP RED", "T-LAMP YELLOW", "T-LAMP GREEN", "Touch 수동동작中 Signal"
            ]
        elif current_address == 105:
            bits = [
                "[A] Port 실린더 유무", "[B] Port 실린더 유무",
                "[A] Worker Door Open", "[A] Worker Door Close",
                "[A] Bunker Door Open", "[A] Bunker Door Close",
                "[B] Worker Door Open", "[B] Worker Door Close",
                "[B] Bunker Door Open", "[B] Bunker Door Close"
            ]
        elif current_address == 110:
            bits = [
                "[A] Port 보호캡 분리 완료", "[A] Port 보호캡 체결 완료",
                "[A] Worker Door Open 완료", "[A] Worker Door Close 완료",
                "[A] Worker 투입 Ready", "[A] Worker 투입 Complete",
                "[A] Worker 배출 Ready", "[A] Worker 배출 Complete",
                "[A] Bunker Door Open 완료", "[A] Bunker Door Close 완료",
                "[A] Bunker 투입 Ready", "[A] Bunker 투입 Complete",
                "[A] Bunker 배출 Ready", "[A] Bunker 배출 Complete",
                "[A] Cylinder Align 진행중", "[A] Cylinder Align 완료"
            ]
        elif current_address == 111:
            bits = [
                "[A] Cap Open 진행중", "[A] Cap Close 진행중",
                "[A] Cylinder 위치로 X축 이동중", "[A] Cylinder 위치로 X축 이동완료",
                "[A] Cap 위치 찾는중", "[A] Cylinder Neck 위치 찾는중",
                "[A] Worker door Open 진행중", "[A] Worker door Close 진행중",
                "[A] Bunker door Open 진행중", "[A] Bunker door Close 진행중"
            ]
        elif current_address == 115:
            bits = [
                "[B] Port 보호캡 분리 완료", "[B] Port 보호캡 체결 완료",
                "[B] Worker Door Open 완료", "[B] Worker Door Close 완료",
                "[B] Worker 투입 Ready", "[B] Worker 투입 Complete",
                "[B] Worker 배출 Ready", "[B] Worker 배출 Complete",
                "[B] Bunker Door Open 완료", "[B] Bunker Door Close 완료",
                "[B] Bunker 투입 Ready", "[B] Bunker 투입 Complete",
                "[B] Bunker 배출 Ready", "[B] Bunker 배출 Complete",
                "[B] Cylinder Align 진행중", "[B] Cylinder Align 완료"
            ]
        elif current_address == 116:
            bits = [
                "[B] Cap Open 진행중", "[B] Cap Close 진행중",
                "[B] Cylinder 위치로 X축 이동중", "[B] Cylinder 위치로 X축 이동완료",
                "[B] Cap 위치 찾는중", "[B] Cylinder Neck 위치 찾는중",
                "[B] Worker door Open 진행중", "[B] Worker door Close 진행중",
                "[B] Bunker door Open 진행중", "[B] Bunker door Close 진행중"
            ]
        for j, bit_name in enumerate(bits):
            bit_value = bool((word >> j) & 1)
            print(f"  {bit_name}: {bit_value}")