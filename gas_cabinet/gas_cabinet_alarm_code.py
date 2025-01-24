
class GasCabinetAlarmCode:
    # Common Alarms
    REDUNDANCY_OFF = 1
    EMS_SW_ON = 2
    SAFETY_UNIT_OUT_OFF = 3
    SMOKE_DETECT_ON = 4
    GAS_AIR_PRESSURE_OFF = 5
    AUTO_AIR_PRESSURE_OFF = 6
    DOOR_OPEN_OFF = 7
    AUTO_COUPLER_SYSTEM_EMG = 8
    ARS_RUN_OFF = 9
    UV_IR_ON = 10
    HI_TEMP_ON = 11
    GAS_2ND_LEAK = 12
    CABINET_DOOR_OPEN_SHUTDOWN = 13
    EXHAUST_VELOCITY = 14
    REMOTE_SHUTDOWN = 15
    PT1_HIGH_PRESSURE = 16
    RESERVED_17 = 17
    RESERVED_18 = 18
    RESERVED_19 = 19
    GAS_LEAK_1ST = 20
    EXHAUST_FAIL = 21
    VALVE_LIFETIME_OVER = 22

    # A Port Alarms (101-115)
    A_PORT_RESIDUAL_GAS = 101
    A_PORT_PULSE_VENT = 102
    A_PORT_PULSE_VENT_COUNT_OVER = 103
    A_PORT_LINE_VACUUM_ERROR = 104
    A_PORT_LINE_STATUS_ERROR = 105
    A_PORT_N2_SUPPLY_ERROR = 106
    A_PORT_PT_DECOMPRESSION_TEST_ERROR = 107
    A_PORT_VT_DECOMPRESSION_TEST_ERROR = 108
    A_PORT_AV11_BYPASS = 109
    A_PORT_AV1_BYPASS = 110
    A_PORT_PRESSURIZATION_TEST_ERROR = 111
    A_PORT_PRESSURE_RISE_ERROR = 112
    A_PORT_HIGH_PRESSURE_GAS_LOW = 113
    A_PORT_HIGH_PRESSURE_GAS_HIGH = 114
    A_PORT_NOT_STANDBY = 115
    # A Port Extended Alarms (121-193)
    A_PORT_WEIGHT_OFFSET_ZERO = 121
    A_PORT_GROSS_OFFSET_OVER = 122
    A_PORT_NOT_CHANGE = 123
    A_PORT_PT1_STANDBY_LOW = 131
    A_PORT_SUPPLY_LINE_BYPASS = 133
    A_PORT_MANIFOLD_HEATER_SENSOR_ERROR = 140
    A_PORT_LINE_HEATER_SENSOR_ERROR = 141
    A_PORT_JACKET_HEATER_SENSOR_ERROR = 142
    A_PORT_COOLING_SENSOR_ERROR = 143
    A_PORT_MANIFOLD_HEATER_HIGH_TEMP = 144
    A_PORT_LINE_HEATER_HIGH_TEMP = 145
    A_PORT_JACKET_HEATER_HIGH_TEMP = 146
    A_PORT_MANIFOLD_HEATER_BIMETAL = 147
    A_PORT_LINE_HEATER_BIMETAL = 148
    A_PORT_JACKET_HEATER_BIMETAL = 149
    A_PORT_COOLING_JACKET_HIGH_TEMP_1 = 150
    A_PORT_COOLING_JACKET_HIGH_TEMP_2 = 151
    A_PORT_PT1_HIGH_PRESSURE_2ND = 160
    A_PORT_PT1_HIGH_PRESSURE_1ST = 161
    A_PORT_PT1_LOW_PRESSURE_1ST = 162
    A_PORT_PT1_LOW_PRESSURE_2ND = 163
    A_PORT_PT2_HIGH_PRESSURE_2ND = 164
    A_PORT_PT2_HIGH_PRESSURE_1ST = 165
    A_PORT_PT2_LOW_PRESSURE_1ST = 166
    A_PORT_PT2_LOW_PRESSURE_2ND = 167
    A_PORT_PT3_HIGH_PRESSURE = 168
    A_PORT_PT3_LOW_PRESSURE = 169
    A_PORT_AV1_BYPASS_STATUS = 170
    A_PORT_WEIGHT_OVER = 180
    A_PORT_WEIGHT_ERROR = 181
    A_PORT_WEIGHT_LOW_1ST = 182
    A_PORT_WEIGHT_LOW_2ND = 183
    A_PORT_PT1_NEG_PRESSURE_HIGH = 190
    A_PORT_PT1_NEG_PRESSURE_LOW = 191
    A_PORT_PT2_NEG_PRESSURE_HIGH = 192
    A_PORT_PT2_NEG_PRESSURE_LOW = 193
    # B Port Alarms (201-215)
    B_PORT_RESIDUAL_GAS = 201
    B_PORT_PULSE_VENT = 202
    B_PORT_PULSE_VENT_COUNT_OVER = 203
    B_PORT_LINE_VACUUM_ERROR = 204
    B_PORT_LINE_STATUS_ERROR = 205
    B_PORT_N2_SUPPLY_ERROR = 206
    B_PORT_PT_DECOMPRESSION_TEST_ERROR = 207
    B_PORT_VT_DECOMPRESSION_TEST_ERROR = 208
    B_PORT_AV11_BYPASS = 209
    B_PORT_AV1_BYPASS = 210
    B_PORT_PRESSURIZATION_TEST_ERROR = 211
    B_PORT_PRESSURE_RISE_ERROR = 212
    B_PORT_HIGH_PRESSURE_GAS_LOW = 213
    B_PORT_HIGH_PRESSURE_GAS_HIGH = 214
    B_PORT_NOT_STANDBY = 215
    B_PORT_WEIGHT_OFFSET_ZERO = 221
    B_PORT_GROSS_OFFSET_OVER = 222
    B_PORT_NOT_CHANGE = 223
    B_PORT_PT1_STANDBY_LOW = 231
    B_PORT_SUPPLY_LINE_BYPASS = 233
    B_PORT_MANIFOLD_HEATER_SENSOR_ERROR = 240
    B_PORT_LINE_HEATER_SENSOR_ERROR = 241
    B_PORT_JACKET_HEATER_SENSOR_ERROR = 242
    B_PORT_COOLING_SENSOR_ERROR = 243
    B_PORT_MANIFOLD_HEATER_HIGH_TEMP = 244
    B_PORT_LINE_HEATER_HIGH_TEMP = 245
    B_PORT_JACKET_HEATER_HIGH_TEMP = 246
    B_PORT_MANIFOLD_HEATER_BIMETAL = 247
    B_PORT_LINE_HEATER_BIMETAL = 248
    B_PORT_JACKET_HEATER_BIMETAL = 249
    B_PORT_COOLING_JACKET_HIGH_TEMP_1 = 250
    B_PORT_COOLING_JACKET_HIGH_TEMP_2 = 251
    B_PORT_PT1_HIGH_PRESSURE_2ND = 260
    B_PORT_PT1_HIGH_PRESSURE_1ST = 261
    B_PORT_PT1_LOW_PRESSURE_1ST = 262
    B_PORT_PT1_LOW_PRESSURE_2ND = 263
    B_PORT_PT2_HIGH_PRESSURE_2ND = 264
    B_PORT_PT2_HIGH_PRESSURE_1ST = 265
    B_PORT_PT2_LOW_PRESSURE_1ST = 266
    B_PORT_PT2_LOW_PRESSURE_2ND = 267
    B_PORT_PT3_HIGH_PRESSURE = 268
    B_PORT_PT3_LOW_PRESSURE = 269
    B_PORT_AV1_BYPASS_STATUS = 270
    B_PORT_WEIGHT_OVER = 280
    B_PORT_WEIGHT_ERROR = 281
    B_PORT_WEIGHT_LOW_1ST = 282
    B_PORT_WEIGHT_LOW_2ND = 283
    B_PORT_PT1_NEG_PRESSURE_HIGH = 290
    B_PORT_PT1_NEG_PRESSURE_LOW = 291
    B_PORT_PT2_NEG_PRESSURE_HIGH = 292
    B_PORT_PT2_NEG_PRESSURE_LOW = 293
    A_PORT_FASTENING_MOTOR_ERROR = 301
    A_PORT_ROTATION_MOTOR_ERROR = 302
    A_PORT_UPDOWN_MOTOR_ERROR = 303
    A_PORT_CGA_POSITION_ERROR = 304
    A_PORT_TURN_POSITION_ERROR = 305
    A_PORT_CAP_POSITION_ERROR = 306
    A_PORT_UNDOCKING_ERROR = 307
    A_PORT_DOCKING_ERROR = 308
    A_PORT_HANDVALVE_CYLINDER_FORWARD_ERROR = 309
    A_PORT_HANDVALVE_CYLINDER_RIGHT_ERROR = 310
    A_PORT_HANDVALVE_CYLINDER_LEFT_ERROR = 311
    A_PORT_HANDVALVE_LATCH_ERROR = 312
    A_PORT_HANDVALVE_LATCH_RELEASE_ERROR = 313
    A_PORT_HANDVALVE_SPRING_RELEASE_ERROR = 314
    A_PORT_HANDVALVE_SPRING_WINDING_ERROR = 315
    A_PORT_GASKET_UNIT_REMOVE_POS_ERROR = 316
    A_PORT_GASKET_UNIT_PLUG_POS_ERROR = 317
    A_PORT_GASKET_UNIT_INSERT_POS_ERROR = 318
    A_PORT_GASKET_UNIT_REMOVE_ERROR = 319
    A_PORT_GASKET_UNIT_FORWARD_ERROR = 320
    A_PORT_GASKET_UNIT_BACKWARD_ERROR = 321
    A_PORT_GASKET_UNIT_NO_GASKET_ERROR = 322
    A_PORT_GASKET_UNIT_FULL_ERROR = 323
    A_PORT_GASKET_UNIT_DETECT_ERROR = 324
    A_PORT_CGA_FIBER_SENSOR_FRONT_ERROR = 325
    A_PORT_CGA_FIBER_SENSOR_REAR_ERROR = 326
    A_PORT_LIFT_UNIT_CLAMP_OPEN_ERROR = 327
    A_PORT_LIFT_UNIT_CLAMP_GRIP_ERROR = 328
    A_PORT_LIFT_UNIT_TURNTABLE_LOCK_ERROR = 329
    A_PORT_LIFT_UNIT_TURNTABLE_UNLOCK_ERROR = 330
    A_PORT_COUPLER_UNIT_BALANCE_ERROR = 331
    A_PORT_CAP_REMOVE_ERROR = 332
    A_PORT_LEFT_BOX_SMOKE_ERROR = 334
    A_PORT_GAS_CABINET_EMS_ERROR = 335
    A_PORT_CGA_CONNECT_TIMEOUT = 336
    A_PORT_CAP_CONNECT_TIMEOUT = 337
    A_PORT_HANDVALVE_OPEN_INTERLOCK_OVER = 338
    A_PORT_GASKET_CHECK_INTERLOCK_OVER = 339
    A_PORT_HANDVALVE_CLOSE_INTERLOCK_OVER = 340
    A_PORT_HORIZONTAL_ALIGN_RANGE_OVER = 341
    A_PORT_VALVE_OPEN_DURING_CAP_ERROR = 342
    A_PORT_HORIZONTAL_ALIGN_FIND_ERROR = 343
    A_PORT_CAP_CGA_RETRY_OVER = 344
    A_PORT_LIFT_HEATER_FORWARD_ERROR = 345
    A_PORT_LIFT_HEATER_BACKWARD_ERROR = 346
    A_PORT_LIFT_HINGE_LOCK_FORWARD_ERROR = 347
    A_PORT_LIFT_HINGE_LOCK_BACKWARD_ERROR = 348
    A_PORT_LIFT_GAS_CYLINDER_DETECT_ERROR = 349
    A_PORT_CGA_CONNECT_RETRY_OVER = 350
    A_PORT_LIFT_B_BARREL_CLAMP_ERROR = 351
    A_PORT_UNDOCKING_DETECT_ERROR = 352
    A_PORT_LIFT_LEFT_HINGE_OPEN_ERROR = 353
    A_PORT_LIFT_RIGHT_HINGE_OPEN_ERROR = 354
    A_PORT_COUPLER_CLAMP_FORWARD_ERROR = 355
    A_PORT_COUPLER_CLAMP_DETECT_ERROR = 356
    A_PORT_COUPLER_CLAMP_BACKWARD_ERROR = 357
    A_PORT_GASKET_CGA_PLUG_DETECT_ERROR = 358
    A_PORT_GASKET_CGA_PLUG_FORWARD_ERROR = 359
    A_PORT_GASKET_BOX_DETECT_ERROR = 360
    A_PORT_LIFT_POSITION_TIMEOUT = 361
    A_PORT_GASKET_BOX_COVER_OPEN_ERROR = 362
    A_PORT_GASKET_BOX_COVER_CLOSE_ERROR = 363
    A_PORT_GASKET_GRIPPER_GRIP_DETECT_ERROR = 364
    A_PORT_GASKET_GRIPPER_GRIP_ERROR = 365
    A_PORT_GASKET_REMOVE_COUNT_OVER = 366
    A_PORT_VERTICAL_ALIGN_FIND_ERROR = 367
    A_PORT_GAS_CYLINDER_ALIGN_DETECT_ERROR = 368
    A_PORT_LIFT_TURN_TIMEOUT = 369
    A_PORT_VISION_RETRY_OVER = 370
    A_PORT_HANDVALVE_SPRING_BACKWARD_ERROR = 371
    A_PORT_UNDOCKING_DETECT_ERROR_2 = 372
    A_PORT_PLUG_CONNECT_TIMEOUT = 373
    A_PORT_HANDVALVE_LOW_PRESSURE_OPEN_INTERLOCK_OVER = 374
    A_PORT_BARCODE_READ_ERROR = 375
    A_PORT_ETHERCAT_COMM_ERROR = 393
    A_PORT_EIP_COMM_ERROR = 394
    A_PORT_UPPER_COMM_ERROR = 395
    A_PORT_AUTO_DOOR_MOTOR_ERROR = 396

    # B Port Motion Control Alarms (401-496)
    B_PORT_FASTENING_MOTOR_ERROR = 401
    B_PORT_ROTATION_MOTOR_ERROR = 402
    B_PORT_UPDOWN_MOTOR_ERROR = 403
    B_PORT_CGA_POSITION_ERROR = 404
    B_PORT_TURN_POSITION_ERROR = 405
    B_PORT_CAP_POSITION_ERROR = 406
    B_PORT_UNDOCKING_ERROR = 407
    B_PORT_DOCKING_ERROR = 408
    B_PORT_HANDVALVE_CYLINDER_FORWARD_ERROR = 409
    B_PORT_HANDVALVE_CYLINDER_RIGHT_ERROR = 410
    B_PORT_HANDVALVE_CYLINDER_LEFT_ERROR = 411
    B_PORT_HANDVALVE_LATCH_ERROR = 412
    B_PORT_HANDVALVE_LATCH_RELEASE_ERROR = 413
    B_PORT_HANDVALVE_SPRING_RELEASE_ERROR = 414
    B_PORT_HANDVALVE_SPRING_WINDING_ERROR = 415
    B_PORT_GASKET_UNIT_REMOVE_POS_ERROR = 416
    B_PORT_GASKET_UNIT_PLUG_POS_ERROR = 417
    B_PORT_GASKET_UNIT_INSERT_POS_ERROR = 418
    B_PORT_GASKET_UNIT_REMOVE_ERROR = 419
    B_PORT_GASKET_UNIT_FORWARD_ERROR = 420
    B_PORT_GASKET_UNIT_BACKWARD_ERROR = 421
    B_PORT_GASKET_UNIT_NO_GASKET_ERROR = 422
    B_PORT_GASKET_UNIT_FULL_ERROR = 423
    B_PORT_GASKET_UNIT_DETECT_ERROR = 424
    B_PORT_CGA_FIBER_SENSOR_FRONT_ERROR = 425
    B_PORT_CGA_FIBER_SENSOR_REAR_ERROR = 426
    B_PORT_LIFT_UNIT_CLAMP_OPEN_ERROR = 427
    B_PORT_LIFT_UNIT_CLAMP_GRIP_ERROR = 428
    B_PORT_LIFT_UNIT_TURNTABLE_LOCK_ERROR = 429
    B_PORT_LIFT_UNIT_TURNTABLE_UNLOCK_ERROR = 430
    B_PORT_COUPLER_UNIT_BALANCE_ERROR = 431
    B_PORT_CAP_REMOVE_ERROR = 432
    B_PORT_RESERVED_433 = 433
    B_PORT_LEFT_BOX_SMOKE_ERROR = 434
    B_PORT_GAS_CABINET_EMS_ERROR = 435
    B_PORT_CGA_CONNECT_TIMEOUT = 436
    B_PORT_CAP_CONNECT_TIMEOUT = 437
    B_PORT_HANDVALVE_OPEN_INTERLOCK_OVER = 438
    B_PORT_GASKET_CHECK_INTERLOCK_OVER = 439
    B_PORT_HANDVALVE_CLOSE_INTERLOCK_OVER = 440
    B_PORT_HORIZONTAL_ALIGN_RANGE_OVER = 441
    B_PORT_VALVE_OPEN_DURING_CAP_ERROR = 442
    B_PORT_HORIZONTAL_ALIGN_FIND_ERROR = 443
    B_PORT_CAP_CGA_RETRY_OVER = 444
    B_PORT_LIFT_HEATER_FORWARD_ERROR = 445
    B_PORT_LIFT_HEATER_BACKWARD_ERROR = 446
    B_PORT_LIFT_HINGE_LOCK_FORWARD_ERROR = 447
    B_PORT_LIFT_HINGE_LOCK_BACKWARD_ERROR = 448
    B_PORT_LIFT_GAS_CYLINDER_DETECT_ERROR = 449
    B_PORT_CGA_CONNECT_RETRY_OVER = 450
    B_PORT_LIFT_B_BARREL_CLAMP_ERROR = 451
    B_PORT_UNDOCKING_DETECT_ERROR = 452
    B_PORT_LIFT_LEFT_HINGE_OPEN_ERROR = 453
    B_PORT_LIFT_RIGHT_HINGE_OPEN_ERROR = 454
    B_PORT_COUPLER_CLAMP_FORWARD_ERROR = 455
    B_PORT_COUPLER_CLAMP_DETECT_ERROR = 456
    B_PORT_COUPLER_CLAMP_BACKWARD_ERROR = 457
    B_PORT_GASKET_CGA_PLUG_DETECT_ERROR = 458
    B_PORT_GASKET_CGA_PLUG_FORWARD_ERROR = 459
    B_PORT_GASKET_BOX_DETECT_ERROR = 460
    B_PORT_LIFT_POSITION_TIMEOUT = 461
    B_PORT_GASKET_BOX_COVER_OPEN_ERROR = 462
    B_PORT_GASKET_BOX_COVER_CLOSE_ERROR = 463
    B_PORT_GASKET_GRIPPER_GRIP_DETECT_ERROR = 464
    B_PORT_GASKET_GRIPPER_GRIP_ERROR = 465
    B_PORT_GASKET_REMOVE_COUNT_OVER = 466
    B_PORT_VERTICAL_ALIGN_FIND_ERROR = 467
    B_PORT_GAS_CYLINDER_ALIGN_DETECT_ERROR = 468
    B_PORT_LIFT_TURN_TIMEOUT = 469
    B_PORT_VISION_RETRY_OVER = 470
    B_PORT_HANDVALVE_SPRING_BACKWARD_ERROR = 471
    B_PORT_UNDOCKING_DETECT_ERROR_2 = 472
    B_PORT_PLUG_CONNECT_TIMEOUT = 473
    B_PORT_HANDVALVE_LOW_PRESSURE_OPEN_INTERLOCK_OVER = 474
    B_PORT_BARCODE_READ_ERROR = 475
    B_PORT_ETHERCAT_COMM_ERROR = 493
    B_PORT_EIP_COMM_ERROR = 494
    B_PORT_UPPER_COMM_ERROR = 495
    B_PORT_AUTO_DOOR_MOTOR_ERROR = 496

    @classmethod
    def get_description(cls, code):
        """알람 코드에 대한 설명을 반환"""
        alarm_descriptions = {
            1: "[공통] REDUNANCY OFF ERROR",
            2: "[공통] EMS S/W On ERROR",
            3: "[공통] SAFETY UNIT OUT OFF CHECK ERROR",
            4: "[공통] SMOKE DETECT CHECK ON ERROR",
            5: "[공통] GAS AIR PRESSURE OFF CHECK ERROR",
            6: "[공통] AUTO AIR PRESSURE OFF CHECK ERROR",
            7: "[공통] DOOR OPEN CHECK OFF ERROR",
            8: "[공통] AUTO COUPLER SYSTEM EMG STATUS ERROR",
            9: "[공통] ARS RUN OFF CHECK ERROR",
            10: "[공통] UV/IR ON CHECK ERROR",
            11: "[공통] Hi-Temp ON CHECK ERROR",
            12: "[공통] Gas 2nd Leak CHECK ERROR",
            13: "[공통] Cabinet Door Open Shutdown ERROR",
            14: "[공통] Exhaust Velocity ERROR",
            15: "[공통] Remote Shutdown Error",
            16: "[공통] PT1 HIGH PRESSURE STATUS Error",
            17: "[공통] Reserved",
            18: "[공통] Reserved",
            19: "[공통] Reserved",
            20: "[공통] 가스 누출 1차",
            21: "[공통] Exhaust Fail",
            22: "[공통] VALVE LIFE TIME OVER (SOME ONE)",
            # alarm_descriptions 딕셔너리에 추가할 부분
            101: "[A Port] 배관 내 잔류 가스 발생 알람",
            102: "[A Port] 펄스 벤트 알람",
            103: "[A Port] 펄스 벤트 진행 횟수 초과 알람",
            104: "[A Port] 배관 진공 상태 불량 알람",
            105: "[A Port] 배관 라인 상태 불량 알람",
            106: "[A Port] 배관 질소 공급 상태 불량 알람",
            107: "[A Port] PT 감압 시험 불량 알람",
            108: "[A Port] VT 감압 시험 불량 알람",
            109: "[A Port] AV11 Bypass 알람",
            110: "[A Port] AV1 Bypass 알람",
            111: "[A Port] 가압 시험 불량 알람",
            112: "[A Port] 가압 시험 압력 상승 알람",
            113: "[A Port] 고압 가스 부족 알람",
            114: "[A Port] 고압 가스 상한치 알람",
            115: "[A Port] NOT STAND-BY 알람",
            121: "[A Port] 무게 옵셋 제로 셋팅 알람",
            122: "[A Port] Gross 옵셋 범위 초과 알람",
            123: "[A Port] NOT CHANGE 알람",
            131: "[A Port] PT1 STAND-BY 저압 알람",
            133: "[A Port] 공급 라인 BYPASS 발생 알람",
            140: "[A Port] Manifold Heater 센서 단선 알람",
            141: "[A Port] Line Heater 센서 단선 알람",
            142: "[A Port] Jacket Heater 센서 단선 알람",
            143: "[A Port] Cooling 단선 알람",
            144: "[A Port] MANIFOLD HEATER 고온 알람",
            145: "[A Port] Line HEATER 고온 알람",
            146: "[A Port] Jacket Heater 고온 알람",
            147: "[A Port] MANIFOLD HEATER BIMETAL 알람",
            148: "[A Port] LINE HEATER BIMETAL 알람",
            149: "[A Port] Jacket HEATER BIMETAL 알람",
            150: "[A Port] Cooling Jacket 1차 고온 알람",
            151: "[A Port] Cooling Jacket 2차 고온",
            160: "[A Port] PT1 2차 고압 상태",
            161: "[A Port] PT1 1차 고압 상태",
            162: "[A Port] PT1 1차 저압 상태",
            163: "[A Port] PT1 2차 저압 상태",
            164: "[A Port] PT2 2차 고압 상태 (Shutdown)",
            165: "[A Port] PT2 1차 고압 상태",
            166: "[A Port] PT2 1차 저압 상태",
            167: "[A Port] PT2 2차 저압 상태",
            168: "[A Port] PT3 고압 상태",
            169: "[A Port] PT3 저압 상태",
            170: "[A Port] AV1 BY-PASS 상태",
            180: "[A Port] 무게 과 중량",
            181: "[A Port] 무게 이상",
            182: "[A Port] 무게 1차 저 중량 상태",
            183: "[A Port] 무게 2차 저 중량 상태",
            190: "[A Port] PT1 음압 상한",
            191: "[A Port] PT1 음압 하한",
            192: "[A Port] PT2 음압 상한",
            193: "[A Port] PT2 음압 하한",
            201: "[B Port] 배관 내 잔류 가스 발생 알람",
            202: "[B Port] 펄스 벤트 알람",
            203: "[B Port] 펄스 벤트 진행 횟수 초과 알람",
            204: "[B Port] 배관 진공 상태 불량 알람",
            205: "[B Port] 배관 라인 상태 불량 알람",
            206: "[B Port] 배관 질소 공급 상태 불량 알람",
            207: "[B Port] PT 감압 시험 불량 알람",
            208: "[B Port] VT 감압 시험 불량 알람",
            209: "[B Port] AV11 Bypass 알람",
            210: "[B Port] AV1 Bypass 알람",
            211: "[B Port] 가압 시험 불량 알람",
            212: "[B Port] 가압 시험 압력 상승 알람",
            213: "[B Port] 고압 가스 부족 알람",
            214: "[B Port] 고압 가스 상한치 알람",
            215: "[B Port] NOT STAND-BY 알람",
            221: "[B Port] 무게 옵셋 제로 셋팅 알람",
            222: "[B Port] Gross 옵셋 범위 초과 알람",
            223: "[B Port] NOT CHANGE 알람",
            231: "[B Port] PT1 STAND-BY 저압 알람",
            233: "[B Port] 공급 라인 BYPASS 발생 알람",
            240: "[B Port] Manifold Heater 센서 단선 알람",
            241: "[B Port] Line Heater 센서 단선 알람",
            242: "[B Port] Jacket Heater 센서 단선 알람",
            243: "[B Port] Cooling 단선 알람",
            244: "[B Port] MANIFOLD HEATER 고온 알람",
            245: "[B Port] Line HEATER 고온 알람",
            246: "[B Port] Jacket Heater 고온 알람",
            247: "[B Port] MANIFOLD HEATER BIMETAL 알람",
            248: "[B Port] LINE HEATER BIMETAL 알람",
            249: "[B Port] Jacket HEATER BIMETAL 알람",
            250: "[B Port] Cooling Jacket 1차 고온 알람",
            251: "[B Port] Cooling Jacket 2차 고온",
            260: "[B Port] PT1 2차 고압 상태",
            261: "[B Port] PT1 1차 고압 상태",
            262: "[B Port] PT1 1차 저압 상태",
            263: "[B Port] PT1 2차 저압 상태",
            264: "[B Port] PT2 2차 고압 상태 (Shutdown)",
            265: "[B Port] PT2 1차 고압 상태",
            266: "[B Port] PT2 1차 저압 상태",
            267: "[B Port] PT2 2차 저압 상태",
            268: "[B Port] PT3 고압 상태",
            269: "[B Port] PT3 저압 상태",
            270: "[B Port] AV1 BY-PASS 상태",
            280: "[B Port] 무게 과 중량",
            281: "[B Port] 무게 이상",
            282: "[B Port] 무게 1차 저 중량 상태",
            283: "[B Port] 무게 2차 저 중량 상태",
            290: "[B Port] PT1 음압 상한",
            291: "[B Port] PT1 음압 하한",
            292: "[B Port] PT2 음압 상한",
            293: "[B Port] PT2 음압 하한",
            301: "[A Port] 체결 모터 이상",
            302: "[A Port] 회전 모터 이상",
            303: "[A Port] 상승/하강 모터 이상",
            304: "[A Port] 체결부 CGA 위치 이동 이상",
            305: "[A Port] 체결부 Turn 위치 이동 이상",
            306: "[A Port] 체결부 CAP 위치 이동 이상",
            307: "[A Port] 체결부 후진(도킹해제) 이상",
            308: "[A Port] 체결부 전진(도킹) 이상",
            309: "[A Port] 핸드밸브 연결실린더 전진 이상",
            310: "[A Port] 핸드밸브 Open/Close 실린더 우측 이동 이상",
            311: "[A Port] 핸드밸브 Open/Close 실린더 좌측 이동 이상",
            312: "[A Port] 핸드밸브 Latch 실린더 연결 이상",
            313: "[A Port] 핸드밸브 Latch 실린더 해제 이상",
            314: "[A Port] 핸드밸브 태엽 고정 실린더 해제 이상",
            315: "[A Port] 핸드밸브 태엽 감기 실린더 감기 이상",
            316: "[A Port] 가스켓 Unit 제거 위치 이동 이상",
            317: "[A Port] 가스켓 Unit Plug 위치 이동 이상",
            318: "[A Port] 가스켓 Unit Insert 위치 이동 이상",
            319: "[A Port] 가스켓 Unit 가스켓 제거 이상",
            320: "[A Port] 가스켓 Unit 전진 이상",
            321: "[A Port] 가스켓 Unit 후진 이상",
            322: "[A Port] 가스켓 Unit 삽입 피스톤 가스켓 없음 이상",
            323: "[A Port] 가스켓 Unit 제거 피스톤 가스켓 Full 이상",
            324: "[A Port] 가스켓 Unit 가스켓 삽입 후 감지 이상",
            325: "[A Port] 가스 실린더 CGA 감지 Fiber Sensor Front 이상",
            326: "[A Port] 가스 실린더 CGA 감지 Fiber Sensor Rear 이상",
            327: "[A Port] 리프트 Unit 실린더 클램프 열기 이상",
            328: "[A Port] 리프트 Unit 실린더 클램프 잡기 이상",
            329: "[A Port] 리프트 Unit 실린더 회전테이블 고정 이상",
            330: "[A Port] 리프트 Unit 실린더 회전테이블 풀기 이상",
            331: "[A Port] 커플러 Unit 웨이트발란스 상승 이상",
            332: "[A Port] 캡 제거 이상",
            334: "[A Port] 왼쪽 전장 박스 연기감지 이상",
            335: "[A Port] Gas Cabinet EMS 감지 이상",
            336: "[A Port] CGA 체결 시간 초과 이상",
            337: "[A Port] CAP 체결 시간 초과 이상",
            338: "[A Port] 핸드밸브 열림 동작 인터락 횟수 초과 이상",
            339: "[A Port] Gasket 유무 확인 인터락 횟수 초과 이상",
            340: "[A Port] 핸드밸브 닫기 동작 인터락 횟수 초과 이상",
            341: "[A Port] 수평 얼라인 범위 초과 이상",
            342: "[A Port] 캡 오픈 중 밸브열림 명령 이상",
            343: "[A Port] 수평 얼라인 찾기 실패 이상",
            344: "[A Port] CAP&CGA 체결 Retry 횟수 초과 이상",
            345: "[A Port] 리프트 Unit 히터 접촉 실린더 전진 이상",
            346: "[A Port] 리프트 Unit 히터 접촉 실린더 후진 이상",
            347: "[A Port] 리프트 Unit 힌지 고정 실린더 전진 이상",
            348: "[A Port] 리프트 Unit 힌지 고정 실린더 후진 이상",
            349: "[A Port] 리프트 Unit Gas Cylinder 감지 이상",
            350: "[A Port] CGA 연결 Retry 횟수 초과 이상",
            351: "[A Port] Lifter 상승중 B면 Barrel Clamper Open 상태 이상",
            352: "[A Port] 체결부 후진(도킹해제) 감지 이상",
            353: "[A Port] 리프트 Unit 왼쪽 힌지 열림 감지 이상",
            354: "[A Port] 리프트 Unit 오른쪽 힌지 열림 감지 이상",
            355: "[A Port] 커플러 Unit 클램프 실린더 전진 이상",
            356: "[A Port] 커플러 Unit 클램프 감지 이상",
            357: "[A Port] 커플러 Unit 클램프 실린더 후진 이상",
            358: "[A Port] 가스켓 Unit CGA Plug 전진 감지 이상",
            359: "[A Port] 가스켓 Unit CGA Plug 전진 이상",
            360: "[A Port] 가스켓 Unit 가스켓 박스 감지 이상",
            361: "[A Port] 리프트 Unit 리프트 위치 이동 시간 초과 이상",
            362: "[A Port] 가스켓 Unit 가스켓 박스 커버 열림 감지 이상",
            363: "[A Port] 가스켓 Unit 가스켓 박스 커버 닫힘 감지 이상",
            364: "[A Port] 가스켓 Unit 가스켓 그립퍼 그립 감지 이상",
            365: "[A Port] 가스켓 Unit 가스켓 그립퍼 그립 이상",
            366: "[A Port] 가스켓 Unit 가스켓 제거 횟수 초과 이상",
            367: "[A Port] 수직 얼라인 찾기 실패 이상",
            368: "[A Port] Gas Cylinder 얼라인 감지 이상",
            369: "[A Port] 리프트 Unit 턴 위치 이동 시간 초과 이상",
            370: "[A Port] 비젼 Retry 횟수 초과 이상",
            371: "[A Port] 핸드밸브 태엽 고정 실린더 후진 감지 이상",
            372: "[A Port] 체결부 후진(도킹해제) 감지 이상",
            373: "[A Port] Plug 체결 시간 초과 이상",
            374: "[A Port] 핸드밸브 밸브 저압 열기 인터락 횟수 초과 이상",
            375: "[A Port] 바코드 읽기 실패 이상",
            393: "[A Port] EtherCat 통신 이상",
            394: "[A Port] EIP 통신 이상", 
            395: "[A Port] 상위 통신 이상",
            396: "[A Port] 자동 도어 모터 이상",
            401: "[B Port] 체결 모터 이상",
            402: "[B Port] 회전 모터 이상",
            403: "[B Port] 상승/하강 모터 이상",
            404: "[B Port] 체결부 CGA 위치 이동 이상",
            405: "[B Port] 체결부 Turn 위치 이동 이상",
            406: "[B Port] 체결부 CAP 위치 이동 이상",
            407: "[B Port] 체결부 후진(도킹해제) 이상",
            408: "[B Port] 체결부 전진(도킹) 이상",
            409: "[B Port] 핸드밸브 연결실린더 전진 이상",
            410: "[B Port] 핸드밸브 Open/Close 실린더 우측 이동 이상",
            411: "[B Port] 핸드밸브 Open/Close 실린더 좌측 이동 이상",
            412: "[B Port] 핸드밸브 Latch 실린더 연결 이상",
            413: "[B Port] 핸드밸브 Latch 실린더 해제 이상",
            414: "[B Port] 핸드밸브 태엽 고정 실린더 해제 이상",
            415: "[B Port] 핸드밸브 태엽 감기 실린더 감기 이상",
            416: "[B Port] 가스켓 Unit 제거 위치 이동 이상",
            417: "[B Port] 가스켓 Unit Plug 위치 이동 이상",
            418: "[B Port] 가스켓 Unit Insert 위치 이동 이상",
            419: "[B Port] 가스켓 Unit 가스켓 제거 이상",
            420: "[B Port] 가스켓 Unit 전진 이상",
            421: "[B Port] 가스켓 Unit 후진 이상",
            422: "[B Port] 가스켓 Unit 삽입 피스톤 가스켓 없음 이상",
            423: "[B Port] 가스켓 Unit 제거 피스톤 가스켓 Full 이상",
            424: "[B Port] 가스켓 Unit 가스켓 삽입 후 감지 이상",
            425: "[B Port] 가스 실린더 CGA 감지 Fiber Sensor Front 이상",
            426: "[B Port] 가스 실린더 CGA 감지 Fiber Sensor Rear 이상",
            427: "[B Port] 리프트 Unit 실린더 클램프 열기 이상",
            428: "[B Port] 리프트 Unit 실린더 클램프 잡기 이상",
            429: "[B Port] 리프트 Unit 실린더 회전테이블 고정 이상",
            430: "[B Port] 리프트 Unit 실린더 회전테이블 풀기 이상",
            431: "[B Port] 커플러 Unit 웨이트발란스 상승 이상",
            432: "[B Port] 캡 제거 이상",
            433: "[B Port] Reserved",
            434: "[B Port] 왼쪽 전장 박스 연기감지 이상",
            435: "[B Port] Gas Cabinet EMS 감지 이상",
            436: "[B Port] CGA 체결 시간 초과 이상",
            437: "[B Port] CAP 체결 시간 초과 이상",
            438: "[B Port] 핸드밸브 열림 동작 인터락 횟수 초과 이상",
            439: "[B Port] Gasket 유무 확인 인터락 횟수 초과 이상",
            440: "[B Port] 핸드밸브 닫기 동작 인터락 횟수 초과 이상",
            441: "[B Port] 수평 얼라인 범위 초과 이상",
            442: "[B Port] 캡 오픈 중 밸브열림 명령 이상",
            443: "[B Port] 수평 얼라인 찾기 실패 이상",
            444: "[B Port] CAP&CGA 체결 Retry 횟수 초과 이상",
            445: "[B Port] 리프트 Unit 히터 접촉 실린더 전진 이상",
            446: "[B Port] 리프트 Unit 히터 접촉 실린더 후진 이상",
            447: "[B Port] 리프트 Unit 힌지 고정 실린더 전진 이상",
            448: "[B Port] 리프트 Unit 힌지 고정 실린더 후진 이상",
            449: "[B Port] 리프트 Unit Gas Cylinder 감지 이상",
            450: "[B Port] CGA 연결 Retry 횟수 초과 이상",
            451: "[B Port] Lifter 상승중 B면 Barrel Clamper Open 상태 이상",
            452: "[B Port] 체결부 후진(도킹해제) 감지 이상",
            453: "[B Port] 리프트 Unit 왼쪽 힌지 열림 감지 이상",
            454: "[B Port] 리프트 Unit 오른쪽 힌지 열림 감지 이상",
            455: "[B Port] 커플러 Unit 클램프 실린더 전진 이상",
            456: "[B Port] 커플러 Unit 클램프 감지 이상",
            457: "[B Port] 커플러 Unit 클램프 실린더 후진 이상",
            458: "[B Port] 가스켓 Unit CGA Plug 전진 감지 이상",
            459: "[B Port] 가스켓 Unit CGA Plug 전진 이상",
            460: "[B Port] 가스켓 Unit 가스켓 박스 감지 이상",
            461: "[B Port] 리프트 Unit 리프트 위치 이동 시간 초과 이상",
            462: "[B Port] 가스켓 Unit 가스켓 박스 커버 열림 감지 이상",
            463: "[B Port] 가스켓 Unit 가스켓 박스 커버 닫힘 감지 이상",
            464: "[B Port] 가스켓 Unit 가스켓 그립퍼 그립 감지 이상",
            465: "[B Port] 가스켓 Unit 가스켓 그립퍼 그립 이상",
            466: "[B Port] 가스켓 Unit 가스켓 제거 횟수 초과 이상",
            467: "[B Port] 수직 얼라인 찾기 실패 이상",
            468: "[B Port] Gas Cylinder 얼라인 감지 이상",
            469: "[B Port] 리프트 Unit 턴 위치 이동 시간 초과 이상",
            470: "[B Port] 비젼 Retry 횟수 초과 이상",
            471: "[B Port] 핸드밸브 태엽 고정 실린더 후진 감지 이상",
            472: "[B Port] 체결부 후진(도킹해제) 감지 이상",
            473: "[B Port] Plug 체결 시간 초과 이상",
            474: "[B Port] 핸드밸브 밸브 저압 열기 인터락 횟수 초과 이상",
            475: "[B Port] 바코드 읽기 실패 이상",
            493: "[B Port] EtherCat 통신 이상",
            494: "[B Port] EIP 통신 이상",
            495: "[B Port] 상위 통신 이상",
            496: "[B Port] 자동 도어 모터 이상",
            
        }
        return alarm_descriptions.get(code, "Unknown Alarm Code")

    @classmethod
    def is_valid_alarm(cls, code):
        """주어진 코드가 유효한 알람 코드인지 확인"""
        return code in [member.value for member in cls]
# 인스턴스 생성
gas_cabinet_alarm_code = GasCabinetAlarmCode()

# # 사용 예시
# if __name__ == "__main__":
#     # 알람 코드 열거
#     print("Available Alarm Codes:")
#     for alarm in GasCabinetAlarmCode:
#         print(f"{alarm.value}: {GasCabinetAlarmCode.get_description(alarm.value)}")
    
#     # 특정 알람 코드 조회
#     test_code = 475
#     if GasCabinetAlarmCode.is_valid_alarm(test_code):
#         print(f"\nAlarm {test_code}: {GasCabinetAlarmCode.get_description(test_code)}")
#     else:
#         print(f"\nInvalid alarm code: {test_code}")
    
#     # 알람 코드 조회
#     alarm_code = 475
#     description = GasCabinetAlarmCode.get_description(alarm_code)
#     print(f"Alarm {alarm_code}: {description}")

#     # Enum으로 접근
#     alarm = GasCabinetAlarmCode.B_PORT_BARCODE_READ_ERROR
#     print(f"Alarm code: {alarm.value}")
#     print(f"Description: {GasCabinetAlarmCode.get_description(alarm.value)}")