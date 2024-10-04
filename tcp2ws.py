import asyncio
import websockets
import base64

async def tcp_to_ws(reader, writer):
    try:
        # WebSocket接続先のURLとBasic認証情報を指定
        ws_url = "wss://"  # WebSocketのURL
        username = "name"
        password = "password"
        credentials = base64.b64encode(f"{username}:{password}".encode()).decode("utf-8")
        headers = [("Authorization", f"Basic {credentials}")]
        
        # WebSocketへの接続
        websocket = await websockets.connect(ws_url, extra_headers=headers)

        async def forward_data(src_reader, dest_writer):
            while True:
                data = await src_reader.read(4096)
                if not data:
                    break
                await dest_writer.send(data)

        # TCPからWebSocketへのデータ転送
        asyncio.ensure_future(forward_data(reader, websocket))

        # WebSocketからTCPへのデータ転送
        async for message in websocket:
            writer.write(message)  # バイト列をそのまま書き込む
            await writer.drain()
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        await websocket.close()

async def main():
    server = await asyncio.start_server(tcp_to_ws, '0.0.0.0', 8888)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
