from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
from typing import List, Dict, Optional
from contextlib import asynccontextmanager
from pymodbus.client import AsyncModbusTcpClient
from gas_cabinet_alarm_code import gas_cabinet_alarm_code

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
                console.log("Received data:", data); // 디버깅용
                let formatted = {
                    "Gas Cabinet PLC Data Area": {
                        "기본 정보": {
                            "Bunker ID": data.plc_data.bunker_id,
                            "Cabinet ID": data.plc_data.cabinet_id,
                            "가스 종류": data.plc_data.gas_type
                        },
                        "시스템 상태": data.plc_data.status,
                        "센서 데이터": data.plc_data.sensors,
                        "히터 상태": data.plc_data.heaters,
                        "Port A": data.plc_data.port_a,
                        "Port B": data.plc_data.port_b
                    },
                    "Gas Cabinet Bit Area Data": {
                        "[100] 기본 신호": data.bit_data.word_100.states,
                        "[101] 밸브 상태": data.bit_data.word_101.states,
                        "[102] 센서 및 릴레이": data.bit_data.word_102.states,
                        "[103] Port 요청 상태": data.bit_data.word_103.states,
                        "[105] 실린더 및 도어": data.bit_data.word_105.states,
                        "[110] A Port 작업": data.bit_data.word_110.states,
                        "[115] B Port 작업": data.bit_data.word_115.states,
                        "[116] B Port 상세": data.bit_data.word_116.states,
                        "[117] B Port 추가": data.bit_data.word_117.states
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

                # 비트 데이터 읽기
                bit_result = await self.client.read_holding_registers(
                    address=200,
                    count=27,
                    slave=1
                )
                
                if not bit_result or bit_result.isError():
                    logger.error("비트 데이터 읽기 실패")
                    return None

                plc_data = results
                bit_data = bit_result.registers

                current_data = {
                    "plc_data": {
                        "bunker_id": plc_data[0] if len(plc_data) > 0 else 0,
                        "cabinet_id": plc_data[1] if len(plc_data) > 1 else 0,
                        "gas_type": plc_data[2:7] if len(plc_data) > 6 else [0]*5,

                        "status": {
                            "machine_code": plc_data[7] if len(plc_data) > 7 else 0,
                            "alarm_code": plc_data[8] if len(plc_data) > 8 else 0,
                            "alarm_message": gas_cabinet_alarm_code.get_description(plc_data[8] if len(plc_data) > 8 else 0)
                        },
                        
                        "sensors": {
                            "pt1a": plc_data[10] if len(plc_data) > 10 else 0,
                            "pt2a": plc_data[11] if len(plc_data) > 11 else 0,
                            "pt1b": plc_data[12] if len(plc_data) > 12 else 0,
                            "pt2b": plc_data[13] if len(plc_data) > 13 else 0,
                            "pt3": plc_data[14] if len(plc_data) > 14 else 0,
                            "pt4": plc_data[15] if len(plc_data) > 15 else 0,
                            "weight_a": plc_data[16] if len(plc_data) > 16 else 0,
                            "weight_b": plc_data[17] if len(plc_data) > 17 else 0
                        },
                        "heaters": {
                            "jacket_heater_a": plc_data[18] if len(plc_data) > 18 else 0,
                            "line_heater_a": plc_data[19] if len(plc_data) > 19 else 0,
                            "jacket_heater_b": plc_data[20] if len(plc_data) > 20 else 0,
                            "line_heater_b": plc_data[21] if len(plc_data) > 21 else 0
                        },
                        "port_a": {
                            "cga_torque": plc_data[24] if len(plc_data) > 24 else 0,
                            "cap_torque": plc_data[25] if len(plc_data) > 25 else 0,
                            "cylinder_position": plc_data[26] if len(plc_data) > 26 else 0,
                            "barcode": ''.join([chr(x) if 32 <= x <= 126 else '?' for x in plc_data[30:60]]),
                            "gas_type": plc_data[90:95] if len(plc_data) > 94 else [0]*5
                        },
                        "port_b": {
                            "cga_torque": plc_data[27] if len(plc_data) > 27 else 0,
                            "cap_torque": plc_data[28] if len(plc_data) > 28 else 0,
                            "cylinder_position": plc_data[29] if len(plc_data) > 29 else 0,
                            "barcode": ''.join([chr(x) if 32 <= x <= 126 else '?' for x in plc_data[60:90]]),
                            "gas_type": plc_data[95:100] if len(plc_data) > 99 else [0]*5
                        }

                    },
                    "bit_data": {
                        "word_100": {
                            "raw": bit_data[0],
                            "states": {
                                "EMG Signal": bool(bit_data[0] & (1 << 0)),
                                "Heart Bit": bool(bit_data[0] & (1 << 1)),
                                "Run/Stop Signal": bool(bit_data[0] & (1 << 2)),
                                "Server Connected Bit": bool(bit_data[0] & (1 << 3)),
                                "T-LAMP RED": bool(bit_data[0] & (1 << 4)),
                                "T-LAMP YELLOW": bool(bit_data[0] & (1 << 5)),
                                "T-LAMP GREEN": bool(bit_data[0] & (1 << 6)),
                                "Touch 수동동작中 Signal": bool(bit_data[0] & (1 << 7))
                            }
                        },
                        "word_101": {
                            "raw": bit_data[1],
                            "states": {
                                "AV1A": bool(bit_data[1] & (1 << 0)),
                                "AV2A": bool(bit_data[1] & (1 << 1)),
                                "AV3A": bool(bit_data[1] & (1 << 2)),
                                "AV4A": bool(bit_data[1] & (1 << 3)),
                                "AV5A": bool(bit_data[1] & (1 << 4)),
                                "AV1B": bool(bit_data[1] & (1 << 5)),
                                "AV2B": bool(bit_data[1] & (1 << 6)),
                                "AV3B": bool(bit_data[1] & (1 << 7)),
                                "AV4B": bool(bit_data[1] & (1 << 8)),
                                "AV5B": bool(bit_data[1] & (1 << 9)),
                                "AV7": bool(bit_data[1] & (1 << 10)),
                                "AV8": bool(bit_data[1] & (1 << 11)),
                                "AV9": bool(bit_data[1] & (1 << 12))
                            }
                        },
                        "word_102": {
                            "raw": bit_data[2],
                            "states": {
                                "JACKET HEATER A RELAY": bool(bit_data[2] & (1 << 0)),
                                "LINE HEATER A RELAY": bool(bit_data[2] & (1 << 1)),
                                "JACKET HEATER B RELAY": bool(bit_data[2] & (1 << 2)),
                                "LINE HEATER B RELAY": bool(bit_data[2] & (1 << 3)),
                                "GAS LEAK SHUT DOWN": bool(bit_data[2] & (1 << 4)),
                                "VMB STOP SIGNAL": bool(bit_data[2] & (1 << 5)),
                                "UV/IR SENSOR": bool(bit_data[2] & (1 << 6)),
                                "HIGH TEMP SENSOR": bool(bit_data[2] & (1 << 7)),
                                "SMOKE SENSOR": bool(bit_data[2] & (1 << 8))
                            }
                        },
                        "word_103": {
                            "raw": bit_data[3],
                            "states": {
                                "[A] Port Insert Request": bool(bit_data[3] & (1 << 0)),
                                "[A] Port Insert Complete": bool(bit_data[3] & (1 << 1)),
                                "[A] Port Remove Request": bool(bit_data[3] & (1 << 2)),
                                "[A] Port Remove Complete": bool(bit_data[3] & (1 << 3)),
                                "[B] Port Insert Request": bool(bit_data[3] & (1 << 8)),
                                "[B] Port Insert Complete": bool(bit_data[3] & (1 << 9)),
                                "[B] Port Remove Request": bool(bit_data[3] & (1 << 10)),
                                "[B] Port Remove Complete": bool(bit_data[3] & (1 << 11))
                            }
                        },
                        "word_105": {
                            "raw": bit_data[5],
                            "states": {
                                "[A] Port 실린더 유무": bool(bit_data[5] & (1 << 0)),
                                "[B] Port 실린더 유무": bool(bit_data[5] & (1 << 1)),
                                "Door Open 완료": bool(bit_data[5] & (1 << 2)),
                                "Door Close 완료": bool(bit_data[5] & (1 << 3))
                            }
                        },
                        "word_110": {
                            "raw": bit_data[10],
                            "states": {
                                "[A] Close the Cylinder": bool(bit_data[10] & (1 << 0)),
                                "[A] 1st Purge before Exchange": bool(bit_data[10] & (1 << 1)),
                                "[A] Decompression Test": bool(bit_data[10] & (1 << 2)),
                                "[A] 2nd Purge before Exchange": bool(bit_data[10] & (1 << 3)),
                                "[A] Exchange Cylinder": bool(bit_data[10] & (1 << 4)),
                                "[A] 1st Purge after Exchange": bool(bit_data[10] & (1 << 5)),
                                "[A] Pressure Test": bool(bit_data[10] & (1 << 6)),
                                "[A] 2nd Purge after Exchange": bool(bit_data[10] & (1 << 7)),
                                "[A] Purge Completed": bool(bit_data[10] & (1 << 8)),
                                "[A] Prepare to Supply": bool(bit_data[10] & (1 << 9)),
                                "[A] Gas Supply AV3 Open/Close Choose": bool(bit_data[10] & (1 << 10)),
                                "[A] Gas Supply": bool(bit_data[10] & (1 << 11)),
                                "[A] Ready to Supply": bool(bit_data[10] & (1 << 12))
                            }
                        },
                        "word_115": {
                            "raw": bit_data[15],
                            "states": {
                                "[B] Close the Cylinder": bool(bit_data[15] & (1 << 0)),
                                "[B] 1st Purge before Exchange": bool(bit_data[15] & (1 << 1)),
                                "[B] Decompression Test": bool(bit_data[15] & (1 << 2)),
                                "[B] 2nd Purge before Exchange": bool(bit_data[15] & (1 << 3)),
                                "[B] Exchange Cylinder": bool(bit_data[15] & (1 << 4)),
                                "[B] 1st Purge after Exchange": bool(bit_data[15] & (1 << 5)),
                                "[B] Pressure Test": bool(bit_data[15] & (1 << 6)),
                                "[B] 2nd Purge after Exchange": bool(bit_data[15] & (1 << 7)),
                                "[B] Purge Completed": bool(bit_data[15] & (1 << 8)),
                                "[B] Prepare to Supply": bool(bit_data[15] & (1 << 9)),
                                "[B] Gas Supply AV3 Open/Close Choose": bool(bit_data[15] & (1 << 10)),
                                "[B] Gas Supply": bool(bit_data[15] & (1 << 11)),
                                "[B] Ready to Supply": bool(bit_data[15] & (1 << 12))
                            }
                        },
                        "word_116": {
                            "raw": bit_data[16],
                            "states": {
                                "[B] Cylinder Ready": bool(bit_data[16] & (1 << 0)),
                                "[B] CGA Disconnect Complete": bool(bit_data[16] & (1 << 1)),
                                "[B] CGA Connect Complete": bool(bit_data[16] & (1 << 2)),
                                "[B] Cylinder Valve Open Complete": bool(bit_data[16] & (1 << 3)),
                                "[B] Cylinder Valve Close Complete": bool(bit_data[16] & (1 << 4)),
                                "[B] Cylinder Valve Open Status": bool(bit_data[16] & (1 << 5)),
                                "[B] Cylinder Lift Unit Ready": bool(bit_data[16] & (1 << 6)),
                                "[B] Cylinder Lift Unit Moving Up": bool(bit_data[16] & (1 << 7)),
                                "[B] Cylinder Lift Unit Moving Down": bool(bit_data[16] & (1 << 8)),
                                "[B] CGA Separation In Progress": bool(bit_data[16] & (1 << 9)),
                                "[B] CGA Connection In Progress": bool(bit_data[16] & (1 << 10)),
                                "[B] Cylinder Cap Separation In Progress": bool(bit_data[16] & (1 << 11)),
                                "[B] Cylinder Valve Open In Progress": bool(bit_data[16] & (1 << 12)),
                                "[B] Cylinder Valve Close In Progress": bool(bit_data[16] & (1 << 13)),
                                "[B] Cylinder Alignment In Progress": bool(bit_data[16] & (1 << 14)),
                                "[B] Cylinder Turn In Progress": bool(bit_data[16] & (1 << 15))
                            }
                        },
                        "word_117": {
                            "raw": bit_data[17],
                            "states": {
                                "[B] Cylinder Turn Complete": bool(bit_data[17] & (1 << 0)),
                                "[B] Cylinder Clamp Complete": bool(bit_data[17] & (1 << 1)),
                                "[B] CGA Connect Complete Status": bool(bit_data[17] & (1 << 2))
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

    def _get_word_200_states(self, word: int) -> Dict[str, bool]:
        """word_200 상태 비트 해석"""
        return {
            "emg_signal": bool(word & (1 << 0)),
            "heart_bit": bool(word & (1 << 1)),
            "run_stop_signal": bool(word & (1 << 2)),
            "server_connected": bool(word & (1 << 3)),
            "port_a_cylinder": bool(word & (1 << 4)),
            "port_b_cylinder": bool(word & (1 << 5)),
            "port_a_manual": bool(word & (1 << 6)),
            "port_b_manual": bool(word & (1 << 7)),
            "door_open": bool(word & (1 << 8)),
            "door_close": bool(word & (1 << 9))
        }

    def _get_word_201_states(self, word: int) -> Dict[str, bool]:
        """word_201 상태 비트 해석"""
        return {
            "lamp_red": bool(word & (1 << 0)),
            "lamp_yellow": bool(word & (1 << 1)),
            "lamp_green": bool(word & (1 << 2)),
            "jacket_heater_a": bool(word & (1 << 3)),
            "line_heater_a": bool(word & (1 << 4)),
            "jacket_heater_b": bool(word & (1 << 5)),
            "line_heater_b": bool(word & (1 << 6)),
            "gas_leak_shutdown": bool(word & (1 << 7)),
            "vmb_stop": bool(word & (1 << 8)),
            "uv_ir_sensor": bool(word & (1 << 9)),
            "high_temp_sensor": bool(word & (1 << 10)),
            "smoke_sensor": bool(word & (1 << 11))
        }

    def _get_word_210_states(self, word: int) -> Dict[str, bool]:
        """[A] Port 진행 상태 해석"""
        states = [
            "close_cylinder", "purge_1st_before", "decompression_test",
            "purge_2nd_before", "exchange_cylinder", "purge_1st_after",
            "pressure_test", "purge_2nd_after", "purge_completed",
            "prepare_supply", "av3_control", "gas_supply", "ready_supply"
        ]
        return {state: bool(word & (1 << i)) for i, state in enumerate(states)}

    def _get_word_211_states(self, word: int) -> Dict[str, bool]:
        """A Port 밸브 상태 해석"""
        return {f"av{i+1}a": bool(word & (1 << i)) for i in range(5)}

    def _get_word_215_states(self, word: int) -> Dict[str, bool]:
        """[A] Port 상세 상태 해석"""
        states = [
            "cylinder_ready", "cga_disconnected", "cga_connected",
            "valve_open_complete", "valve_close_complete", "valve_open_status",
            "lift_ready", "lift_up_progress", "lift_down_progress",
            "cga_disconnecting", "cga_connecting", "cap_removing",
            "valve_opening", "valve_closing", "cylinder_aligning",
            "lift_rotating"
        ]
        return {state: bool(word & (1 << i)) for i, state in enumerate(states)}

    def _get_word_216_states(self, word: int) -> Dict[str, bool]:
        """[A] Port 추가 상태 해석"""
        states = [
            "lift_rotation_complete", "clamp_close_complete", "cga_connection_complete",
            "port_input_request", "port_input_complete", "port_output_request",
            "port_output_complete"
        ]
        return {state: bool(word & (1 << i)) for i, state in enumerate(states)}

    def _get_word_220_states(self, word: int) -> Dict[str, bool]:
        """[B] Port 진행 상태 해석"""
        states = [
            "close_cylinder", "purge_1st_before", "decompression_test",
            "purge_2nd_before", "exchange_cylinder", "purge_1st_after",
            "pressure_test", "purge_2nd_after", "purge_completed",
            "prepare_supply", "av3_control", "gas_supply", "ready_supply"
        ]
        return {state: bool(word & (1 << i)) for i, state in enumerate(states)}

    def _get_word_221_states(self, word: int) -> Dict[str, bool]:
        """B Port 밸브 상태 해석"""
        states = {f"av{i+1}b": bool(word & (1 << i)) for i in range(5)}
        # AV7-AV9 (13-15)
        for i, num in enumerate(range(13, 16)):
            states[f"av{7+i}"] = bool(word & (1 << num))
        return states

    def _get_word_225_states(self, word: int) -> Dict[str, bool]:
        """[B] Port 상세 상태 해석"""
        states = [
            "cylinder_ready", "cga_disconnected", "cga_connected",
            "valve_open_complete", "valve_close_complete", "valve_open_status",
            "lift_ready", "lift_up_progress", "lift_down_progress",
            "cga_disconnecting", "cga_connecting", "cap_removing",
            "valve_opening", "valve_closing", "cylinder_aligning",
            "lift_rotating"
        ]
        return {state: bool(word & (1 << i)) for i, state in enumerate(states)}

    def _get_word_226_states(self, word: int) -> Dict[str, bool]:
        """[B] Port 추가 상태 해석"""
        states = [
            "lift_rotation_complete", "clamp_close_complete", "cga_connection_complete",
            "port_input_request", "port_input_complete", "port_output_request",
            "port_output_complete"
        ]
        return {state: bool(word & (1 << i)) for i, state in enumerate(states)}
    
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

    async def update_client_data(modbus_client):
        while modbus_client.running:  # running 플래그 확인
            try:
                data = await modbus_client.get_data()
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