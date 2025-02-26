import cv2
import numpy as np
import base64
import json
import random
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import asyncio  # To slow down frame rate
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, world!"}
@app.get("/favicon.ico")
def favicon():
    return {}

# Allow frontend connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_random_shape(num_points, width=640, height=480):
    """Generate a random shape with a given number of points."""
    return [[random.randint(50, width-50), random.randint(50, height-50)] for _ in range(num_points)]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    frame_num = 0

    try:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (640, 480))

            # Generate shapes
            red_shape = generate_random_shape(4)  # Backend-drawn shape
            blue_shape = generate_random_shape(5)  # Sent to frontend for drawing

            # Draw red shape on frame
            pts = np.array(red_shape, np.int32).reshape((-1, 1, 2))
            overlay = frame.copy()
            cv2.fillPoly(overlay, [pts], (0, 0, 255))  # Red shape with opacity
            frame = cv2.addWeighted(overlay, 0.5, frame, 0.5, 0)

            # Encode frame as JPEG
            _, buffer = cv2.imencode(".jpg", frame)
            encoded_frame = base64.b64encode(buffer).decode("utf-8")

            # Send frame + blue shape points
            await websocket.send_text(json.dumps({
                "frame": encoded_frame,
                "frame_num": frame_num,
                "blue_shape": blue_shape
            }))

            frame_num += 1
            await asyncio.sleep(0.1)  # Slow down frame rate (10 FPS)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        cap.release()
        await websocket.close()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
