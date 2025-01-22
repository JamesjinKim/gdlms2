# gas_cabinet_db.py
from base_db import BaseDB, AlarmCodeMixin
from typing import Dict, Any
import json

class GasCabinetDB(BaseDB, AlarmCodeMixin):
    async def initialize(self):
        """Gas Cabinet 데이터베이스 초기화"""
        async with self._init_lock:
            if self._initialized:
                return
            
            async with await self.get_connection() as conn:
                await conn.executescript('''
                    -- Gas Cabinet 기본 데이터 테이블
                    CREATE TABLE IF NOT EXISTS gas_cabinet_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        bunker_id INTEGER,
                        cabinet_id INTEGER,
                        machine_code INTEGER,
                        alarm_code INTEGER,
                        alarm_message TEXT
                    );

                    -- 센서 데이터 테이블
                    CREATE TABLE IF NOT EXISTS gas_cabinet_sensors (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cabinet_data_id INTEGER,
                        pt1a REAL,
                        pt2a REAL,
                        pt1b REAL,
                        pt2b REAL,
                        pt3 REAL,
                        pt4 REAL,
                        weight_a REAL,
                        weight_b REAL,
                        FOREIGN KEY (cabinet_data_id) REFERENCES gas_cabinet_data(id)
                    );

                    -- 히터 데이터 테이블
                    CREATE TABLE IF NOT EXISTS gas_cabinet_heaters (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cabinet_data_id INTEGER,
                        jacket_heater_a_temp REAL,
                        line_heater_a_temp REAL,
                        jacket_heater_b_temp REAL,
                        line_heater_b_temp REAL,
                        FOREIGN KEY (cabinet_data_id) REFERENCES gas_cabinet_data(id)
                    );

                    -- 시스템 상태 비트 테이블
                    CREATE TABLE IF NOT EXISTS gas_cabinet_system_status (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cabinet_data_id INTEGER,
                        emg_signal BOOLEAN,
                        heart_bit BOOLEAN,
                        run_stop_signal BOOLEAN,
                        server_connected BOOLEAN,
                        port_a_cylinder BOOLEAN,
                        port_b_cylinder BOOLEAN,
                        port_a_manual BOOLEAN,
                        port_b_manual BOOLEAN,
                        door_open BOOLEAN,
                        door_close BOOLEAN,
                        FOREIGN KEY (cabinet_data_id) REFERENCES gas_cabinet_data(id)
                    );

                    -- 센서/릴레이 상태 테이블
                    CREATE TABLE IF NOT EXISTS gas_cabinet_sensor_relay_status (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cabinet_data_id INTEGER,
                        lamp_red BOOLEAN,
                        lamp_yellow BOOLEAN,
                        lamp_green BOOLEAN,
                        jacket_heater_a_relay BOOLEAN,
                        line_heater_a_relay BOOLEAN,
                        jacket_heater_b_relay BOOLEAN,
                        line_heater_b_relay BOOLEAN,
                        gas_leak_shutdown BOOLEAN,
                        vmb_stop BOOLEAN,
                        uv_ir_sensor BOOLEAN,
                        high_temp_sensor BOOLEAN,
                        smoke_sensor BOOLEAN,
                        FOREIGN KEY (cabinet_data_id) REFERENCES gas_cabinet_data(id)
                    );

                    -- 포트 진행 상태 테이블
                    CREATE TABLE IF NOT EXISTS gas_cabinet_port_progress (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cabinet_data_id INTEGER,
                        port_id TEXT,
                        close_cylinder BOOLEAN,
                        purge_1st_before BOOLEAN,
                        decompression_test BOOLEAN,
                        purge_2nd_before BOOLEAN,
                        exchange_cylinder BOOLEAN,
                        purge_1st_after BOOLEAN,
                        pressure_test BOOLEAN,
                        purge_2nd_after BOOLEAN,
                        purge_completed BOOLEAN,
                        prepare_supply BOOLEAN,
                        av3_control BOOLEAN,
                        gas_supply BOOLEAN,
                        ready_supply BOOLEAN,
                        FOREIGN KEY (cabinet_data_id) REFERENCES gas_cabinet_data(id)
                    );

                    -- 포트 밸브 상태 테이블
                    CREATE TABLE IF NOT EXISTS gas_cabinet_port_valves (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cabinet_data_id INTEGER,
                        port_id TEXT,
                        av1 BOOLEAN,
                        av2 BOOLEAN,
                        av3 BOOLEAN,
                        av4 BOOLEAN,
                        av5 BOOLEAN,
                        av7 BOOLEAN,
                        av8 BOOLEAN,
                        av9 BOOLEAN,
                        FOREIGN KEY (cabinet_data_id) REFERENCES gas_cabinet_data(id)
                    );

                    -- Gas Cabinet 알람 코드 테이블
                    CREATE TABLE IF NOT EXISTS gas_cabinet_alarm_codes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        alarm_code INTEGER NOT NULL,
                        alarm_comment TEXT NOT NULL,
                        category TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    );

                    -- 인덱스 생성
                    CREATE INDEX IF NOT EXISTS idx_gas_cabinet_timestamp 
                    ON gas_cabinet_data(timestamp);
                    
                    CREATE INDEX IF NOT EXISTS idx_gas_cabinet_ids 
                    ON gas_cabinet_data(bunker_id, cabinet_id);
                ''')
                
                self._initialized = True
                self.logger.info("Gas Cabinet database initialized successfully")

    async def save_data(self, data: Dict[str, Any]):
        """Gas Cabinet 데이터 저장"""
        try:
            async with await self.get_connection() as conn:
                # 기본 데이터 저장
                cursor = await conn.execute('''
                    INSERT INTO gas_cabinet_data 
                    (bunker_id, cabinet_id, machine_code, alarm_code, alarm_message)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    data['basic']['bunker_id'],
                    data['basic']['cabinet_id'],
                    data['status']['machine_code'],
                    data['status']['alarm_code'],
                    data.get('alarm_message', '')
                ))
                cabinet_data_id = cursor.lastrowid

                # 센서 데이터 저장
                sensors = data['sensors']
                await conn.execute('''
                    INSERT INTO gas_cabinet_sensors 
                    (cabinet_data_id, pt1a, pt2a, pt1b, pt2b, pt3, pt4, weight_a, weight_b)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    cabinet_data_id,
                    sensors['pt1a'], sensors['pt2a'],
                    sensors['pt1b'], sensors['pt2b'],
                    sensors['pt3'], sensors['pt4'],
                    sensors['weight_a'], sensors['weight_b']
                ))

                # 히터 데이터 저장
                heaters = data['heaters']
                await conn.execute('''
                    INSERT INTO gas_cabinet_heaters 
                    (cabinet_data_id, jacket_heater_a_temp, line_heater_a_temp,
                     jacket_heater_b_temp, line_heater_b_temp)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    cabinet_data_id,
                    heaters['jacket_heater_a'],
                    heaters['line_heater_a'],
                    heaters['jacket_heater_b'],
                    heaters['line_heater_b']
                ))

                # 시스템 상태 저장
                system = data['bitStatus']['system']
                await conn.execute('''
                    INSERT INTO gas_cabinet_system_status 
                    (cabinet_data_id, emg_signal, heart_bit, run_stop_signal,
                     server_connected, port_a_cylinder, port_b_cylinder,
                     port_a_manual, port_b_manual, door_open, door_close)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    cabinet_data_id,
                    system['emg_signal'],
                    system['heart_bit'],
                    system['run_stop_signal'],
                    system['server_connected'],
                    system['port_a_cylinder'],
                    system['port_b_cylinder'],
                    system['port_a_manual'],
                    system['port_b_manual'],
                    system['door_open'],
                    system['door_close']
                ))

                # Port A/B 데이터 저장
                for port_id in ['A', 'B']:
                    port_data = data['bitStatus'][f'port{port_id}']
                    
                    # 진행 상태 저장
                    progress = port_data['progress']['states']
                    await conn.execute('''
                        INSERT INTO gas_cabinet_port_progress 
                        (cabinet_data_id, port_id, close_cylinder, purge_1st_before,
                         decompression_test, purge_2nd_before, exchange_cylinder,
                         purge_1st_after, pressure_test, purge_2nd_after,
                         purge_completed, prepare_supply, av3_control,
                         gas_supply, ready_supply)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        cabinet_data_id, port_id,
                        *[progress[k] for k in [
                            'close_cylinder', 'purge_1st_before', 'decompression_test',
                            'purge_2nd_before', 'exchange_cylinder', 'purge_1st_after',
                            'pressure_test', 'purge_2nd_after', 'purge_completed',
                            'prepare_supply', 'av3_control', 'gas_supply', 'ready_supply'
                        ]]
                    ))

                    # 밸브 상태 저장
                    valves = port_data['valves']['states']
                    await conn.execute('''
                        INSERT INTO gas_cabinet_port_valves 
                        (cabinet_data_id, port_id, av1, av2, av3, av4, av5,
                         av7, av8, av9)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        cabinet_data_id, port_id,
                        valves.get(f'av1{port_id.lower()}', False),
                        valves.get(f'av2{port_id.lower()}', False),
                        valves.get(f'av3{port_id.lower()}', False),
                        valves.get(f'av4{port_id.lower()}', False),
                        valves.get(f'av5{port_id.lower()}', False),
                        valves.get('av7', False),
                        valves.get('av8', False),
                        valves.get('av9', False)
                    ))

                await conn.commit()
                self.logger.info(f"Gas Cabinet data saved successfully. ID: {cabinet_data_id}")

        except Exception as e:
            self.logger.error(f"Error saving gas cabinet data: {e}")
            raise

    async def clean_old_data(self, days: int = 30):
        """오래된 데이터 정리"""
        try:
            async with await self.get_connection() as conn:
                tables = [
                    'gas_cabinet_port_valves',
                    'gas_cabinet_port_progress',
                    'gas_cabinet_system_status',
                    'gas_cabinet_sensor_relay_status',
                    'gas_cabinet_heaters',
                    'gas_cabinet_sensors',
                    'gas_cabinet_data'
                ]
                
                for table in tables:
                    await conn.execute(f'''
                        DELETE FROM {table} 
                        WHERE timestamp < datetime('now', '-{days} days')
                    ''')
                
                await conn.commit()
                self.logger.info(f"Cleaned gas cabinet data older than {days} days")
        except Exception as e:
            self.logger.error(f"Error cleaning old data: {e}")
            raise