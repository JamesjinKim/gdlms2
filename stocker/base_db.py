# base_db.py
import aiosqlite
import logging
import asyncio
import os
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class BaseDB(ABC):
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_lock = asyncio.Lock()
        self._initialized = False
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # DB 파일 디렉토리 생성
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    async def get_connection(self) -> aiosqlite.Connection:
        """데이터베이스 연결 생성"""
        await self.initialize()
        return await aiosqlite.connect(self.db_path)

    @abstractmethod
    async def initialize(self):
        """데이터베이스 초기화 및 테이블 생성"""
        pass

    async def clean_old_data(self, days: int = 30):
        """오래된 데이터 정리"""
        pass

    async def execute_query(self, query: str, params: tuple = ()) -> Optional[List[Dict]]:
        """SQL 쿼리 실행"""
        try:
            async with await self.get_connection() as conn:
                conn.row_factory = aiosqlite.Row
                cursor = await conn.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
                await conn.commit()
                return None
        except Exception as e:
            self.logger.error(f"Query execution error: {e}")
            raise

class AlarmCodeMixin:
    """알람 코드 관리 믹스인"""
    async def insert_alarm_codes(self, alarm_data: List[tuple], table_name: str):
        """알람 코드 데이터 삽입"""
        try:
            query = f"""
                INSERT INTO {table_name} 
                (alarm_code, alarm_comment, category)
                VALUES (?, ?, ?)
            """
            await self.execute_query(query, alarm_data)
            self.logger.info(f"Inserted {len(alarm_data)} alarm codes into {table_name}")
            return True
        except Exception as e:
            self.logger.error(f"Error inserting alarm codes: {e}")
            return False

    async def get_alarm_codes(self, table_name: str) -> List[Dict]:
        """알람 코드 조회"""
        query = f"SELECT * FROM {table_name} ORDER BY alarm_code"
        return await self.execute_query(query)