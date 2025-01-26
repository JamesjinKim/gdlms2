from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
from typing import List, Dict, Optional
from contextlib import asynccontextmanager
from pymodbus.client import AsyncModbusTcpClient
from stocker_alarm_codes import stocker_alarm_code

# 로깅 설정
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)
logger = logging.getLogger("GasWebServer")

# HTML 템플릿 (이전과 동일하되 스타일과 기능을 개선)
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Stocker Monitor</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                margin: 0;
                padding: 20px;
                font-family: Arial, sans-serif;
                background: #f5f5f5;
            }
            .container { 
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                border-bottom: 2px solid #eee;
                padding-bottom: 10px;
            }
            .status {
                margin: 20px 0;
                padding: 15px;
                background: #f8f9fa;
                border-radius: 4px;
                border-left: 4px solid #6c757d;
            }
            .status span {
                font-weight: bold;
            }
            .data-display {
                background: #fff;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-top: 20px;
            }
            .data-display h3 {
                color: #495057;
                margin-top: 0;
            }
            pre {
                white-space: pre-wrap;
                word-wrap: break-word;
                background: #f8f9fa;
                padding: 15px;
                border-radius: 4px;
                border: 1px solid #e9ecef;
                font-family: monospace;
                font-size: 14px;
            }
            .connected { color: #28a745; }
            .disconnected { color: #dc3545; }
            .error { color: #dc3545; }
            
            /* 새로운 스타일 추가 */
            .alarm {
                background-color: #fff3cd;
                border: 1px solid #ffeeba;
                color: #856404;
                padding: 10px;
                margin-top: 10px;
                border-radius: 4px;
                display: none;
            }
            .indicator {
                display: inline-block;
                width: 10px;
                height: 10px;
                border-radius: 50%;
                margin-right: 5px;
            }
            .indicator.on { background-color: #28a745; }
            .indicator.off { background-color: #dc3545; }

            .bit-data {
                margin-top: 20px;
                padding: 15px;
                background: #f8f9fa;
                border-left: 4px solid #28a745;
            }
            .bit-status {
                display: inline-block;
                margin-right: 10px;
                padding: 2px 6px;
                border-radius: 3px;
                background: #e9ecef;
            }
            .bit-true { color: #28a745; }
            .bit-false { color: #dc3545; }

        </style>
    </head>
    <body>
        <div class="container">
            <h1>Stocker Monitoring System</h1>
            <div class="status">
                Connection Status: <span id="connection-status">Disconnected</span>
            </div>
            <div class="alarm" id="alarm-container">
                <strong>Alarm:</strong> <span id="alarm-message"></span>
            </div>
            <div class="data-display">
                <h3>Real-time Data:</h3>
                <pre id="data-container">Waiting for data...</pre>
            </div>
        </div>

        <script>
            const ws = new WebSocket("ws://localhost:5001/ws");
            const status = document.getElementById('connection-status');
            const dataContainer = document.getElementById('data-container');
            const alarmContainer = document.getElementById('alarm-container');
            const alarmMessage = document.getElementById('alarm-message');
            
            function formatData(data) {
                console.log("Received data:", data); // 디버깅용
                let formatted = {
                    "Stocker PLC Data": {
                        "기본 정보": {
                            "Bunker ID": data.plc_data.bunker_id,
                            "Stocker ID": data.plc_data.stocker_id,
                            "가스 종류": data.plc_data.gas_type
                        },
                        "시스템 상태": {
                            "알람 코드": data.plc_data.system_status.alarm_code,
                            "알람 메시지": data.plc_data.system_status.alarm_message
                        },
                        "위치 정보": {
                            "X축 위치": data.plc_data.position.x_axis,
                            "Z축 위치": data.plc_data.position.z_axis
                        },
                        "토크 설정": {
                            "Cap 분리": data.plc_data.torque.cap_open,
                            "Cap 체결": data.plc_data.torque.cap_close
                        },
                        "Port A": {
                            "바코드": data.plc_data.port_a.barcode,
                            "가스 종류": data.plc_data.port_a.gas_type
                        },
                        "Port B": {
                            "바코드": data.plc_data.port_b.barcode,
                            "가스 종류": data.plc_data.port_b.gas_type
                        }
                    },
                    "Stocker Bit Data": {
                        "[100] 기본 신호": data.bit_data.word_100.states,
                        "[105] 도어/실린더 상태": data.bit_data.word_105.states,
                        "[110] A Port 작업 상태": data.bit_data.word_110.states,
                        "[111] A Port 상세 상태": data.bit_data.word_111.states,
                        "[115] B Port 작업 상태": data.bit_data.word_115.states,
                        "[116] B Port 상세 상태": data.bit_data.word_116.states
                    }
                };
                return JSON.stringify(formatted, null, 2);
            }
            
            ws.onopen = () => {
                status.textContent = 'Connected';
                status.className = 'connected';
            };

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                dataContainer.textContent = formatData(data);
                
                // 알람 체크 및 표시
                if (data.plc_data.status.alarm_code !== 0) {
                    alarmContainer.style.display = 'block';
                    alarmMessage.textContent = `Alarm Code ${data.plc_data.status.alarm_code}`;
                    alarmMessage.textContent = `${data.plc_data.status.alarm_code} - ${data.plc_data.status.alarm_message}`;
                } else {
                    alarmContainer.style.display = 'none';
                }
            };

            ws.onclose = () => {
                status.textContent = 'Disconnected';
                status.className = 'disconnected';
                setTimeout(reconnect, 5000);
            };

            ws.onerror = (error) => {
                status.textContent = 'Error';
                status.className = 'error';
                console.error('WebSocket error:', error);
            };
            
            function reconnect() {
                if (ws.readyState === WebSocket.CLOSED) {
                    status.textContent = 'Reconnecting...';
                    ws = new WebSocket("ws://localhost:5001/ws");
                }
            }
            
            // 페이지 종료 시 연결 정리
            window.addEventListener('beforeunload', () => {
                if (ws) {
                    ws.close();
                }
            });
        </script>
    </body>
</html>
"""

class ModbusDataClient:
    def __init__(self):
        self.client = None
        self.connected = False
        self.unit = 1
        self.last_data = None
        self.running = True
        self._lock = asyncio.Lock()
    
    async def connect(self):
        """Modbus 클라이언트 연결"""
        try:
            async with self._lock:
                if self.client is None or not self.client.connected:
                    self.client = AsyncModbusTcpClient('127.0.0.1', port=5020)
                    self.connected = await self.client.connect()
                    if self.connected:
                        logger.info("Modbus 서버에 연결됨")
                    else:
                        logger.error("Modbus 서버 연결 실패")
                        await asyncio.sleep(5)
        except Exception as e:
            logger.error(f"연결 오류: {e}")
            self.connected = False
            await asyncio.sleep(5)

    async def get_data(self) -> Optional[Dict]:
        """데이터 조회"""
        if not self.connected:
            await self.connect()
            if not self.connected:
                return None
        
        try:
            async with self._lock:
                # 더 작은 단위로 데이터 읽기
                results = []
                for start in range(0, 140, 50):
                    count = min(50, 140 - start)
                    result = await self.client.read_holding_registers(
                        address=start,
                        count=count,
                        slave=1
                    )
                    if result and not result.isError():
                        results.extend(result.registers)
                    else:
                        logger.error(f"레지스터 읽기 실패: {start}-{start+count}")
                        return None

                # 비트 데이터 읽기   self.client.read_holding_registers(
                bit_results = await self.client.read_coils(
                    address=0,
                    count=18,
                    slave=1
                )
                
                if not bit_results or bit_results.isError():
                    logger.error("비트 데이터 읽기 실패")
                    return None

                plc_data = results
                current_bits = bit_results.bits

                if not hasattr(self, '_last_bits') or self._last_bits != current_bits:
                    logger.info("비트 데이터 변경 감지")
                    logger.info(f"현재 비트 데이터: {current_bits}")
                    if hasattr(self, '_last_bits'):
                        logger.info(f"이전 비트 데이터: {self._last_bits}")
                    self._last_bits = current_bits
                    
                # 데이터 변환 로직
                current_data = {
                    "plc_data": {
                        "bunker_id": plc_data[0] if len(plc_data) > 0 else 0,
                        "stocker_id": plc_data[1] if len(plc_data) > 1 else 0,
                        "gas_type": plc_data[2:7] if len(plc_data) > 6 else [0]*5,
                        "system_status": {
                            "alarm_code": plc_data[8] if len(plc_data) > 8 else 0,
                            "alarm_message": stocker_alarm_code.get_description(plc_data[8] if len(plc_data) > 8 else 0)
                        },
                        "position": {
                            "x_axis": plc_data[10] if len(plc_data) > 10 else 0,
                            "z_axis": plc_data[11] if len(plc_data) > 11 else 0
                        },
                        "torque": {
                            "cap_open": plc_data[12] if len(plc_data) > 12 else 0,
                            "cap_close": plc_data[13] if len(plc_data) > 13 else 0
                        },
                        "port_a": {
                            "barcode": ''.join([chr(x) if 32 <= x <= 126 else '?' for x in plc_data[30:60]]),
                            "gas_type": plc_data[90:95] if len(plc_data) > 94 else [0]*5
                        },
                        "port_b": {
                            "barcode": ''.join([chr(x) if 32 <= x <= 126 else '?' for x in plc_data[60:90]]),
                            "gas_type": plc_data[95:100] if len(plc_data) > 99 else [0]*5
                        }
                    },
                    "bit_data": {
                        "word_100": {
                            "raw": int(''.join(['1' if x else '0' for x in bit_results.bits[0:8]]), 2),
                            "states": {
                                "EMG Signal": bit_results.bits[0],
                                "Heart Bit": bit_results.bits[1],
                                "Run/Stop Signal": bit_results.bits[2],
                                "Server Connected Bit": bit_results.bits[3],
                                "T-LAMP RED": bit_results.bits[4],
                                "T-LAMP YELLOW": bit_results.bits[5],
                                "T-LAMP GREEN": bit_results.bits[6],
                                "Touch 수동동작中 Signal": bit_results.bits[7]
                            }
                        },
                        "word_105": {
                            "raw": int(''.join(['1' if x else '0' for x in bit_results.bits[16:20]]), 2),
                            "states": {
                                "[A] Port 실린더 유무": bit_results.bits[16],
                                "[B] Port 실린더 유무": bit_results.bits[17],
                                "Door Open 완료": bit_results.bits[18],
                                "Door Close 완료": bit_results.bits[19]
                            }
                        },
                        "word_110": {
                            "raw": int(''.join(['1' if x else '0' for x in bit_results.bits[32:45]]), 2),
                            "states": {
                                "[A] Close the Cylinder": bit_results.bits[32],
                                "[A] 1st Purge before Exchange": bit_results.bits[33],
                                "[A] Decompression Test": bit_results.bits[34],
                                "[A] 2nd Purge before Exchange": bit_results.bits[35],
                                "[A] Exchange Cylinder": bit_results.bits[36],
                                "[A] 1st Purge after Exchange": bit_results.bits[37],
                                "[A] Pressure Test": bit_results.bits[38],
                                "[A] 2nd Purge after Exchange": bit_results.bits[39],
                                "[A] Purge Completed": bit_results.bits[40],
                                "[A] Prepare to Supply": bit_results.bits[41],
                                "[A] Gas Supply AV3 Open/Close Choose": bit_results.bits[42],
                                "[A] Gas Supply": bit_results.bits[43],
                                "[A] Ready to Supply": bit_results.bits[44]
                            }
                        },
                        "word_111": {
                            "raw": int(''.join(['1' if x else '0' for x in bit_results.bits[45:61]]), 2),
                            "states": {
                                "[A] Cyclinder Ready": bit_results.bits[45],
                                "[A] CGA Disconnect Complete": bit_results.bits[46],
                                "[A] CGA Connect Complete": bit_results.bits[47],
                                "[A] Cylinder Valve Open Complete": bit_results.bits[48],
                                "[A] Cylinder Valve Close Complete": bit_results.bits[49],
                                "[A] Cylinder Valve Open Status": bit_results.bits[50],
                                "[A] Cylinder Lift Unit Ready": bit_results.bits[51],
                                "[A] Cylinder Lift Unit Moving Up": bit_results.bits[52],
                                "[A] Cylinder Lift Unit Moving Down": bit_results.bits[53],
                                "[A] CGA Separation In Progress": bit_results.bits[54],
                                "[A] CGA Connection In Progress": bit_results.bits[55],
                                "[A] Cylinder Cap Separation In Progress": bit_results.bits[56],
                                "[A] Cylinder Valve Open In Progress": bit_results.bits[57],
                                "[A] Cylinder Valve Close In Progress": bit_results.bits[58],
                                "[A] Cylinder Alignment In Progress": bit_results.bits[59],
                                "[A] Cylinder Turn In Progress": bit_results.bits[60]
                            }
                        },
                        "word_115": {
                            "raw": int(''.join(['1' if x else '0' for x in bit_results.bits[61:74]]), 2),
                            "states": {
                                "[B] Close the Cylinder": bit_results.bits[61],
                                "[B] 1st Purge before Exchange": bit_results.bits[62],
                                "[B] Decompression Test": bit_results.bits[63],
                                "[B] 2nd Purge before Exchange": bit_results.bits[64],
                                "[B] Exchange Cylinder": bit_results.bits[65],
                                "[B] 1st Purge after Exchange": bit_results.bits[66],
                                "[B] Pressure Test": bit_results.bits[67],
                                "[B] 2nd Purge after Exchange": bit_results.bits[68],
                                "[B] Purge Completed": bit_results.bits[69],
                                "[B] Prepare to Supply": bit_results.bits[70],
                                "[B] Gas Supply AV3 Open/Close Choose": bit_results.bits[71],
                                "[B] Gas Supply": bit_results.bits[72],
                                "[B] Ready to Supply": bit_results.bits[73]
                            }
                        },
                        "word_116": {
                            "raw": int(''.join(['1' if x else '0' for x in bit_results.bits[74:90]]), 2),
                            "states": {
                                "[B] Cylinder Ready": bit_results.bits[74],
                                "[B] CGA Disconnect Complete": bit_results.bits[75],
                                "[B] CGA Connect Complete": bit_results.bits[76],
                                "[B] Cylinder Valve Open Complete": bit_results.bits[77],
                                "[B] Cylinder Valve Close Complete": bit_results.bits[78],
                                "[B] Cylinder Valve Open Status": bit_results.bits[79],
                                "[B] Cylinder Lift Unit Ready": bit_results.bits[80],
                                "[B] Cylinder Lift Unit Moving Up": bit_results.bits[81],
                                "[B] Cylinder Lift Unit Moving Down": bit_results.bits[82],
                                "[B] CGA Separation In Progress": bit_results.bits[83],
                                "[B] CGA Connection In Progress": bit_results.bits[84],
                                "[B] Cylinder Cap Separation In Progress": bit_results.bits[85],
                                "[B] Cylinder Valve Open In Progress": bit_results.bits[86],
                                "[B] Cylinder Valve Close In Progress": bit_results.bits[87],
                                "[B] Cylinder Alignment In Progress": bit_results.bits[88],
                                "[B] Cylinder Turn In Progress": bit_results.bits[89]
                            }
                        }
                    }
                }

                # 데이터가 변경되었는지 확인
                if self.last_data != current_data:
                    self.last_data = current_data
                    return current_data
                return None

        except Exception as e:
            logger.error(f"데이터 수신 오류: {e}")
            self.connected = False
            return None
    
    def _get_word_100_states(self, word: int) -> Dict[str, bool]:
        return {
            "emg_signal": bool(word & (1 << 0)),
            "heart_bit": bool(word & (1 << 1)),
            "run_stop_signal": bool(word & (1 << 2)),
            "server_connected": bool(word & (1 << 3)),
            "t_lamp_red": bool(word & (1 << 4)),
            "t_lamp_yellow": bool(word & (1 << 5)),
            "t_lamp_green": bool(word & (1 << 6)),
            "touch_manual": bool(word & (1 << 7))
        }

    def _get_word_105_states(self, word: int) -> Dict[str, bool]:
        return {
            "port_a_cylinder": bool(word & (1 << 0)),
            "port_b_cylinder": bool(word & (1 << 1)),
            "port_a_worker_door_open": bool(word & (1 << 2)),
            "port_a_worker_door_close": bool(word & (1 << 3)),
            "port_a_bunker_door_open": bool(word & (1 << 4)),
            "port_a_bunker_door_close": bool(word & (1 << 5)),
            "port_b_worker_door_open": bool(word & (1 << 6)),
            "port_b_worker_door_close": bool(word & (1 << 7)),
            "port_b_bunker_door_open": bool(word & (1 << 8)),
            "port_b_bunker_door_close": bool(word & (1 << 9))
        }

    def _get_word_110_states(self, word: int) -> Dict[str, bool]:
        return {
            "port_a_cap_open_complete": bool(word & (1 << 0)),
            "port_a_cap_close_complete": bool(word & (1 << 1)),
            "port_a_worker_door_open_complete": bool(word & (1 << 2)),
            "port_a_worker_door_close_complete": bool(word & (1 << 3)),
            "port_a_worker_input_ready": bool(word & (1 << 4)),
            "port_a_worker_input_complete": bool(word & (1 << 5)),
            "port_a_worker_output_ready": bool(word & (1 << 6)),
            "port_a_worker_output_complete": bool(word & (1 << 7)),
            "port_a_bunker_door_open_complete": bool(word & (1 << 8)),
            "port_a_bunker_door_close_complete": bool(word & (1 << 9)),
            "port_a_bunker_input_ready": bool(word & (1 << 10)),
            "port_a_bunker_input_complete": bool(word & (1 << 11)),
            "port_a_bunker_output_ready": bool(word & (1 << 12)),
            "port_a_bunker_output_complete": bool(word & (1 << 13)),
            "port_a_cylinder_align_in_progress": bool(word & (1 << 14)),
            "port_a_cylinder_align_complete": bool(word & (1 << 15))
        }

    def _get_word_111_states(self, word: int) -> Dict[str, bool]:
        return {
            "port_a_cap_opening": bool(word & (1 << 0)),
            "port_a_cap_closing": bool(word & (1 << 1)),
            "port_a_x_axis_moving": bool(word & (1 << 2)),
            "port_a_x_axis_complete": bool(word & (1 << 3)),
            "port_a_finding_cap": bool(word & (1 << 4)),
            "port_a_finding_cylinder_neck": bool(word & (1 << 5)),
            "port_a_worker_door_opening": bool(word & (1 << 6)),
            "port_a_worker_door_closing": bool(word & (1 << 7)),
            "port_a_bunker_door_opening": bool(word & (1 << 8)),
            "port_a_bunker_door_closing": bool(word & (1 << 9))
        }

    def _get_word_115_states(self, word: int) -> Dict[str, bool]:
        return {
            "port_b_cap_open_complete": bool(word & (1 << 0)),
            "port_b_cap_close_complete": bool(word & (1 << 1)),
            "port_b_worker_door_open_complete": bool(word & (1 << 2)),
            "port_b_worker_door_close_complete": bool(word & (1 << 3)),
            "port_b_worker_input_ready": bool(word & (1 << 4)),
            "port_b_worker_input_complete": bool(word & (1 << 5)),
            "port_b_worker_output_ready": bool(word & (1 << 6)),
            "port_b_worker_output_complete": bool(word & (1 << 7)),
            "port_b_bunker_door_open_complete": bool(word & (1 << 8)),
            "port_b_bunker_door_close_complete": bool(word & (1 << 9)),
            "port_b_bunker_input_ready": bool(word & (1 << 10)),
            "port_b_bunker_input_complete": bool(word & (1 << 11)),
            "port_b_bunker_output_ready": bool(word & (1 << 12)),
            "port_b_bunker_output_complete": bool(word & (1 << 13)),
            "port_b_cylinder_align_in_progress": bool(word & (1 << 14)),
            "port_b_cylinder_align_complete": bool(word & (1 << 15))
        }

    def _get_word_116_states(self, word: int) -> Dict[str, bool]:
        return {
            "port_b_cap_opening": bool(word & (1 << 0)),
            "port_b_cap_closing": bool(word & (1 << 1)),
            "port_b_x_axis_moving": bool(word & (1 << 2)),
            "port_b_x_axis_complete": bool(word & (1 << 3)),
            "port_b_finding_cap": bool(word & (1 << 4)),
            "port_b_finding_cylinder_neck": bool(word & (1 << 5)),
            "port_b_worker_door_opening": bool(word & (1 << 6)),
            "port_b_worker_door_closing": bool(word & (1 << 7)),
            "port_b_bunker_door_opening": bool(word & (1 << 8)),
            "port_b_bunker_door_closing": bool(word & (1 << 9))
        }

    async def close(self):
        try:
            self.running = False  # 실행 상태 플래그 해제
            if self.client and hasattr(self.client, 'connected') and self.client.connected:
                await self.client.close()
                print("Modbus 클라이언트가 정상적으로 종료되었습니다.")
            self.connected = False
        except Exception as e:
            print(f"Modbus 클라이언트 종료 중 오류: {e}")
        finally:
            self.client = None

    async def update_client_data(self):
        while self.running:  # running 플래그 확인
            try:
                data = await self.get_data()
                if data:
                    await manager.broadcast(data)
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"데이터 업데이트 오류: {e}")
                await asyncio.sleep(1)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket):
        async with self._lock:
            self.active_connections.append(websocket)
            print(f"WebSocket 클라이언트 연결됨. 현재 연결 수: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"WebSocket 클라이언트 연결 해제. 현재 연결 수: {len(self.active_connections)}")

    async def broadcast(self, data: dict):
        for connection in self.active_connections[:]:
            try:
                await connection.send_json(data)
            except Exception as e:
                print(f"브로드캐스트 오류: {e}")
                await self.disconnect(connection)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("애플리케이션 시작중...")
    modbus_client = ModbusDataClient()
    app.state.modbus_client = modbus_client
    app.state.update_task = asyncio.create_task(modbus_client.update_client_data())  # 수정된 부분
    try:
        yield
    except Exception as e:
        print(f"라이프스팬 오류: {e}")
    finally:
        print("애플리케이션 종료중...")
        if hasattr(app.state, 'modbus_client'):
            app.state.modbus_client.running = False
            if app.state.modbus_client.client:
                try:
                    await app.state.modbus_client.close()
                except Exception as e:
                    print(f"Modbus 클라이언트 종료 오류: {e}")

        if hasattr(app.state, 'update_task'):
            try:
                app.state.update_task.cancel()
                try:
                    await app.state.update_task
                except asyncio.CancelledError:
                    pass
            except Exception as e:
                print(f"업데이트 태스크 종료 오류: {e}")

app = FastAPI(lifespan=lifespan)
manager = ConnectionManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

async def update_client_data(modbus_client):
    while True:
        try:
            data = await modbus_client.get_data()
            if data:
                await manager.broadcast(data)
            await asyncio.sleep(1)
        except Exception as e:
            print(f"데이터 업데이트 오류: {e}")
            await asyncio.sleep(1)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        await manager.connect(websocket)
        
        while True:
            try:
                if not app.state.modbus_client.running:
                    break
                    
                data = await app.state.modbus_client.get_data()
                if data:
                    await websocket.send_json(data)
                await asyncio.sleep(0.5)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"데이터 처리 오류: {e}")
                break
    finally:
        await manager.disconnect(websocket)
        print("WebSocket 연결이 종료되었습니다.")

@app.get("/api/stocker/data")
async def get_stocker_data():
    """현재 캐비닛 데이터 조회"""
    try:
        data = await app.state.modbus_client.get_data()
        return {"success": True, "data": data}
    except Exception as e:
        return {"success": False, "error": str(e)}
    
# 루트 경로에 HTML 페이지 제공
@app.get("/", response_class=HTMLResponse)
async def get():
    return html

if __name__ == "__main__":
    try:
        import uvicorn
        print("=== Stocker Web Server 시작 ===")
        
        # uvicorn 설정
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=5001,
            loop="asyncio",
            log_level="info"
        )
        server = uvicorn.Server(config)

        # 메인 실행
        async def main():
            try:
                await server.serve()
            except Exception as e:
                print(f"서버 실행 중 오류: {e}")

        # 서버 실행
        asyncio.run(main())

    except KeyboardInterrupt:
        print("\n=== 서버 종료 요청됨 ===")
        if hasattr(app.state, 'update_task'):
            app.state.update_task.cancel()
        if hasattr(app.state, 'modbus_client'):
            app.state.modbus_client.running = False
    except Exception as e:
        print(f"\n예기치 않은 오류: {e}")
    finally:
        print("=== 서버가 종료되었습니다 ===")