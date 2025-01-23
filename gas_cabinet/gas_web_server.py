from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
import asyncio
import json
import socket
from typing import List, Dict, Optional
from contextlib import asynccontextmanager
from pymodbus.client import AsyncModbusTcpClient
from datetime import datetime

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
        <title>Gas Cabinet Monitor</title>
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
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Gas Cabinet Monitoring System</h1>
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
                let formatted = {
                    basic: {
                        bunker_id: data.plc_data.bunker_id,
                        cabinet_id: data.plc_data.cabinet_id,
                        gas_type: data.plc_data.gas_type,
                        system_status: data.plc_data.system_status
                    },
                    sensors: data.plc_data.sensors,
                    heaters: data.plc_data.heaters,
                    bitStatus: {
                        cylinderDoor: data.bit_data.cylinder_door.states,
                        basicSignals: data.bit_data.basic_signals.states,
                        valves: data.bit_data.valves.states,
                        sensorsRelays: data.bit_data.sensors_relays.states,
                        portStatus: data.bit_data.port_status.states,
                        portA: {
                            operation: data.bit_data.port_a.operation.states,
                            valves: data.bit_data.port_a.valves.states
                        },
                        portB: {
                            operation: data.bit_data.port_b.operation.states,
                            valves: data.bit_data.port_b.valves.states,
                            details: data.bit_data.port_b.details.states,
                            additional: data.bit_data.port_b.additional.states
                        }
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

    # 데이터 조회
    async def get_data(self) -> Optional[Dict]:
        """데이터 조회"""
        if not self.connected:
            await self.connect()
            if not self.connected:
                return None
        
        try:
            async with self._lock:
                # PLC 데이터 영역 (0-99) 읽기
                plc_results = []
                for start in range(0, 100, 50):  # 0-99 범위의 데이터를 50개씩 나눠서 읽기
                    count = min(50, 100 - start)
                    result = await self.client.read_holding_registers(
                        address=start,
                        count=count,
                        slave=1
                    )
                    if result and not result.isError():
                        plc_results.extend(result.registers)
                    else:
                        logger.error(f"PLC 데이터 읽기 실패: {start}-{start+count}")
                        return None

                # 비트 데이터 영역 (100-117) 읽기
                bit_result = await self.client.read_holding_registers(
                    address=100,
                    count=18,
                    slave=1
                )
                
                if not bit_result or bit_result.isError():
                    logger.error("비트 데이터 읽기 실패")
                    return None

                plc_data = plc_results
                bit_data = bit_result.registers

                current_data = {
                    "plc_data": {
                        "bunker_id": plc_data[0],
                        "cabinet_id": plc_data[1],
                        "gas_type": plc_data[2:7],
                        "system_status": {
                            "machine_code": plc_data[7],
                            "alarm_code": plc_data[8]
                        },
                        "sensors": {
                            "pt1a": plc_data[10],
                            "pt2a": plc_data[11],
                            "pt1b": plc_data[12],
                            "pt2b": plc_data[13],
                            "pt3": plc_data[14],
                            "pt4": plc_data[15],
                            "weight_a": plc_data[16],
                            "weight_b": plc_data[17]
                        },
                        "heaters": {
                            "jacket_heater_a": plc_data[18],
                            "line_heater_a": plc_data[19],
                            "jacket_heater_b": plc_data[20],
                            "line_heater_b": plc_data[21]
                        },
                        "port_a": {
                            "torque": {
                                "cga_set": plc_data[24],
                                "cap_set": plc_data[25],
                                "cylinder_pos": plc_data[26]
                            },
                            "barcode": plc_data[30:60],
                            "gas_type": plc_data[90:95]
                        },
                        "port_b": {
                            "torque": {
                                "cga_set": plc_data[27],
                                "cap_set": plc_data[28],
                                "cylinder_pos": plc_data[29]
                            },
                            "barcode": plc_data[60:90],
                            "gas_type": plc_data[95:100]
                        }
                    },
                    "bit_data": {
                        "cylinder_door": {
                            "raw": bit_data[5],  # word_105는 bit_data의 5번째 인덱스
                            "states": self._get_word_105_states(bit_data[5])
                        },
                        "basic_signals": {
                            "raw": bit_data[0],
                            "states": self._get_word_200_states(bit_data[0])
                        },
                        "valves": {
                            "raw": bit_data[1],
                            "states": self._get_word_201_states(bit_data[1])
                        },
                        "sensors_relays": {
                            "raw": bit_data[2],
                            "states": self._get_word_202_states(bit_data[2])
                        },
                        "port_status": {
                            "raw": bit_data[3],
                            "states": {
                                "port_a": {
                                    "insert_request": bool(bit_data[3] & (1 << 0)),
                                    "insert_complete": bool(bit_data[3] & (1 << 1)),
                                    "remove_request": bool(bit_data[3] & (1 << 2)),
                                    "remove_complete": bool(bit_data[3] & (1 << 3))
                                },
                                "port_b": {
                                    "insert_request": bool(bit_data[3] & (1 << 8)),
                                    "insert_complete": bool(bit_data[3] & (1 << 9)),
                                    "remove_request": bool(bit_data[3] & (1 << 10)),
                                    "remove_complete": bool(bit_data[3] & (1 << 11))
                                }
                            }
                        },
                        "port_a": {
                            "operation": {
                                "raw": bit_data[10],
                                "states": self._get_word_210_states(bit_data[10])
                            },
                            "valves": {
                                "raw": bit_data[11],
                                "states": self._get_word_211_states(bit_data[11])
                            }
                        },
                        "port_b": {
                            "operation": {
                                "raw": bit_data[15],
                                "states": self._get_word_220_states(bit_data[15])
                            },
                            "valves": {
                                "raw": bit_data[16],
                                "states": self._get_word_221_states(bit_data[16])
                            },
                            "details": {
                                "raw": bit_data[16],
                                "states": self._get_word_225_states(bit_data[16])
                            },
                            "additional": {
                                "raw": bit_data[17],
                                "states": self._get_word_226_states(bit_data[17])
                            }
                        }
                    }
                }

                # 데이터가 변경되었는지 확인
                # if self.last_data != current_data:
                #     self.last_data = current_data
                return current_data
                # return None

        except Exception as e:
            logger.error(f"데이터 수신 오류: {e}")
            self.connected = False
            return None
    
    def _get_word_105_states(self, word: int) -> Dict[str, bool]:
        return {
            "port_a_cylinder": bool(word & (1 << 0)),  # [A] Port 실린더 유무
            "port_b_cylinder": bool(word & (1 << 1)),  # [B] Port 실린더 유무
            "door_open": bool(word & (1 << 2)),        # Door Open 완료
            "door_close": bool(word & (1 << 3))        # Door Close 완료
        }

    def _get_word_200_states(self, word: int) -> Dict[str, bool]:
        """기본 신호 상태 해석 (100.00-100.07)"""
        return {
            "emg_signal": bool(word & (1 << 0)),        # EMG Signal
            "heart_bit": bool(word & (1 << 1)),         # Heart Bit
            "run_stop_signal": bool(word & (1 << 2)),   # Run/Stop Signal
            "server_connected": bool(word & (1 << 3)),   # Server Connected Bit
            "t_lamp_red": bool(word & (1 << 4)),        # T-LAMP RED
            "t_lamp_yellow": bool(word & (1 << 5)),     # T-LAMP YELLOW
            "t_lamp_green": bool(word & (1 << 6)),      # T-LAMP GREEN
            "touch_manual": bool(word & (1 << 7))       # Touch 수동동작中 Signal
        }

    def _get_word_201_states(self, word: int) -> Dict[str, bool]:
        """밸브 상태 해석 (101.00-101.12)"""
        return {
            "av1a": bool(word & (1 << 0)),
            "av2a": bool(word & (1 << 1)),
            "av3a": bool(word & (1 << 2)),
            "av4a": bool(word & (1 << 3)),
            "av5a": bool(word & (1 << 4)),
            "av1b": bool(word & (1 << 5)),
            "av2b": bool(word & (1 << 6)),
            "av3b": bool(word & (1 << 7)),
            "av4b": bool(word & (1 << 8)),
            "av5b": bool(word & (1 << 9)),
            "av7": bool(word & (1 << 10)),
            "av8": bool(word & (1 << 11)),
            "av9": bool(word & (1 << 12))
        }

    def _get_word_202_states(self, word: int) -> Dict[str, bool]:
        """센서 및 릴레이 상태 해석 (102.00-102.08)"""
        return {
            "jacket_heater_a": bool(word & (1 << 0)),   # JACKET HEATER A RELAY
            "line_heater_a": bool(word & (1 << 1)),     # LINE HEATER A RELAY
            "jacket_heater_b": bool(word & (1 << 2)),   # JACKET HEATER B RELAY
            "line_heater_b": bool(word & (1 << 3)),     # LINE HEATER B RELAY
            "gas_leak_shutdown": bool(word & (1 << 4)), # GAS LEAK SHUT DOWN
            "vmb_stop": bool(word & (1 << 5)),         # VMB STOP SIGNAL
            "uv_ir_sensor": bool(word & (1 << 6)),     # UV/IR SENSOR
            "high_temp_sensor": bool(word & (1 << 7)), # HIGH TEMP SENSOR
            "smoke_sensor": bool(word & (1 << 8))      # SMOKE SENSOR
        }

    def _get_word_210_states(self, word: int) -> Dict[str, bool]:
        """A Port 작업 상태 해석 (110.00-110.12)"""
        return {
            "close_cylinder": bool(word & (1 << 0)),
            "first_purge_before": bool(word & (1 << 1)),
            "decompression_test": bool(word & (1 << 2)),
            "second_purge_before": bool(word & (1 << 3)),
            "exchange_cylinder": bool(word & (1 << 4)),
            "first_purge_after": bool(word & (1 << 5)),
            "pressure_test": bool(word & (1 << 6)),
            "second_purge_after": bool(word & (1 << 7)),
            "purge_completed": bool(word & (1 << 8)),
            "prepare_supply": bool(word & (1 << 9)),
            "av3_control": bool(word & (1 << 10)),
            "gas_supply": bool(word & (1 << 11)),
            "ready_supply": bool(word & (1 << 12))
        }

    def _get_word_211_states(self, word: int) -> Dict[str, bool]:
        """A Port 밸브 상태 해석 (111.00-111.15)"""
        return {
            "cylinder_ready": bool(word & (1 << 0)),
            "cga_disconnect": bool(word & (1 << 1)),
            "cga_connect": bool(word & (1 << 2)),
            "valve_open_complete": bool(word & (1 << 3)),
            "valve_close_complete": bool(word & (1 << 4)),
            "valve_open_status": bool(word & (1 << 5)),
            "lift_ready": bool(word & (1 << 6)),
            "lift_moving_up": bool(word & (1 << 7)),
            "lift_moving_down": bool(word & (1 << 8)),
            "cga_separating": bool(word & (1 << 9)),
            "cga_connecting": bool(word & (1 << 10)),
            "cap_separating": bool(word & (1 << 11)),
            "valve_opening": bool(word & (1 << 12)),
            "valve_closing": bool(word & (1 << 13)),
            "cylinder_aligning": bool(word & (1 << 14)),
            "cylinder_turning": bool(word & (1 << 15))
        }

    def _get_word_220_states(self, word: int) -> Dict[str, bool]:
        """B Port 작업 상태 해석 (115.00-115.12)"""
        return {
            "close_cylinder": bool(word & (1 << 0)),
            "first_purge_before": bool(word & (1 << 1)),
            "decompression_test": bool(word & (1 << 2)),
            "second_purge_before": bool(word & (1 << 3)),
            "exchange_cylinder": bool(word & (1 << 4)),
            "first_purge_after": bool(word & (1 << 5)),
            "pressure_test": bool(word & (1 << 6)),
            "second_purge_after": bool(word & (1 << 7)),
            "purge_completed": bool(word & (1 << 8)),
            "prepare_supply": bool(word & (1 << 9)),
            "av3_control": bool(word & (1 << 10)),
            "gas_supply": bool(word & (1 << 11)),
            "ready_supply": bool(word & (1 << 12))
        }

    def _get_word_221_states(self, word: int) -> Dict[str, bool]:
        """B Port 밸브 상태 해석 (221.00-221.15)"""
        states = {f"av{i+1}b": bool(word & (1 << i)) for i in range(5)}  # AV1B-AV5B
        # AV7-AV9 (13-15 비트)
        for i, num in enumerate(range(13, 16)):
            states[f"av{7+i}"] = bool(word & (1 << num))
        return states

    def _get_word_225_states(self, word: int) -> Dict[str, bool]:
        """B Port 상세 상태 해석 (116.00-116.15)"""
        return {
            "cylinder_ready": bool(word & (1 << 0)),
            "cga_disconnect": bool(word & (1 << 1)),
            "cga_connect": bool(word & (1 << 2)),
            "valve_open_complete": bool(word & (1 << 3)),
            "valve_close_complete": bool(word & (1 << 4)),
            "valve_open_status": bool(word & (1 << 5)),
            "lift_ready": bool(word & (1 << 6)),
            "lift_moving_up": bool(word & (1 << 7)),
            "lift_moving_down": bool(word & (1 << 8)),
            "cga_separating": bool(word & (1 << 9)),
            "cga_connecting": bool(word & (1 << 10)),
            "cap_separating": bool(word & (1 << 11)),
            "valve_opening": bool(word & (1 << 12)),
            "valve_closing": bool(word & (1 << 13)),
            "cylinder_aligning": bool(word & (1 << 14)),
            "cylinder_turning": bool(word & (1 << 15))
        }

    def _get_word_226_states(self, word: int) -> Dict[str, bool]:
        """B Port 추가 상태 해석 (117.00-117.02)"""
        return {
            "cylinder_turn_complete": bool(word & (1 << 0)),
            "cylinder_clamp_complete": bool(word & (1 << 1)),
            "cga_connect_status": bool(word & (1 << 2))
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
    app.state.update_task = asyncio.create_task(update_client_data(modbus_client))
    
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

@app.get("/api/cabinet/data")
async def get_cabinet_data():
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
        print("=== Gas Cabinet Web Server 시작 ===")
        
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