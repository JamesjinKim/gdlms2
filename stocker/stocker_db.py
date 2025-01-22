# stocker_db.py
from base_db import BaseDB, AlarmCodeMixin
from typing import Dict, Any

class StockerDB(BaseDB, AlarmCodeMixin):
    async def initialize(self):
        """Stocker 데이터베이스 초기화"""
        async with self._init_lock:
            if self._initialized:
                return
            
            async with await self.get_connection() as conn:
                await conn.executescript('''
                    -- Stocker 데이터 테이블
                    CREATE TABLE IF NOT EXISTS stocker_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        bunker_id INTEGER,
                        stocker_id INTEGER,
                        alarm_code INTEGER,
                        x_pos INTEGER,
                        z_pos INTEGER
                    );

                    -- Stocker Port 데이터 테이블
                    CREATE TABLE IF NOT EXISTS stocker_port_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        stocker_data_id INTEGER,
                        port_id TEXT,
                        barcode TEXT,
                        FOREIGN KEY (stocker_data_id) REFERENCES stocker_data(id)
                    );

                    -- Stocker Gas 타입 테이블
                    CREATE TABLE IF NOT EXISTS stocker_gas_type (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        stocker_data_id INTEGER,
                        port_id TEXT,
                        gas_type_1 INTEGER,
                        gas_type_2 INTEGER,
                        gas_type_3 INTEGER,
                        gas_type_4 INTEGER,
                        gas_type_5 INTEGER,
                        FOREIGN KEY (stocker_data_id) REFERENCES stocker_data(id)
                    );

                    -- Stocker Port 설정값 테이블
                    CREATE TABLE IF NOT EXISTS stocker_port_settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        stocker_data_id INTEGER,
                        port_id TEXT,
                        cap_torque_remove_set INTEGER,
                        cap_torque_connect_set INTEGER,
                        cap_torque_remove_current INTEGER,
                        cap_torque_connect_current INTEGER,
                        x_cylinder_pos_set INTEGER,
                        z_cap_open_down_pos_set INTEGER,
                        z_cap_open_separate_pos_set INTEGER,
                        z_cap_open_up_pos_set INTEGER,
                        z_cap_close_down_pos_set INTEGER,
                        z_cap_close_screw_pos_set INTEGER,
                        z_cap_close_up_pos_set INTEGER,
                        cylinder_gripper_barrel_turn_pos_set INTEGER,
                        cylinder_gripper_barrel_turn_pos_current INTEGER,
                        worker_door_torque_set INTEGER,
                        bunker_door_torque_set INTEGER,
                        worker_door_open_pos_set INTEGER,
                        bunker_door_open_pos_set INTEGER,
                        worker_door_close_pos_set INTEGER,
                        bunker_door_close_pos_set INTEGER,
                        worker_door_torque_current INTEGER,
                        bunker_door_torque_current INTEGER,
                        worker_door_pos_current INTEGER,
                        bunker_door_pos_current INTEGER,
                        FOREIGN KEY (stocker_data_id) REFERENCES stocker_data(id)
                    );

                    -- Stocker 알람 코드 테이블
                    CREATE TABLE IF NOT EXISTS stocker_alarm_codes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        alarm_code INTEGER NOT NULL,
                        alarm_comment TEXT NOT NULL,
                        category TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    );

                    -- 인덱스 생성
                    CREATE INDEX IF NOT EXISTS idx_stocker_timestamp 
                    ON stocker_data(timestamp);
                    
                    CREATE INDEX IF NOT EXISTS idx_stocker_ids 
                    ON stocker_data(bunker_id, stocker_id);
                ''')
                
                self._initialized = True
                self.logger.info("Stocker database initialized successfully")

    async def save_data(self, data: Dict[str, Any]):
        """Stocker 데이터 저장"""
        try:
            async with await self.get_connection() as conn:
                # 기본 데이터 저장
                cursor = await conn.execute('''
                    INSERT INTO stocker_data 
                    (bunker_id, stocker_id, alarm_code, x_pos, z_pos)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    data['basic']['bunker_id'],
                    data['basic']['stocker_id'],
                    data['status']['alarm_code'],
                    data['status']['x_pos'],
                    data['status']['z_pos']
                ))
                stocker_data_id = cursor.lastrowid

                # Port A/B 데이터 저장
                for port_id in ['A', 'B']:
                    port_key = f'port_{port_id.lower()}'
                    port_data = data[port_key]

                    # 바코드 데이터 저장
                    await conn.execute('''
                        INSERT INTO stocker_port_data 
                        (stocker_data_id, port_id, barcode)
                        VALUES (?, ?, ?)
                    ''', (
                        stocker_data_id,
                        port_id,
                        str(port_data['barcode'])
                    ))

                    # Gas 타입 데이터 저장
                    await conn.execute('''
                        INSERT INTO stocker_gas_type 
                        (stocker_data_id, port_id, gas_type_1, gas_type_2, 
                         gas_type_3, gas_type_4, gas_type_5)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        stocker_data_id,
                        port_id,
                        *port_data['gas_type']
                    ))

                    # 설정값 데이터 저장
                    settings = port_data['settings']
                    await conn.execute('''
                        INSERT INTO stocker_port_settings 
                        (stocker_data_id, port_id, 
                         cap_torque_remove_set, cap_torque_connect_set,
                         cap_torque_remove_current, cap_torque_connect_current,
                         x_cylinder_pos_set,
                         z_cap_open_down_pos_set, z_cap_open_separate_pos_set,
                         z_cap_open_up_pos_set)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        stocker_data_id,
                        port_id,
                        settings['cap_torque']['remove_set'],
                        settings['cap_torque']['connect_set'],
                        settings['cap_torque']['remove_current'],
                        settings['cap_torque']['connect_current'],
                        settings['positions']['cylinder_x'],
                        settings['positions']['cap']['open_down'],
                        settings['positions']['cap']['open_separate'],
                        settings['positions']['cap']['open_up']
                    ))

                await conn.commit()
                self.logger.info(f"Stocker data saved successfully. ID: {stocker_data_id}")

        except Exception as e:
            self.logger.error(f"Error saving stocker data: {e}")
            raise

    async def clean_old_data(self, days: int = 30):
        """오래된 데이터 정리"""
        try:
            async with await self.get_connection() as conn:
                tables = ['stocker_port_settings', 'stocker_gas_type', 
                         'stocker_port_data', 'stocker_data']
                
                for table in tables:
                    await conn.execute(f'''
                        DELETE FROM {table} 
                        WHERE timestamp < datetime('now', '-{days} days')
                    ''')
                
                await conn.commit()
                self.logger.info(f"Cleaned stocker data older than {days} days")
        except Exception as e:
            self.logger.error(f"Error cleaning old data: {e}")
            raise