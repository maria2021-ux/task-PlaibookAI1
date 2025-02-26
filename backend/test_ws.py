
app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ WebSocket Connection Opened")
    try:
        while True:
            data = await websocket.receive_text()
            print("📩 Received:", data)  # Check if frames are coming in
            await websocket.send_text(json.dumps({"frame_number": 123, "blue_points": [{"x": 50, "y": 50}, {"x": 100, "y": 100}]}))
    except Exception as e:
        print("❌ WebSocket Error:", e)
    finally:
        print("🔴 WebSocket Connection Closed")