# database/stocker/stocker_db.py

import aiosqlite
import logging
import asyncio
from pathlib import Path

logger = logging.getLogger("StockerDB")

class StockerDB:
    def __init__(self, db_path: str = "database/stocker/stocker.db"):
        self.db_path = db_path
        self._init_lock = asyncio.Lock()
        self._initialized = False
        
        # DB 파일 디렉토리 생성
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    async def initialize(self):
        """데이터베이스 초기화 및 테이블 생성"""
        async with self._init_lock:
            if self._initialized:
                return
            
            async with aiosqlite.connect(self.db_path) as db:
                await db.executescript('''
                    CREATE TABLE IF NOT EXISTS stocker_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        bunker_id INTEGER,
                        stocker_id INTEGER,
                        alarm_code INTEGER,
                        x_pos INTEGER,
                        z_pos INTEGER
                    );

                    CREATE TABLE IF NOT EXISTS stocker_port_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        stocker_data_id INTEGER,
                        port_id TEXT,
                        barcode TEXT,
                        FOREIGN KEY (stocker_data_id) REFERENCES stocker_data(id)
                    );

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

                    -- 인덱스 생성
                    CREATE INDEX IF NOT EXISTS idx_stocker_timestamp 
                    ON stocker_data(timestamp);
                    
                    CREATE INDEX IF NOT EXISTS idx_stocker_ids 
                    ON stocker_data(bunker_id, stocker_id);
                ''')
                await db.commit()
                self._initialized = True
                logger.info("Stocker database initialized successfully")

    async def get_connection(self):
        """데이터베이스 연결 생성"""
        await self.initialize()
        return await aiosqlite.connect(self.db_path)