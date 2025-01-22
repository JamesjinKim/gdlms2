from enum import Enum


class StockerAlarmCode(Enum):
    # Emergency & Safety
    EMERGENCY_BUTTON = 1
    DOOR_OPEN = 2
    MAIN_AIR_OFF = 3
    MAIN_MC_OFF = 4

    # Motor Faults (0-9 Axis)
    MOTOR_X_AXIS_FAULT = 5
    MOTOR_Z_AXIS_FAULT = 6
    MOTOR_REMOVE_TURN_FAULT = 7
    MOTOR_GRIPPER_TURN_FAULT = 8
    MOTOR_LEFT_DOOR_FAULT = 9
    MOTOR_RIGHT_DOOR_FAULT = 10
    MOTOR_UNDEFINED_1_FAULT = 11
    MOTOR_UNDEFINED_2_FAULT = 12
    MOTOR_UNDEFINED_3_FAULT = 13
    MOTOR_UNDEFINED_4_FAULT = 14

    # Initialization Errors
    INIT_INCOMPLETE = 15
    INIT_Z_AXIS_HOME_FAIL = 16
    INIT_X_AXIS_HOME_FAIL = 17

    # Cap Unscrew Errors (18-28)
    CAP_UNSCREW_DETECT_ERROR = 18
    CAP_UNSCREW_Z_AXIS_SAFETY_ERROR = 19
    CAP_UNSCREW_X_AXIS_BARREL_ERROR = 20
    CAP_UNSCREW_BARREL_DETECT_ERROR = 21
    CAP_UNSCREW_TOP_SEARCH_ERROR = 22
    CAP_UNSCREW_Z_AXIS_READY_ERROR = 23
    CAP_UNSCREW_Z_AXIS_INSERT_ERROR = 24
    CAP_UNSCREW_ROTATOR_TORQUE_ERROR = 25
    CAP_UNSCREW_Z_AXIS_SEPARATE_ERROR = 26
    RESERVED_27 = 27
    RESERVED_28 = 28


    # Cap Screw Errors (29-50)
    CAP_SCREW_GRIPPER_ERROR = 29
    CAP_SCREW_Z_AXIS_SAFETY_ERROR = 30
    CAP_SCREW_X_AXIS_BARREL_ERROR = 31
    CAP_SCREW_BARREL_DETECT_ERROR = 32
    CAP_SCREW_Z_AXIS_READY_ERROR = 33
    CAP_SCREW_BARREL_NECK_ERROR = 34
    CAP_SCREW_Z_AXIS_INSERT_ERROR = 35
    CAP_SCREW_ROTATOR_TORQUE_ERROR = 36
    CAP_SCREW_Z_AXIS_SAFETY_ERROR_2 = 37


    # Reserved (38-51)
    RESERVED_38 = 38
    RESERVED_39 = 39
    RESERVED_40 = 40
    RESERVED_41 = 41
    RESERVED_42 = 42
    RESERVED_43 = 43
    RESERVED_44 = 44
    RESERVED_45 = 45
    RESERVED_46 = 46
    RESERVED_47 = 47
    RESERVED_48 = 48
    RESERVED_49 = 49
    RESERVED_50 = 50
    RESERVED_51 = 51


    # RGV Errors (52-59)
    RGV_LD_BARREL_EXIST_ERROR = 52
    RGV_LD_DOOR_OPEN_ERROR = 53
    RGV_LD_BARREL_DETECT_ERROR = 54
    RGV_LD_DOOR_CLOSE_ERROR = 55
    RGV_ULD_BARREL_EXIST_ERROR = 56
    RGV_ULD_DOOR_OPEN_ERROR = 57
    RGV_ULD_BARREL_DETECT_ERROR = 58
    RGV_ULD_DOOR_CLOSE_ERROR = 59


    # Barrel Align Error (60)
    BARREL_ALIGN_ROTATE_ERROR = 60


    # Reserved (61-73)
    RESERVED_61 = 61
    RESERVED_62 = 62
    RESERVED_63 = 63
    RESERVED_64 = 64
    RESERVED_65 = 65
    RESERVED_66 = 66
    RESERVED_67 = 67
    RESERVED_68 = 68
    RESERVED_69 = 69
    RESERVED_70 = 70
    RESERVED_71 = 71
    RESERVED_72 = 72
    RESERVED_73 = 73


    # Sensor and Switch Errors (74-169)
    BUNKER_EMS_ERROR = 74
    BUNKER_MODE_SWITCH_WORKER_ERROR = 75
    BUNKER_MODE_SWITCH_REAR_ERROR = 76
    BUNKER_OPEN_SWITCH_ERROR = 77
    BUNKER_CLOSE_SWITCH_ERROR = 78
    BUNKER_S_RESET_SWITCH_ERROR = 79
    BUNKER_BUZZER_OFF_SWITCH_ERROR = 80
    WORKER_EMS_ERROR = 81
    WORKER_MODE_SWITCH_FRONT_ERROR = 82
    WORKER_MODE_SWITCH_BUNKER_ERROR = 83
    WORKER_OPEN_SWITCH_ERROR = 84
    WORKER_CLOSE_SWITCH_ERROR = 85
    WORKER_S_RESET_SWITCH_ERROR = 86
    WORKER_BUZZER_OFF_SWITCH_ERROR = 87
    NA_88 = 88
    NA_89 = 89
    SMOKE_SENSOR_ERROR = 90
    REGULATOR_SENSOR_ERROR = 91
    MC_ON_ERROR = 92
    SAFETY_UNIT_ERROR = 93
    FROM_PIO_SIGNAL1_ERROR = 94
    FROM_PIO_SIGNAL2_ERROR = 95
    FROM_PIO_SIGNAL3_ERROR = 96
    FROM_PIO_SIGNAL4_ERROR = 97
    FROM_PIO_SIGNAL5_ERROR = 98
    FROM_PIO_SIGNAL6_ERROR = 99
    FROM_PIO_SIGNAL7_ERROR = 100
    FROM_PIO_SIGNAL8_ERROR = 101
    FROM_PIO_SIGNAL9_ERROR = 102
    NA_103 = 103
    NA_104 = 104
    NA_105 = 105
    WORKER_LD_DR_OP_STATUS_ERROR = 106
    WORKER_LD_DR_CL_STATUS_ERROR = 107
    WORKER_ULD_DR_OP_STATUS_ERROR = 108
    WORKER_ULD_DR_CL_STATUS_ERROR = 109
    BUNKER_LD_DR_OP_STATUS_ERROR = 110
    BUNKER_LD_DR_CL_STATUS_ERROR = 111
    BUNKER_ULD_DR_OP_STATUS_ERROR = 112
    BUNKER_ULD_DR_CL_STATUS_ERROR = 113
    NA_114_TO_121 = 114
    BUNKER_LD_DOOR_HEAD_CYL_FWD_ERROR = 122
    BUNKER_LD_DOOR_HEAD_CYL_BWD_ERROR = 123
    BUNKER_ULD_DOOR_HEAD_CYL_FWD_ERROR = 124
    BUNKER_ULD_DOOR_HEAD_CYL_BWD_ERROR = 125
    BUNKER_LD_DOOR_LEFT_BOT_CYL_FWD_ERROR = 126
    BUNKER_LD_DOOR_LEFT_BOT_CYL_BWD_ERROR = 127
    BUNKER_LD_DOOR_RIGHT_BOT_CYL_FWD_ERROR = 128
    BUNKER_LD_DOOR_RIGHT_BOT_CYL_BWD_ERROR = 129
    BUNKER_ULD_DOOR_LEFT_BOT_CYL_FWD_ERROR = 130
    BUNKER_ULD_DOOR_LEFT_BOT_CYL_BWD_ERROR = 131
    BUNKER_ULD_DOOR_RIGHT_BOT_CYL_FWD_ERROR = 132
    BUNKER_ULD_DOOR_RIGHT_BOT_CYL_BWD_ERROR = 133
    NA_134_TO_137 = 134
    LD_LEFT_GRIPPER_CYL_FWD_ERROR = 138
    LD_LEFT_GRIPPER_CYL_BWD_ERROR = 139
    LD_RIGHT_GRIPPER_CYL_FWD_ERROR = 140
    LD_RIGHT_GRIPPER_CYL_BWD_ERROR = 141
    GRIPPER_UNIT_GUIDE_BAR_CYL_FWD_ERROR = 142
    GRIPPER_UNIT_GUIDE_BAR_CYL_BWD_ERROR = 143
    LD_TURN_TABLE_CYL_1_LOCK_ERROR = 144
    LD_TURN_TABLE_CYL_1_UNLOCK_ERROR = 145
    LD_TURN_TABLE_CYL_2_LOCK_ERROR = 146
    LD_TURN_TABLE_CYL_2_UNLOCK_ERROR = 147
    GRIPPER_GAS_CYL_ERROR = 148
    NA_149_TO_153 = 149
    FRONT_CAP_GRIP_GUIDE_CYL_FWD_ERROR = 154
    FRONT_CAP_GRIP_GUIDE_CYL_BWD_ERROR = 155
    REAR_CAP_GRIP_GUIDE_CYL_FWD_ERROR = 156
    REAR_CAP_GRIP_GUIDE_CYL_BWD_ERROR = 157
    CAP_OPEN_CLOSE_CYL_UP_ERROR = 158
    CAP_OPEN_CLOSE_CYL_DOWN_ERROR = 159
    UNIT_FRONT_CAP_ERROR = 160
    UNIT_FRONT_NECKRING_EDGE_ERROR = 161
    VISION_UNIT_CYL_UP_ERROR = 162
    VISION_UNIT_CYL_DOWN_ERROR = 163
    NA_164_TO_169 = 164


    @classmethod
    def get_description(cls, code):
        """알람 코드에 대한 설명을 반환"""
        alarm_descriptions = {
            1: "Emergency 버튼이 동작",
            2: "Door 열림 감지",
            3: "Main Air OFF 감지",
            4: "Main MC OFF 감지",
            5: "Motor # 0축 (X) Amp Fault Alarm",
            6: "Motor # 1축 (Z) Amp Fault Alarm",
            7: "Motor # 2축 (Remove Turn) Amp Fault Alarm",
            8: "Motor # 3축 (Gripper Turn) Amp Fault Alarm",
            9: "Motor # 4축 (Left Door) Amp Fault Alarm",
            10: "Motor # 5축 (Right Door) Amp Fault Alarm",
            11: "Motor # 6축 (미정의) Amp Fault Alarm",
            12: "Motor # 7축 (미정의) Amp Fault Alarm",
            13: "Motor # 8축 (미정의) Amp Fault Alarm",
            14: "Motor # 9축 (미정의) Amp Fault Alarm",
            15: "초기화가 정상적으로 완료되지 않음",
            16: "초기화: Z 축 Home Check 이동 실패",
            17: "초기화: X 축 Home Check 이동 실패",
            18: "Front Cap Gripper에 Cap 분리중 Cap이 감지됨 이상",
            19: "모터 #2 Axis(Z)이 Cap 분리중 Safety 위치로 상승 이상",
            20: "모터 #1 Axis(X)이 Cap 분리중 Barrel (LD) 위치로 이동 이상",
            21: "Cap 분리중 Barrel이 감지 불가 이상",
            22: "Cap 분리중 Cap의 Top 위치 찾기 실패",
            23: "모터 #2 Axis(Z)이 Cap 분리 준비 위치로 하강 이상",
            24: "모터 #2 Axis(Z)이 Cap 분리 너트 체결위치로 하강 이상",
            25: "모터 #3 Axis(Rotator)이 Cap 분리 Cap 열기시작 토크에 도달하지 못함",
            26: "모터 #2 Axis(Z)이 Cap 분리 분리위치로 상승 이상",
            29: "Cap 체결 중 Gripper에 Cap 감지 이상",
            30: "모터 #2 Axis(Z)이 Safety 위치로 상승 이상",
            31: "모터 #1 Axis(X)이 Barrel (LD) 위치로 이동 이상",
            32: "Cap 체결중 Barrel이 감지 불가 이상",
            33: "모터 #2 Axis(Z)이 Cap 체결 준비 위치로 하강 이상",
            34: "모터 #2 Axis(Z)이 Cap 체결중 Barrel Neck 감지 불가 이상",
            35: "모터 #2 Axis(Z)이 Cap 체결 위치로 하강 이상",
            36: "모터 #3 Axis(Rotator)이 Cap 체결 Cap의 닫기 토크에 도달하지 못함",
            37: "모터 #2 Axis(Z)이 Cap 체결 Safety 위치로 상승 이상",
            52: "Rgv LD BarrelExist Check 중 Barrel 감지",
            53: "Rgv LD Door Open Check 동작 중 LD Door Open 이상 감지",
            54: "Rgv LD BarrelDetected Check 중 Barrel 미감지",
            55: "Rgv LD Door Close check 동작 중 LD Door Close 이상 감지",
            56: "Rgv ULD BarrelExist Check 중 Barrel 감지",
            57: "Rgv ULD Door Open Check 동작 중 LD Door Open 이상 감지",
            58: "Rgv ULD BarrelDetected Check 중 Barrel 미감지",
            59: "Rgv ULD Door Close check 동작 중 LD Door Close 이상 감지",
            60: "Barrel 얼라인 중에 Load 부 얼라인을 위한 회전에 실패",
            74: "BUNKER_EMS_ON_CHK 감지 이상",
            75: "BUNKER_MODE_SWITCH_WORKER_CHK 감지 이상",
            76: "BUNKER_MODE_SWITCH_REAR_CHK 감지 이상",
            77: "BUNKER_OPEN_SWITCH_CHK 감지 이상",
            78: "BUNKER_CLOSE_SWITCH_CHK 감지 이상",
            79: "BUNKER_S_RESET_SWITCH_CHK 감지 이상",
            80: "BUNKER_BUZZER_OFF_SWITCH_CHK 감지 이상",
            81: "WORKER_EMS_ON_CHK 감지 이상",
            82: "WORKER_MODE_SWITCH_FRONT_CHK 감지 이상",
            83: "WORKER_MODE_SWITCH_BUNKER_CHK 감지 이상",
            84: "WORKER_OPEN_SWITCH_CHK 감지 이상",
            85: "WORKER_CLOSE_SWITCH_CHK 감지 이상",
            86: "WORKER_S_RESET_SWITCH_CHK 감지 이상",
            87: "WORKER_BUZZER_OFF_SWITCH_CHK 감지 이상",
            88: "X000E_NA 감지 이상",
            89: "X000F_NA 감지 이상",
            90: "SMOKE_SENSOR_ON_CHK 감지 이상",
            91: "REGULATOR_SENSOR_ON_CHK 감지 이상",
            92: "MC_ON_CHK 감지 이상",
            93: "SAFETY_UNIT_ON_CHK 감지 이상",
            94: "FROM_PIO_SIGNAL1 감지 이상",
            95: "FROM_PIO_SIGNAL2 감지 이상",
            96: "FROM_PIO_SIGNAL3 감지 이상",
            97: "FROM_PIO_SIGNAL4 감지 이상",
            98: "FROM_PIO_SIGNAL5 감지 이상",
            99: "FROM_PIO_SIGNAL6 감지 이상",
            100: "FROM_PIO_SIGNAL7 감지 이상",
            101: "FROM_PIO_SIGNAL8 감지 이상",
            102: "FROM_PIO_SIGNAL9 감지 이상",
            103: "X001D_NA 감지 이상",
            104: "X001E_NA 감지 이상",
            105: "X001F_NA 감지 이상",
            106: "WORKER_LD_DR_OP_STATUS 감지 이상",
            107: "WORKER_LD_DR_CL_STATUS 감지 이상",
            108: "WORKER_ULD_DR_OP_STATUS 감지 이상",
            109: "WORKER_ULD_DR_CL_STATUS 감지 이상",
            110: "BUNKER_LD_DR_OP_STATUS 감지 이상",
            111: "BUNKER_LD_DR_CL_STATUS 감지 이상",
            112: "BUNKER_ULD_DR_OP_STATUS 감지 이상",
            113: "BUNKER_ULD_DR_CL_STATUS 감지 이상",
            114: "X0028_NA 감지 이상",
            115: "X0029_NA 감지 이상",
            116: "X002A_NA 감지 이상",
            117: "X002B_NA 감지 이상",
            118: "X002C_NA 감지 이상",
            119: "X002D_NA 감지 이상",
            120: "X002E_NA 감지 이상",
            121: "X002F_NA 감지 이상",
            122: "BUNKER_LD_DOOR_HEAD_CYL_FWD 감지 이상",
            123: "BUNKER_LD_DOOR_HEAD_CYL_BWD 감지 이상",
            124: "BUNKER_ULD_DOOR_HEAD_CYL_FWD 감지 이상",
            125: "BUNKER_ULD_DOOR_HEAD_CYL_BWD 감지 이상",
            126: "BUNKER_LD_DOOR_LEFT_BOT_CYL_FWD 감지 이상",
            127: "BUNKER_LD_DOOR_LEFT_BOT_CYL_BWD 감지 이상",
            128: "BUNKER_LD_DOOR_RIGHT_BOT_CYL_FWD 감지 이상",
            129: "BUNKER_LD_DOOR_RIGHT_BOT_CYL_BWD 감지 이상",
            130: "BUNKER_ULD_DOOR_LEFT_BOT_CYL_FWD 감지 이상",
            131: "BUNKER_ULD_DOOR_LEFT_BOT_CYL_BWD 감지 이상",
            132: "BUNKER_ULD_DOOR_RIGHT_BOT_CYL_FWD 감지 이상",
            133: "BUNKER_ULD_DOOR_RIGHT_BOT_CYL_BWD 감지 이상",
            134: "X003C_NA 감지 이상",
            135: "X003D_NA 감지 이상",
            136: "X003E_NA 감지 이상",
            137: "X003F_NA 감지 이상",
            138: "LD_LEFT_GRIPPER_CYL_FWD 감지 이상",
            139: "LD_LEFT_GRIPPER_CYL_BWD 감지 이상",
            140: "LD_RIGHT_GRIPPER_CYL_FWD 감지 이상",
            141: "LD_RIGHT_GRIPPER_CYL_BWD 감지 이상",
            142: "GRIPPER_UNIT_GUIDE_BAR_CYL_FWD 감지 이상",
            143: "GRIPPER_UNIT_GUIDE_BAR_CYL_BWD 감지 이상",
            144: "LD_TURN_TABLE_CYL_1_LOCK 감지 이상",
            145: "LD_TURN_TABLE_CYL_1_UNLOCK 감지 이상",
            146: "LD_TURN_TABLE_CYL_2_LOCK 감지 이상",
            147: "LD_TURN_TABLE_CYL_2_UNLOCK 감지 이상",
            148: "GRIPPER_GAS_CYL_CHK 감지 이상",
            149: "X004B_NA 감지 이상",
            150: "X004C_NA 감지 이상",
            151: "X004D_NA 감지 이상",
            152: "X004E_NA 감지 이상",
            153: "X004F_NA 감지 이상",
            154: "FRONT_CAP_GRIP_GUIDE_CYL_FWD 감지 이상",
            155: "FRONT_CAP_GRIP_GUIDE_CYL_BWD 감지 이상",
            156: "REAR_CAP_GRIP_GUIDE_CYL_FWD 감지 이상",
            157: "REAR_CAP_GRIP_GUIDE_CYL_BWD 감지 이상",
            158: "CAP_OPEN_CLOSE_CYL_UP 감지 이상",
            159: "CAP_OPEN_CLOSE_CYL_DOWN 감지 이상",
            160: "UNIT_FRONT_CAP_CHK 감지 이상",
            161: "UNIT_FRONT_NECKRING_EDGE_CHK 감지 이상",
            162: "VISION_UNIT_CYL_UP 감지 이상",
            163: "VISION_UNIT_CYL_DOWN 감지 이상",
            164: "X005A_NA 감지 이상",
            165: "X005B_NA 감지 이상",
            166: "X005C_NA 감지 이상",
            167: "X005D_NA 감지 이상",
            168: "X005E_NA 감지 이상",
            169: "X005F_NA 감지 이상"
            }
        return alarm_descriptions.get(code, f"Unknown Alarm Code: {code}")