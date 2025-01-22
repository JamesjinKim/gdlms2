import sqlite3
import logging
import os
import pandas as pd
from datetime import datetime

class ExtendedDatabaseHandler:
    def __init__(self, db_path):
        """
        DatabaseHandler 확장 초기화
        Args:
            db_path (str): SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """데이터베이스 및 테이블 초기화"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 기존 modbus_messages 테이블 유지
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS modbus_messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        message_type TEXT NOT NULL,
                        function_code INTEGER NOT NULL,
                        register_address INTEGER NOT NULL,
                        register_data TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # gas cabinet 알람 코드 테이블 생성
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS gas_cabinet_alarm_codes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        alarm_code INTEGER NOT NULL,
                        alarm_comment TEXT NOT NULL,
                        category TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # stocker 알람 코드 테이블 생성
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS stocker_alarm_codes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        alarm_code INTEGER NOT NULL,
                        alarm_comment TEXT NOT NULL,
                        category TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                conn.commit()
                logging.info(f"Database initialized at: {self.db_path}")

        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {e}")
            raise

    def check_gas_cabinet_alarm_table_empty(self):
        """알람 코드 테이블이 비어있는지 확인"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM gas_cabinet_alarm_codes")
                count = cursor.fetchone()[0]
                return count == 0
        except sqlite3.Error as e:
            logging.error(f"Error checking alarm table: {e}")
            return True

    def check_stocker_alarm_table_empty(self):
        """알람 코드 테이블이 비어있는지 확인"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM stocker_alarm_codes")
                count = cursor.fetchone()[0]
                return count == 0
        except sqlite3.Error as e:
            logging.error(f"Error checking alarm table: {e}")
            return True
        
    def insert_gas_cabinet_alarm_codes(self):
        """알람 코드 데이터 삽입"""
        alarm_data = [
            (1, "[공통] REDUNANCY OFF ERROR", "공통"),
            (2, "[공통] EMS S/W On ERROR", "공통"),
            (3, "[공통] SAFETY UNIT OUT OFF CHECK ERROR", "공통"),
            (4, "[공통] SMOKE DETECT CHECK ON ERROR", "공통"),
            (5, "[공통] GAS AIR PRESSURE OFF CHECK ERROR", "공통"),
            (6, "[공통] AUTO AIR PRESSURE OFF CHECK ERROR", "공통"),
            (7, "[공통] DOOR OPEN CHECK OFF ERROR", "공통"),
            (8, "[공통] AUTO COUPLER SYSTEM EMG STATUS ERROR", "공통"),
            (9, "[공통] ARS RUN OFF CHECK ERROR", "공통"),
            (10, "[공통] UV/IR ON CHECK ERROR", "공통"),
            (11, "[공통] Hi-Temp ON CHECK ERROR", "공통"),
            (12, "[공통] Gas 2nd Leak CHECK ERROR", "공통"),
            (13, "[공통] Cabinet Door Open Shutdown ERROR", "공통"),
            (14, "[공통] Exhaust Velocity ERROR", "공통"),
            (15, "[공통] Remote Shutdown Error", "공통"),
            (16, "[공통] PT1 HIGH PRESSURE STATUS Error", "공통"),
            (17, "[공통] Reserved", "공통"),
            (18, "[공통] Reserved", "공통"),
            (19, "[공통] Reserved", "공통"),
            (20, "[공통] 가스 누출 1차", "공통"),
            (21, "[공통] Exhaust Fail", "공통"),
            (22, "[공통] VALVE LIFE TIME OVER (SOME ONE)", "공통"),
            (101, "[A Port] 배관 내 잔류 가스 발생 알람", "A Port"),
            (102, "[A Port] 펄스 벤트 알람 [A Port]", "A Port"),
            (103, "[A Port] 펄스 벤트 진행 횟수 초과 알람", "A Port"),
            (104, "[A Port] 배관 진공 상태 불량 알람 [A Port]", "A Port"),
            (105, "[A Port] 배관 라인 상태 불량 알람 [A Port]", "A Port"),
            (106, "[A Port] 배관 질소 공급 상태 불량 알람 [A Port]", "A Port"),
            (107, "[A Port] PT 감압 시험 불량 알람", "A Port"),
            (108, "[A Port] VT 감압 시험 불량 알람", "A Port"),
            (109, "[A Port] AV11 Bypass 알람", "A Port"),
            (110, "[A Port] AV1 Bypass 알람", "A Port"),
            (111, "[A Port] 가압 시험 불량 알람", "A Port"),
            (112, "[A Port] 가압 시험 압력 상승 알람", "A Port"),
            (113, "[A Port] 고압 가스 부족 알람", "A Port"),
            (114, "[A Port] 고압 가스 상한치 알람", "A Port"),
            (115, "[A Port] NOT STAND-BY 알람", "A Port"),
            (116, "[A Port] Reserved", "A Port"),
            (117, "[A Port] Reserved", "A Port"),
            (118, "[A Port] Reserved", "A Port"),
            (119, "[A Port] Reserved", "A Port"),
            (120, "[A Port] Reserved", "A Port"),
            (121, "[A Port] 무게 옵셋 제로 셋팅 알람", "A Port"),
            (122, "[A Port] Gross 옵셋 범위 초과 알람", "A Port"),
            (123, "[A Port] NOT CHANGE 알람", "A Port"),
            (124, "[A Port] Reserved", "A Port"),
            (125, "[A Port] Reserved", "A Port"),
            (126, "[A Port] Reserved", "A Port"),
            (127, "[A Port] Reserved", "A Port"),
            (128, "[A Port] Reserved", "A Port"),
            (129, "[A Port] Reserved", "A Port"),
            (130, "[A Port] Reserved", "A Port"),
            (131, "[A Port] PT1 STAND-BY 저압 알람", "A Port"),
            (132, "[A Port] Reserved", "A Port"),
            (133, "[A Port] 공급 라인 BYPASS 발생 알람", "A Port"),
            (134, "[A Port] Reserved", "A Port"),
            (135, "[A Port] Reserved", "A Port"),
            (136, "[A Port] Reserved", "A Port"),
            (137, "[A Port] Reserved", "A Port"),
            (138, "[A Port] Reserved", "A Port"),
            (139, "[A Port] Reserved", "A Port"),
            (140, "[A Port] Manifold Heater 센서 단선 알람", "A Port"),
            (141, "[A Port] Line Heater 센서 단선 알람", "A Port"),
            (142, "[A Port] Jacket Heater 센서 단선 알람", "A Port"),
            (143, "[A Port] Cooling 단선 알람", "A Port"),
            (144, "[A Port] MANIFOLD HEATER 고온 알람", "A Port"),
            (145, "[A Port] Line HEATER 고온 알람", "A Port"),
            (146, "[A Port] Jacket Heater 고온 알람", "A Port"),
            (147, "[A Port] MANIFOLD HEATER BIMETAL 알람", "A Port"),
            (148, "[A Port] LINE HEATER BIMETAL 알람", "A Port"),
            (149, "[A Port] Jacket HEATER BIMETAL 알람", "A Port"),
            (150, "[A Port] Cooling Jacket 1차 고온 알람", "A Port"),
            (151, "[A Port] Cooling Jacket 2차 고온", "A Port"),
            (152, "[A Port] Reserved", "A Port"),
            (153, "[A Port] Reserved", "A Port"),
            (154, "[A Port] Reserved", "A Port"),
            (155, "[A Port] Reserved", "A Port"),
            (156, "[A Port] Reserved", "A Port"),
            (157, "[A Port] Reserved", "A Port"),
            (158, "[A Port] Reserved", "A Port"),
            (159, "[A Port] Reserved", "A Port"),
            (160, "[A Port] PT1 2차 고압 상태", "A Port"),
            (161, "[A Port] PT1 1차 고압 상태", "A Port"),
            (162, "[A Port] PT1 1차 저압 상태", "A Port"),
            (163, "[A Port] PT1 2차 저압 상태", "A Port"),
            (164, "[A Port] PT2 2차 고압 상태 (Shutdown)", "A Port"),
            (165, "[A Port] PT2 1차 고압 상태", "A Port"),
            (166, "[A Port] PT2 1차 저압 상태", "A Port"),
            (167, "[A Port] PT2 2차 저압 상태", "A Port"),
            (168, "[A Port] PT3 고압 상태", "A Port"),
            (169, "[A Port] PT3 저압 상태", "A Port"),
            (170, "[A Port] AV1 BY-PASS 상태", "A Port"),
            (171, "[A Port] Reserved", "A Port"),
            (172, "[A Port] Reserved", "A Port"),
            (173, "[A Port] Reserved", "A Port"),
            (174, "[A Port] Reserved", "A Port"),
            (175, "[A Port] Reserved", "A Port"),
            (176, "[A Port] Reserved", "A Port"),
            (177, "[A Port] Reserved", "A Port"),
            (178, "[A Port] Reserved", "A Port"),
            (179, "[A Port] Reserved", "A Port"),
            (180, "[A Port] 무게 과 중량", "A Port"),
            (181, "[A Port] 무게 이상", "A Port"),
            (182, "[A Port] 무게 1차 저 중량 상태", "A Port"),
            (183, "[A Port] 무게 2차 저 중량 상태", "A Port"),
            (184, "[A Port] Reserved", "A Port"),
            (185, "[A Port] Reserved", "A Port"),
            (186, "[A Port] Reserved", "A Port"),
            (187, "[A Port] Reserved", "A Port"),
            (188, "[A Port] Reserved", "A Port"),
            (189, "[A Port] Reserved", "A Port"),
            (190, "[A Port] PT1 음압 상한", "A Port"),
            (191, "[A Port] PT1 음압 하한", "A Port"),
            (192, "[A Port] PT2 음압 상한", "A Port"),
            (193, "[A Port] PT2 음압 하한", "A Port"),
            (194, "[A Port] Reserved", "A Port"),
            (195, "[A Port] Reserved", "A Port"),
            (196, "[A Port] Reserved", "A Port"),
            (197, "[A Port] Reserved", "A Port"),
            (198, "[A Port] Reserved", "A Port"),
            (199, "[A Port] Reserved", "A Port"),
            (200, "[A Port] Reserved", "A Port"),
            (201, "[B Port] 배관 내 잔류 가스 발생 알람", "B Port"),
            (202, "[B Port] 펄스 벤트 알람 [B Port]", "B Port"),
            (203, "[B Port] 펄스 벤트 진행 횟수 초과 알람", "B Port"),
            (204, "[B Port] 배관 진공 상태 불량 알람 [B Port]", "B Port"), 
            (205, "[B Port] 배관 라인 상태 불량 알람 [B Port]", "B Port"),
            (206, "[B Port] 배관 질소 공급 상태 불량 알람 [B Port]", "B Port"),
            (207, "[B Port] PT 감압 시험 불량 알람", "B Port"),
            (208, "[B Port] VT 감압 시험 불량 알람", "B Port"),
            (209, "[B Port] AV11 Bypass 알람", "B Port"),
            (210, "[B Port] AV1 Bypass 알람", "B Port"),
            (211, "[B Port] 가압 시험 불량 알람", "B Port"),
            (212, "[B Port] 가압 시험 압력 상승 알람", "B Port"),
            (213, "[B Port] 고압 가스 부족 알람", "B Port"),
            (214, "[B Port] 고압 가스 상한치 알람", "B Port"),
            (215, "[B Port] NOT STAND-BY 알람", "B Port"),
            (216, "[B Port] Reserved", "B Port"),
            (217, "[B Port] Reserved", "B Port"),
            (218, "[B Port] Reserved", "B Port"),
            (219, "[B Port] Reserved", "B Port"),
            (220, "[B Port] Reserved", "B Port"),
            (221, "[B Port] 무게 옵셋 제로 셋팅 알람", "B Port"),
            (222, "[B Port] Gross 옵셋 범위 초과 알람", "B Port"),
            (223, "[B Port] NOT CHANGE 알람", "B Port"),
            (224, "[B Port] Reserved", "B Port"),
            (225, "[B Port] Reserved", "B Port"),
            (226, "[B Port] Reserved", "B Port"),
            (227, "[B Port] Reserved", "B Port"),
            (228, "[B Port] Reserved", "B Port"),
            (229, "[B Port] Reserved", "B Port"),
            (230, "[B Port] Reserved", "B Port"),
            (231, "[B Port] PT1 STAND-BY 저압 알람", "B Port"),
            (232, "[B Port] Reserved", "B Port"),
            (233, "[B Port] 공급 라인 BYPASS 발생 알람", "B Port"),
            (234, "[B Port] Reserved", "B Port"),
            (235, "[B Port] Reserved", "B Port"),
            (236, "[B Port] Reserved", "B Port"),
            (237, "[B Port] Reserved", "B Port"),
            (238, "[B Port] Reserved", "B Port"),
            (239, "[B Port] Reserved", "B Port"),
            (240, "[B Port] Manifold Heater 센서 단선 알람", "B Port"),
            (241, "[B Port] Line Heater 센서 단선 알람", "B Port"),
            (242, "[B Port] Jacket Heater 센서 단선 알람", "B Port"),
            (243, "[B Port] Cooling 단선 알람", "B Port"),
            (244, "[B Port] MANIFOLD HEATER 고온 알람", "B Port"),
            (245, "[B Port] Line HEATER 고온 알람", "B Port"),
            (246, "[B Port] Jacket Heater 고온 알람", "B Port"),
            (247, "[B Port] MANIFOLD HEATER BIMETAL 알람", "B Port"),
            (248, "[B Port] LINE HEATER BIMETAL 알람", "B Port"),
            (249, "[B Port] Jacket HEATER BIMETAL 알람", "B Port"),
            (250, "[B Port] Cooling Jacket 1차 고온 알람", "B Port"),
            (251, "[B Port] Cooling Jacket 2차 고온", "B Port"),
            (252, "[B Port] Reserved", "B Port"),
            (253, "[B Port] Reserved", "B Port"),
            (254, "[B Port] Reserved", "B Port"),
            (255, "[B Port] Reserved", "B Port"),
            (256, "[B Port] Reserved", "B Port"),
            (257, "[B Port] Reserved", "B Port"),
            (258, "[B Port] Reserved", "B Port"),
            (259, "[B Port] Reserved", "B Port"),
            (260, "[B Port] PT1 2차 고압 상태", "B Port"),
            (261, "[B Port] PT1 1차 고압 상태", "B Port"),
            (262, "[B Port] PT1 1차 저압 상태", "B Port"),
            (263, "[B Port] PT1 2차 저압 상태", "B Port"),
            (264, "[B Port] PT2 2차 고압 상태 (Shutdown)", "B Port"),
            (265, "[B Port] PT2 1차 고압 상태", "B Port"),
            (266, "[B Port] PT2 1차 저압 상태", "B Port"),
            (267, "[B Port] PT2 2차 저압 상태", "B Port"),
            (268, "[B Port] PT3 고압 상태", "B Port"),
            (269, "[B Port] PT3 저압 상태", "B Port"),
            (270, "[B Port] AV1 BY-PASS 상태", "B Port"),
            (271, "[B Port] Reserved", "B Port"),
            (272, "[B Port] Reserved", "B Port"),
            (273, "[B Port] Reserved", "B Port"),
            (274, "[B Port] Reserved", "B Port"),
            (275, "[B Port] Reserved", "B Port"),
            (276, "[B Port] Reserved", "B Port"),
            (277, "[B Port] Reserved", "B Port"),
            (278, "[B Port] Reserved", "B Port"),
            (279, "[B Port] Reserved", "B Port"),
            (280, "[B Port] 무게 과 중량", "B Port"),
            (281, "[B Port] 무게 이상", "B Port"),
            (282, "[B Port] 무게 1차 저 중량 상태", "B Port"),
            (283, "[B Port] 무게 2차 저 중량 상태", "B Port"),
            (284, "[B Port] Reserved", "B Port"),
            (285, "[B Port] Reserved", "B Port"),
            (286, "[B Port] Reserved", "B Port"),
            (287, "[B Port] Reserved", "B Port"),
            (288, "[B Port] Reserved", "B Port"),
            (289, "[B Port] Reserved", "B Port"),
            (290, "[B Port] PT1 음압 상한", "B Port"),
            (291, "[B Port] PT1 음압 하한", "B Port"),
            (292, "[B Port] PT2 음압 상한", "B Port"),
            (293, "[B Port] PT2 음압 하한", "B Port"),
            (294, "[B Port] Reserved", "B Port"),
            (295, "[B Port] Reserved", "B Port"),
            (296, "[B Port] Reserved", "B Port"),
            (297, "[B Port] Reserved", "B Port"),
            (298, "[B Port] Reserved", "B Port"),
            (299, "[B Port] Reserved", "B Port"),
            (300, "[B Port] Reserved", "B Port"),
            (301, "[A Port] 체결 모터 이상", "A Port"),
            (302, "[A Port] 회전 모터 이상", "A Port"),
            (303, "[A Port] 상승/하강 모터 이상", "A Port"),
            (304, "[A Port] 체결부 CGA 위치 이동 이상", "A Port"),
            (305, "[A Port] 체결부 Turn 위치 이동 이상", "A Port"),
            (306, "[A Port] 체결부 CAP 위치 이동 이상", "A Port"),
            (307, "[A Port] 체결부 후진(도킹해제) 이상", "A Port"),
            (308, "[A Port] 체결부 전진(도킹) 이상", "A Port"),
            (309, "[A Port] 핸드밸브 연결실린더 전진 이상", "A Port"),
            (310, "[A Port] 핸드밸브 Open/Close 실린더 우측 이동 이상", "A Port"),
            (311, "[A Port] 핸드밸브 Open/Close 실린더 좌측 이동 이상", "A Port"),
            (312, "[A Port] 핸드밸브 Latch 실린더 연결 이상", "A Port"),
            (313, "[A Port] 핸드밸브 Latch 실린더 해제 이상", "A Port"),
            (314, "[A Port] 핸드밸브 태엽 고정 실린더 해제 이상", "A Port"),
            (315, "[A Port] 핸드밸브 태엽 감기 실린더 감기 이상", "A Port"),
            (316, "[A Port] 가스켓 Unit 제거 위치 이동 이상", "A Port"),
            (317, "[A Port] 가스켓 Unit Plug 위치 이동 이상", "A Port"),
            (318, "[A Port] 가스켓 Unit Insert 위치 이동 이상", "A Port"),
            (319, "[A Port] 가스켓 Unit 가스켓 제거 이상", "A Port"),
            (320, "[A Port] 가스켓 Unit 전진 이상", "A Port"),
            (321, "[A Port] 가스켓 Unit 후진 이상", "A Port"),
            (322, "[A Port] 가스켓 Unit 삽입 피스톤 가스켓 없음 이상", "A Port"),
            (323, "[A Port] 가스켓 Unit 제거 피스톤 가스켓 Full 이상", "A Port"),
            (324, "[A Port] 가스켓 Unit 가스켓 삽입 후 감지 이상", "A Port"),
            (325, "[A Port] 가스 실린더 CGA 감지 Fiber Sensor Front 이상", "A Port"),
            (326, "[A Port] 가스 실린더 CGA 감지 Fiber Sensor Rear 이상", "A Port"),
            (327, "[A Port] 리프트 Unit 실린더 클램프 열기 이상", "A Port"),
            (328, "[A Port] 리프트 Unit 실린더 클램프 잡기 이상", "A Port"),
            (329, "[A Port] 리프트 Unit 실린더 회전테이블 고정 이상", "A Port"),
            (330, "[A Port] 리프트 Unit 실린더 회전테이블 풀기 이상", "A Port"),
            (331, "[A Port] 커플러 Unit 웨이트발란스 상승 이상", "A Port"),
            (332, "[A Port] 캡 제거 이상", "A Port"),
            (333, "[A Port] Reserved", "A Port"),
            (334, "[A Port] 왼쪽 전장 박스 연기감지 이상", "A Port"),
            (335, "[A Port] Gas Cabinet EMS 감지 이상", "A Port"),
            (336, "[A Port] CGA 체결 시간 초과 이상", "A Port"),
            (337, "[A Port] CAP 체결 시간 초과 이상", "A Port"),
            (338, "[A Port] 핸드밸브 열림 동작 인터락 횟수 초과 이상", "A Port"),
            (339, "[A Port] Gasket 유무 확인 인터락 횟수 초과 이상", "A Port"),
            (340, "[A Port] 핸드밸브 닫기 동작 인터락 횟수 초과 이상", "A Port"),
            (341, "[A Port] 수평 얼라인 범위 초과 이상", "A Port"),
            (342, "[A Port] 캡 오픈 중 밸브열림 명령 이상", "A Port"),
            (343, "[A Port] 수평 얼라인 찾기 실패 이상", "A Port"),
            (344, "[A Port] CAP&CGA 체결 Retry 횟수 초과 이상", "A Port"),
            (345, "[A Port] 리프트 Unit 히터 접촉 실린더 전진 이상", "A Port"),
            (346, "[A Port] 리프트 Unit 히터 접촉 실린더 후진 이상", "A Port"),
            (347, "[A Port] 리프트 Unit 힌지 고정 실린더 전진 이상", "A Port"),
            (348, "[A Port] 리프트 Unit 힌지 고정 실린더 후진 이상", "A Port"),
            (349, "[A Port] 리프트 Unit Gas Cylinder 감지 이상", "A Port"),
            (350, "[A Port] CGA 연결 Retry 횟수 초과 이상", "A Port"),
            (351, "[A Port] Lifter 상승중 B면 Barrel Clamper Open 상태 이상", "A Port"),
            (352, "[A Port] 체결부 후진(도킹해제) 감지 이상", "A Port"),
            (353, "[A Port] 리프트 Unit 왼쪽 힌지 열림 감지 이상", "A Port"),
            (354, "[A Port] 리프트 Unit 오른쪽 힌지 열림 감지 이상", "A Port"),
            (355, "[A Port] 커플러 Unit 클램프 실린더 전진 이상", "A Port"),
            (356, "[A Port] 커플러 Unit 클램프 감지 이상", "A Port"),
            (357, "[A Port] 커플러 Unit 클램프 실린더 후진 이상", "A Port"),
            (358, "[A Port] 가스켓 Unit CGA Plug 전진 감지 이상", "A Port"),
            (359, "[A Port] 가스켓 Unit CGA Plug 전진 이상", "A Port"),
            (360, "[A Port] 가스켓 Unit 가스켓 박스 감지 이상", "A Port"),
            (361, "[A Port] 리프트 Unit 리프트 위치 이동 시간 초과 이상", "A Port"),
            (362, "[A Port] 가스켓 Unit 가스켓 박스 커버 열림 감지 이상", "A Port"),
            (363, "[A Port] 가스켓 Unit 가스켓 박스 커버 닫힘 감지 이상", "A Port"),
            (364, "[A Port] 가스켓 Unit 가스켓 그립퍼 그립 감지 이상", "A Port"),
            (365, "[A Port] 가스켓 Unit 가스켓 그립퍼 그립 이상", "A Port"),
            (366, "[A Port] 가스켓 Unit 가스켓 제거 횟수 초과 이상", "A Port"),
            (367, "[A Port] 수직 얼라인 찾기 실패 이상", "A Port"),
            (368, "[A Port] Gas Cylinder 얼라인 감지 이상", "A Port"),
            (369, "[A Port] 리프트 Unit 턴 위치 이동 시간 초과 이상", "A Port"),
            (370, "[A Port] 비젼 Retry 횟수 초과 이상", "A Port"),
            (371, "[A Port] 핸드밸브 태엽 고정 실린더 후진 감지 이상", "A Port"),
            (372, "[A Port] 체결부 후진(도킹해제) 감지 이상", "A Port"),
            (373, "[A Port] Plug 체결 시간 초과 이상", "A Port"),
            (374, "[A Port] 핸드밸브 밸브 저압 열기 인터락 횟수 초과 이상", "A Port"),
            (375, "[A Port] 바코드 읽기 실패 이상", "A Port"),
            (376, "[A Port] Reserved", "A Port"),
            (377, "[A Port] Reserved", "A Port"),
            (378, "[A Port] Reserved", "A Port"),
            (379, "[A Port] Reserved", "A Port"),
            (380, "[A Port] Reserved", "A Port"),
            (381, "[A Port] Reserved", "A Port"),
            (382, "[A Port] Reserved", "A Port"),
            (383, "[A Port] Reserved", "A Port"),
            (384, "[A Port] Reserved", "A Port"),
            (385, "[A Port] Reserved", "A Port"),
            (386, "[A Port] Reserved", "A Port"),
            (387, "[A Port] Reserved", "A Port"),
            (388, "[A Port] Reserved", "A Port"),
            (389, "[A Port] Reserved", "A Port"),
            (390, "[A Port] Reserved", "A Port"),
            (391, "[A Port] Reserved", "A Port"),
            (392, "[A Port] Reserved", "A Port"),
            (393, "[A Port] EtherCat 통신 이상", "A Port"),
            (394, "[A Port] EIP 통신 이상", "A Port"),
            (395, "[A Port] 상위 통신 이상", "A Port"),
            (396, "[A Port] 자동 도어 모터 이상", "A Port"),
            (397, "[A Port] Reserved", "A Port"),
            (398, "[A Port] Reserved", "A Port"),
            (399, "[A Port] Reserved", "A Port"),
            (400, "[A Port] Reserved", "A Port"),
            (401, "[B Port] 체결 모터 이상", "B Port"),
            (402, "[B Port] 회전 모터 이상", "B Port"),
            (403, "[B Port] 상승/하강 모터 이상", "B Port"),
            (404, "[B Port] 체결부 CGA 위치 이동 이상", "B Port"),
            (405, "[B Port] 체결부 Turn 위치 이동 이상", "B Port"),
            (406, "[B Port] 체결부 CAP 위치 이동 이상", "B Port"),
            (407, "[B Port] 체결부 후진(도킹해제) 이상", "B Port"),
            (408, "[B Port] 체결부 전진(도킹) 이상", "B Port"),
            (409, "[B Port] 핸드밸브 연결실린더 전진 이상", "B Port"),
            (410, "[B Port] 핸드밸브 Open/Close 실린더 우측 이동 이상", "B Port"),
            (411, "[B Port] 핸드밸브 Open/Close 실린더 좌측 이동 이상", "B Port"),
            (412, "[B Port] 핸드밸브 Latch 실린더 연결 이상", "B Port"),
            (413, "[B Port] 핸드밸브 Latch 실린더 해제 이상", "B Port"),
            (414, "[B Port] 핸드밸브 태엽 고정 실린더 해제 이상", "B Port"),
            (415, "[B Port] 핸드밸브 태엽 감기 실린더 감기 이상", "B Port"),
            (416, "[B Port] 가스켓 Unit 제거 위치 이동 이상", "B Port"),
            (417, "[B Port] 가스켓 Unit Plug 위치 이동 이상", "B Port"),
            (418, "[B Port] 가스켓 Unit Insert 위치 이동 이상", "B Port"),
            (419, "[B Port] 가스켓 Unit 가스켓 제거 이상", "B Port"),
            (420, "[B Port] 가스켓 Unit 전진 이상", "B Port"),
            (421, "[B Port] 가스켓 Unit 후진 이상", "B Port"),
            (422, "[B Port] 가스켓 Unit 삽입 피스톤 가스켓 없음 이상", "B Port"),
            (423, "[B Port] 가스켓 Unit 제거 피스톤 가스켓 Full 이상", "B Port"),
            (424, "[B Port] 가스켓 Unit 가스켓 삽입 후 감지 이상", "B Port"),
            (425, "[B Port] 가스 실린더 CGA 감지 Fiber Sensor Front 이상", "B Port"),
            (426, "[B Port] 가스 실린더 CGA 감지 Fiber Sensor Rear 이상", "B Port"),
            (427, "[B Port] 리프트 Unit 실린더 클램프 열기 이상", "B Port"),
            (428, "[B Port] 리프트 Unit 실린더 클램프 잡기 이상", "B Port"),
            (429, "[B Port] 리프트 Unit 실린더 회전테이블 고정 이상", "B Port"),
            (430, "[B Port] 리프트 Unit 실린더 회전테이블 풀기 이상", "B Port"),
            (431, "[B Port] 커플러 Unit 웨이트발란스 상승 이상", "B Port"),
            (432, "[B Port] 캡 제거 이상", "B Port"),
            (433, "[B Port] Reserved", "B Port"),
            (434, "[B Port] 왼쪽 전장 박스 연기감지 이상", "B Port"),
            (435, "[B Port] Gas Cabinet EMS 감지 이상", "B Port"),
            (436, "[B Port] CGA 체결 시간 초과 이상", "B Port"),
            (437, "[B Port] CAP 체결 시간 초과 이상", "B Port"),
            (438, "[B Port] 핸드밸브 열림 동작 인터락 횟수 초과 이상", "B Port"),
            (439, "[B Port] Gasket 유무 확인 인터락 횟수 초과 이상", "B Port"),
            (440, "[B Port] 핸드밸브 닫기 동작 인터락 횟수 초과 이상", "B Port"),
            (441, "[B Port] 수평 얼라인 범위 초과 이상", "B Port"),
            (442, "[B Port] 캡 오픈 중 밸브열림 명령 이상", "B Port"),
            (443, "[B Port] 수평 얼라인 찾기 실패 이상", "B Port"),
            (444, "[B Port] CAP&CGA 체결 Retry 횟수 초과 이상", "B Port"),
            (445, "[B Port] 리프트 Unit 히터 접촉 실린더 전진 이상", "B Port"),
            (446, "[B Port] 리프트 Unit 히터 접촉 실린더 후진 이상", "B Port"),
            (447, "[B Port] 리프트 Unit 힌지 고정 실린더 전진 이상", "B Port"),
            (448, "[B Port] 리프트 Unit 힌지 고정 실린더 후진 이상", "B Port"),
            (449, "[B Port] 리프트 Unit Gas Cylinder 감지 이상", "B Port"),
            (450, "[B Port] CGA 연결 Retry 횟수 초과 이상", "B Port"),
            (451, "[B Port] Lifter 상승중 B면 Barrel Clamper Open 상태 이상", "B Port"),
            (452, "[B Port] 체결부 후진(도킹해제) 감지 이상", "B Port"),
            (453, "[B Port] 리프트 Unit 왼쪽 힌지 열림 감지 이상", "B Port"),
            (454, "[B Port] 리프트 Unit 오른쪽 힌지 열림 감지 이상", "B Port"),
            (455, "[B Port] 커플러 Unit 클램프 실린더 전진 이상", "B Port"),
            (456, "[B Port] 커플러 Unit 클램프 감지 이상", "B Port"),
            (457, "[B Port] 커플러 Unit 클램프 실린더 후진 이상", "B Port"),
            (458, "[B Port] 가스켓 Unit CGA Plug 전진 감지 이상", "B Port"),
            (459, "[B Port] 가스켓 Unit CGA Plug 전진 이상", "B Port"),
            (460, "[B Port] 가스켓 Unit 가스켓 박스 감지 이상", "B Port"),
            (461, "[B Port] 리프트 Unit 리프트 위치 이동 시간 초과 이상", "B Port"),
            (462, "[B Port] 가스켓 Unit 가스켓 박스 커버 열림 감지 이상", "B Port"),
            (463, "[B Port] 가스켓 Unit 가스켓 박스 커버 닫힘 감지 이상", "B Port"),
            (464, "[B Port] 가스켓 Unit 가스켓 그립퍼 그립 감지 이상", "B Port"),
            (465, "[B Port] 가스켓 Unit 가스켓 그립퍼 그립 이상", "B Port"),
            (466, "[B Port] 가스켓 Unit 가스켓 제거 횟수 초과 이상", "B Port"),
            (467, "[B Port] 수직 얼라인 찾기 실패 이상", "B Port"),
            (468, "[B Port] Gas Cylinder 얼라인 감지 이상", "B Port"),
            (469, "[B Port] 리프트 Unit 턴 위치 이동 시간 초과 이상", "B Port"),
            (470, "[B Port] 비젼 Retry 횟수 초과 이상", "B Port"),
            (471, "[B Port] 핸드밸브 태엽 고정 실린더 후진 감지 이상", "B Port"),
            (472, "[B Port] 체결부 후진(도킹해제) 감지 이상", "B Port"),
            (473, "[B Port] Plug 체결 시간 초과 이상", "B Port"),
            (474, "[B Port] 핸드밸브 밸브 저압 열기 인터락 횟수 초과 이상", "B Port"),
            (475, "[B Port] 바코드 읽기 실패 이상", "B Port"),
            (476, "[B Port] Reserved", "B Port"),
            (477, "[B Port] Reserved", "B Port"),
            (478, "[B Port] Reserved", "B Port"),
            (479, "[B Port] Reserved", "B Port"),
            (480, "[B Port] Reserved", "B Port"),
            (481, "[B Port] Reserved", "B Port"),
            (482, "[B Port] Reserved", "B Port"),
            (483, "[B Port] Reserved", "B Port"),
            (484, "[B Port] Reserved", "B Port"),
            (485, "[B Port] Reserved", "B Port"),
            (486, "[B Port] Reserved", "B Port"),
            (487, "[B Port] Reserved", "B Port"),
            (488, "[B Port] Reserved", "B Port"),
            (489, "[B Port] Reserved", "B Port"),
            (490, "[B Port] Reserved", "B Port"),
            (491, "[B Port] Reserved", "B Port"),
            (492, "[B Port] Reserved", "B Port"),
            (493, "[B Port] EtherCat 통신 이상", "B Port"),
            (494, "[B Port] EIP 통신 이상", "B Port"),
            (495, "[B Port] 상위 통신 이상", "B Port"),
            (496, "[B Port] 자동 도어 모터 이상", "B Port"),
            (497, "[B Port] Reserved", "B Port"),
            (498, "[B Port] Reserved", "B Port"),
            (499, "[B Port] Reserved", "B Port"),
            (500, "[B Port] Reserved", "B Port")
        ]

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.executemany("""
                    INSERT INTO gas_cabinet_alarm_codes (alarm_code, alarm_comment, category)
                    VALUES (?, ?, ?)
                """, alarm_data)
                
                conn.commit()
                logging.info(f"Inserted {len(alarm_data)} gas cabinet alarm codes")
                return True

        except sqlite3.Error as e:
            logging.error(f"Error inserting alarm codes: {e}")
            return False
        
    def insert_stocker_alarm_codes(self):
        """알람 코드 데이터 삽입"""
        alarm_data = [
            (1, "Emergency 버튼이 동작", "Equipment"),
            (2, "Door 열림 감지", "Equipment"),
            (3, "Main Air OFF 감지", "Equipment"),
            (4, "Main MC OFF 감지", "Equipment"),
            (5, "Motor # 0축 (X) Amp Fault Alarm", "Equipment"),
            (6, "Motor # 1축 (Z) Amp Fault Alarm", "Equipment"),
            (7, "Motor # 2축 (Remove Turn) Amp Fault Alarm", "Equipment"),
            (8, "Motor # 3축 (Gripper Turn) Amp Fault Alarm", "Equipment"),
            (9, "Motor # 4축 (Left Door) Amp Fault Alarm", "Equipment"),
            (10, "Motor # 5축 (Right Door) Amp Fault Alarm", "Equipment"),
            (11, "Motor # 6축 (미정의) Amp Fault Alarm", "Equipment"),
            (12, "Motor # 7축 (미정의)Amp Fault Alarm", "Equipment"),
            (13, "Motor # 8축 (미정의) Amp Fault Alarm", "Equipment"),
            (14, "Motor # 9축 (미정의) Amp Fault Alarm", "Equipment"),
            (15, "초기화가 정상적으로 완료되지 않음", "Equipment"),
            (16, "초기화 : Z 축 Home Check 이동 실패", "Equipment"),
            (17, "초기화 : X 축 Home Check 이동 실패", "Equipment"),
            (18, "Front Cap Gripper 에 Cap 분리중 Cap 이 감지됨 이상", "Equipment"),
            (19, "모터 #2 Axis(Z) 이 Cap 분리중 Safety 위치로 상승 이상", "Equipment"),
            (20, "모터 #1 Axis(X) 이 Cap 분리중 Barrel (LD) 위치로 이동 이상", "Equipment"),
            (21, "Cap 분리중 Barrel 이 감지 불가 이상", "Equipment"),
            (22, "Cap 분리중 Cap 의 Top 위치 찾기 실패", "Equipment"),
            (23, "모터 #2 Axis(Z) 이 Cap 분리 준비 위치로 하강 이상", "Equipment"),
            (24, "모터 #2 Axis(Z) 이 Cap 분리 너트 체결위치로 하강 이상", "Equipment"),
            (25, "모터 #3 Axis(Rotator) 이 Cap 분리 Cap 열기시작 토크에 도달하지 못함", "Equipment"),
            (26, "모터 #2 Axis(Z) 이 Cap 분리 분리위치로 상승 이상", "Equipment"),
            (27, "Reserved", "Equipment"),
            (28, "Reserved", "Equipment"),
            (29, "Cap 체결 중 Gripper 에 Cap 감지 이상", "Equipment"),
            (30, "모터 #2 Axis(Z) 이 Safety 위치로 상승 이상", "Equipment"),
            (31, "모터 #1 Axis(X) 이 Barrel (LD) 위치로 이동 이상", "Equipment"),
            (32, "Cap 체결중 Barrel 이 감지 불가 이상", "Equipment"),
            (33, "모터 #2 Axis(Z) 이 Cap 체결 준비 위치로 하강 이상", "Equipment"),
            (34, "모터 #2 Axis(Z) 이 Cap 체결중 Barrel Neck 감지 불가 이상", "Equipment"),
            (35, "모터 #2 Axis(Z) 이 Cap 체결 위치로 하강 이상", "Equipment"),
            (36, "모터 #3 Axis(Rotator) 이 Cap 체결 Cap의 닫기 토크에 도달하지 못함", "Equipment"),
            (37, "모터 #2 Axis(Z)이 Cap 체결 Safety 위치로 상승 이상", "Equipment"),
            (38, "Reserved", "Equipment"),
            (39, "Reserved", "Equipment"),
            (40, "Reserved", "Equipment"),
            (41, "Reserved", "Equipment"),
            (42, "Reserved", "Equipment"),
            (43, "Reserved", "Equipment"),
            (44, "Reserved", "Equipment"),
            (45, "Reserved", "Equipment"),
            (46, "Reserved", "Equipment"),
            (47, "Reserved", "Equipment"),
            (48, "Reserved", "Equipment"),
            (49, "Reserved", "Equipment"),
            (50, "Reserved", "Equipment"),
            (51, "Reserved", "Equipment"),
            (52, "Rgv LD BarrelExist Check 중 Barrel 감지", "Equipment"),
            (53, "Rgv LD Door Open Check 동작 중 LD Door Open 이상 감지", "Equipment"),
            (54, "Rgv LD BarrelDetected Check 중 Barrel 미감지", "Equipment"),
            (55, "Rgv LD Door Close check 동작 중 LD Door Close 이상 감지", "Equipment"),
            (56, "Rgv ULD BarrelExist Check 중 Barrel 감지", "Equipment"),
            (57, "Rgv ULD Door Open Check 동작 중 LD Door Open 이상 감지", "Equipment"),
            (58, "Rgv ULD BarrelDetected Check 중 Barrel 미감지", "Equipment"),
            (59, "Rgv ULD Door Close check 동작 중 LD Door Close 이상 감지", "Equipment"),
            (60, "Barrel 얼라인 중에 Load 부 얼라인을 위한 회전에 실패했습니다", "Equipment"),
            (61, "Reserved", "Equipment"),
            (62, "Reserved", "Equipment"),
            (63, "Reserved", "Equipment"),
            (64, "Reserved", "Equipment"),
            (65, "Reserved", "Equipment"),
            (66, "Reserved", "Equipment"),
            (67, "Reserved", "Equipment"),
            (68, "Reserved", "Equipment"),
            (69, "Reserved", "Equipment"),
            (70, "Reserved", "Equipment"),
            (71, "Reserved", "Equipment"),
            (72, "Reserved", "Equipment"),
            (73, "Reserved", "Equipment"),
            (74, "X0000_BUNKER_EMS_ON_CHK 감지 이상", "Sensor"),
            (75, "X0001_BUNKER_MODE_SWITCH_WORKER_CHK 감지 이상", "Sensor"),
            (76, "X0002_BUNKER_MODE_SWITCH_REAR_CHK 감지 이상", "Sensor"),
            (77, "X0003_BUNKER_OPEN_SWITCH_CHK 감지 이상", "Sensor"),
            (78, "X0004_BUNKER_CLOSE_SWITCH_CHK 감지 이상", "Sensor"),
            (79, "X0005_BUNKER_S_RESET_SWITCH_CHK 감지 이상", "Sensor"),
            (80, "X0006_BUNKER_BUZZER_OFF_SWITCH_CHK 감지 이상", "Sensor"),
            (81, "X0007_WORKER_EMS_ON_CHK 감지 이상", "Sensor"),
            (82, "X0008_WORKER_MODE_SWITCH_FRONT_CHK 감지 이상", "Sensor"),
            (83, "X0009_WORKER_MODE_SWITCH_BUNKER_CHK 감지 이상", "Sensor"),
            (84, "X000A_WORKER_OPEN_SWITCH_CHK 감지 이상", "Sensor"),
            (85, "X000B_WORKER_CLOSE_SWITCH_CHK 감지 이상", "Sensor"),
            (86, "X000C_WORKER_S_RESET_SWITCH_CHK 감지 이상", "Sensor"),
            (87, "X000D_WORKER_BUZZER_OFF_SWITCH_CHK 감지 이상", "Sensor"),
            (88, "X000E_NA 감지 이상", "Sensor"),
            (89, "X000F_NA 감지 이상", "Sensor"),
            (90, "X0010_SMOKE_SENSOR_ON_CHK 감지 이상", "Sensor"),
            (91, "X0011_REGULATOR_SENSOR_ON_CHK 감지 이상", "Sensor"),
            (92, "X0012_MC_ON_CHK 감지 이상", "Sensor"),
            (93, "X0013_SAFETY_UNIT_ON_CHK 감지 이상", "Sensor"),
            (94, "X0014_FROM_PIO_SIGNAL1 감지 이상", "Sensor"),
            (95, "X0015_FROM_PIO_SIGNAL2 감지 이상", "Sensor"),
            (96, "X0016_FROM_PIO_SIGNAL3 감지 이상", "Sensor"),
            (97, "X0017_FROM_PIO_SIGNAL4 감지 이상", "Sensor"),
            (98, "X0018_FROM_PIO_SIGNAL5 감지 이상", "Sensor"),
            (99, "X0019_FROM_PIO_SIGNAL6 감지 이상", "Sensor"),
            (100, "X001A_FROM_PIO_SIGNAL7 감지 이상", "Sensor"),
            (101, "X001B_FROM_PIO_SIGNAL8 감지 이상", "Sensor"),
            (102, "X001C_FROM_PIO_SIGNAL9 감지 이상", "Sensor"),
            (103, "X001D_NA 감지 이상", "Sensor"),
            (104, "X001E_NA 감지 이상", "Sensor"),
            (105, "X001F_NA 감지 이상", "Sensor"),
            (106, "X0020_WORKER_LD_DR_OP_STATUS 감지 이상", "Sensor"),
            (107, "X0021_WORKER_LD_DR_CL_STATUS 감지 이상", "Sensor"),
            (108, "X0022_WORKER_ULD_DR_OP_STATUS 감지 이상", "Sensor"),
            (109, "X0023_WORKER_ULD_DR_CL_STATUS 감지 이상", "Sensor"),
            (110, "X0024_BUNKER_LD_DR_OP_STATUS 감지 이상", "Sensor"),
            (111, "X0025_BUNKER_LD_DR_CL_STATUS 감지 이상", "Sensor"),
            (112, "X0026_BUNKER_ULD_DR_OP_STATUS 감지 이상", "Sensor"),
            (113, "X0027_BUNKER_ULD_DR_CL_STATUS 감지 이상", "Sensor"),
            (114, "X0028_NA 감지 이상", "Sensor"),
            (115, "X0029_NA 감지 이상", "Sensor"),
            (116, "X002A_NA 감지 이상", "Sensor"),
            (117, "X002B_NA 감지 이상", "Sensor"),
            (118, "X002C_NA 감지 이상", "Sensor"),
            (119, "X002D_NA 감지 이상", "Sensor"),
            (120, "X002E_NA 감지 이상", "Sensor"),
            (121, "X002F_NA 감지 이상", "Sensor"),
            (122, "X0030_BUNKER_LD_DOOR_HEAD_CYL_FWD 감지 이상", "Sensor"),
            (123, "X0031_BUNKER_LD_DOOR_HEAD_CYL_BWD 감지 이상", "Sensor"),
            (124, "X0032_BUNKER_ULD_DOOR_HEAD_CYL_FWD 감지 이상", "Sensor"),
            (125, "X0033_BUNKER_ULD_DOOR_HEAD_CYL_BWD 감지 이상", "Sensor"),
            (126, "X0034_BUNKER_LD_DOOR_LEFT_BOT_CYL_FWD 감지 이상", "Sensor"),
            (127, "X0035_BUNKER_LD_DOOR_LEFT_BOT_CYL_BWD 감지 이상", "Sensor"),
            (128, "X0036_BUNKER_LD_DOOR_RIGHT_BOT_CYL_FWD 감지 이상", "Sensor"),
            (129, "X0037_BUNKER_LD_DOOR_RIGHT_BOT_CYL_BWD 감지 이상", "Sensor"),
            (130, "X0038_BUNKER_ULD_DOOR_LEFT_BOT_CYL_FWD 감지 이상", "Sensor"),
            (131, "X0039_BUNKER_ULD_DOOR_LEFT_BOT_CYL_BWD 감지 이상", "Sensor"),
            (132, "X003A_BUNKER_ULD_DOOR_RIGHT_BOT_CYL_FWD 감지 이상", "Sensor"),
            (133, "X003B_BUNKER_ULD_DOOR_RIGHT_BOT_CYL_BWD 감지 이상", "Sensor"),
            (134, "X003C_NA 감지 이상", "Sensor"),
            (135, "X003D_NA 감지 이상", "Sensor"),
            (136, "X003E_NA 감지 이상", "Sensor"),
            (137, "X003F_NA 감지 이상", "Sensor"),
            (138, "X0040_LD_LEFT_GRIPPER_CYL_FWD 감지 이상", "Sensor"),
            (139, "X0041_LD_LEFT_GRIPPER_CYL_BWD 감지 이상", "Sensor"),
            (140, "X0042_LD_RIGHT_GRIPPER_CYL_FWD 감지 이상", "Sensor"),
            (141, "X0043_LD_RIGHT_GRIPPER_CYL_BWD 감지 이상", "Sensor"),
            (142, "X0044_GRIPPER_UNIT_GUIDE_BAR_CYL_FWD 감지 이상", "Sensor"),
            (143, "X0045_GRIPPER_UNIT_GUIDE_BAR_CYL_BWD 감지 이상", "Sensor"),
            (144, "X0046_LD_TURN_TABLE_CYL_1_LOCK 감지 이상", "Sensor"),
            (145, "X0047_LD_TURN_TABLE_CYL_1_UNLOCK 감지 이상", "Sensor"),
            (146, "X0048_LD_TURN_TABLE_CYL_2_LOCK 감지 이상", "Sensor"),
            (147, "X0049_LD_TURN_TABLE_CYL_2_UNLOCK 감지 이상", "Sensor"),
            (148, "X004A_GRIPPER_GAS_CYL_CHK 감지 이상", "Sensor"),
            (149, "X004B_NA 감지 이상", "Sensor"),
            (150, "X004C_NA 감지 이상", "Sensor"),
            (151, "X004D_NA 감지 이상", "Sensor"),
            (152, "X004E_NA 감지 이상", "Sensor"),
            (153, "X004F_NA 감지 이상", "Sensor"),
            (154, "X0050_FRONT_CAP_GRIP_GUIDE_CYL_FWD 감지 이상", "Sensor"),
            (155, "X0051_FRONT_CAP_GRIP_GUIDE_CYL_BWD 감지 이상", "Sensor"),
            (156, "X0052_REAR_CAP_GRIP_GUIDE_CYL_FWD 감지 이상", "Sensor"),
            (157, "X0053_REAR_CAP_GRIP_GUIDE_CYL_BWD 감지 이상", "Sensor"),
            (158, "X0054_CAP_OPEN_CLOSE_CYL_UP 감지 이상", "Sensor"),
            (159, "X0055_CAP_OPEN_CLOSE_CYL_DOWN 감지 이상", "Sensor"),
            (160, "X0056_UNIT_FRONT_CAP_CHK 감지 이상", "Sensor"),
            (161, "X0057_UNIT_FRONT_NECKRING_EDGE_CHK 감지 이상", "Sensor"),
            (162, "X0058_VISION_UNIT_CYL_UP 감지 이상", "Sensor"),
            (163, "X0059_VISION_UNIT_CYL_DOWN 감지 이상", "Sensor"),
            (164, "X005A_NA 감지 이상", "Sensor"),
            (165, "X005B_NA 감지 이상", "Sensor"),
            (166, "X005C_NA 감지 이상", "Sensor"),
            (167, "X005D_NA 감지 이상", "Sensor"),
            (168, "X005E_NA 감지 이상", "Sensor"),
            (169, "X005F_NA 감지 이상", "Sensor")
        ]
    

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.executemany("""
                    INSERT INTO stocker_alarm_codes (alarm_code, alarm_comment, category)
                    VALUES (?, ?, ?)
                """, alarm_data)
                
                conn.commit()
                logging.info(f"Inserted {len(alarm_data)} stocker alarm codes")
                return True

        except sqlite3.Error as e:
            logging.error(f"Error inserting alarm codes: {e}")
            return False
        

    def get_all_alarm_codes(self):
        """모든 알람 코드 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM gas_cabinet_alarm_codes ORDER BY alarm_code")
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logging.error(f"Error retrieving alarm codes: {e}")
            return []

def main():
    # 현재 작업 디렉토리에 data 폴더 생성 후 데이터베이스 저장
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_dir = os.path.join(current_dir, 'data')
    db_path = os.path.join(db_dir, 'equipment.db')
    
    # 데이터 디렉토리가 없으면 생성
    os.makedirs(db_dir, exist_ok=True)
    
    # 핸들러 인스턴스 생성
    handler = ExtendedDatabaseHandler(db_path)
    
    # 알람 코드 테이블이 비어있는지 확인
    if handler.check_gas_cabinet_alarm_table_empty():
        # 알람 코드 데이터 삽입
        if handler.insert_gas_cabinet_alarm_codes():
            print("Gas Cabinet Alarm codes inserted successfully!")
        else:
            print("Failed to insert alarm codes!")
    else:
        print("Alarm codes table already contains data!")
    
    # 알람 코드 테이블이 비어있는지 확인
    if handler.check_stocker_alarm_table_empty():
        # 알람 코드 데이터 삽입
        if handler.insert_stocker_alarm_codes():
            print("Stocker Alarm codes inserted successfully!")
        else:
            print("Failed to insert alarm codes!")
    else:
        print("Alarm codes table already contains data!")
        
    # 저장된 알람 코드 확인
    alarm_codes = handler.get_all_alarm_codes()
    print("\nStored alarm codes:")
    for alarm in alarm_codes:
        print(f"Code {alarm['alarm_code']}: {alarm['alarm_comment']}")

if __name__ == "__main__":
    main()