from fastapi import FastAPI, WebSocket
import requests
import asyncio

app = FastAPI()

def get_token_info(chain_id: str, token_address: str):

    API_URL = f"https://api.dexscreener.com/tokens/v1/{chain_id}/{token_address}"

    try:
        response = requests.get(API_URL)
        data = response.json()

        if data and isinstance(data, list) and len(data) > 0:
            return data[0]  # Trả về thông tin của token đầu tiên
        else:
            return {"error": "Không tìm thấy dữ liệu cho token này."}
    except Exception as e:
        return {"error": f"Lỗi lấy dữ liệu: {str(e)}"}

def get_token_price(chain_id: str, token_address: str):
    """Lấy giá token từ API Dexscreener"""
    token_info = get_token_info(chain_id, token_address)

    if "error" in token_info:
        return token_info  # Trả về lỗi nếu không tìm thấy token

    return {
        "chain_id": chain_id,
        "token": token_address,
        "price_usd": token_info.get("priceUsd", "Không có dữ liệu"),
        "price_native": token_info.get("priceNative", "Không có dữ liệu")
    }

@app.websocket("/ws/token/{chain_id}/{token_address}")
async def websocket_token_info(websocket: WebSocket, chain_id: str, token_address: str):
    await websocket.accept()
    while True:
        token_info = get_token_info(chain_id, token_address)
        await websocket.send_json(token_info)
        await asyncio.sleep(0.2)

@app.websocket("/ws/price/{chain_id}/{token_address}")
async def websocket_token_price(websocket: WebSocket, chain_id: str, token_address: str):
    await websocket.accept()
    while True:
        price_info = get_token_price(chain_id, token_address)
        await websocket.send_json(price_info)
        await asyncio.sleep(0.2)

@app.get("/")
async def read_root():
    return {"message": "Hello World!"}
