from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ConnectionManager:
    """Manage WebSocket connections"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = set()

        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                disconnected.add(connection)

        # Remove disconnected clients
        self.active_connections -= disconnected

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")

manager = ConnectionManager()

@router.websocket("/flood-updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time flood updates"""

    await manager.connect(websocket)

    try:
        # Send initial connection success message
        await manager.send_personal_message(
            {
                "type": "connection",
                "status": "connected",
                "message": "Connected to flood prediction system"
            },
            websocket
        )

        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Receive messages from client (e.g., subscription requests)
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle different message types
                if message.get("type") == "subscribe":
                    # Handle subscription to specific gauges or areas
                    await manager.send_personal_message(
                        {
                            "type": "subscription",
                            "status": "success",
                            "subscribed_to": message.get("resource")
                        },
                        websocket
                    )

                elif message.get("type") == "ping":
                    # Respond to ping to keep connection alive
                    await manager.send_personal_message(
                        {"type": "pong"},
                        websocket
                    )

            except json.JSONDecodeError:
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "message": "Invalid JSON format"
                    },
                    websocket
                )

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected normally")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

async def broadcast_gauge_update(gauge_data: dict):
    """Broadcast gauge update to all connected clients"""
    await manager.broadcast({
        "type": "gauge_update",
        "data": gauge_data,
        "timestamp": gauge_data.get("last_updated")
    })

async def broadcast_risk_alert(alert_data: dict):
    """Broadcast risk alert to all connected clients"""
    await manager.broadcast({
        "type": "risk_alert",
        "data": alert_data,
        "severity": alert_data.get("risk_level"),
        "timestamp": alert_data.get("timestamp")
    })

async def broadcast_prediction_update(prediction_data: dict):
    """Broadcast new prediction to all connected clients"""
    await manager.broadcast({
        "type": "prediction_update",
        "data": prediction_data,
        "timestamp": prediction_data.get("prediction_time")
    })