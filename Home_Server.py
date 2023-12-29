import asyncio
import logging

import aiohttp
import websockets
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK

logging.basicConfig(level=logging.INFO)

class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = 'll'
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws:WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_client(self, message: str, ws: WebSocketServerProtocol):
        ws.send(message)

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            if message == 'exchange':
                r = await get_exchange()
                await self.send_to_client(r, ws)
            else:
                await self.send_to_clients(f'{ws.name}: {message}')

async def request(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    r = await response.json()
                    return r
                logging.error(f'Error status {response.status} for {url}')
        except aiohttp.ClientConnectionError as e:
            logging.error(f'Connection error {url} : {e}')
        return None

async def get_exchange(days):
    res = await request('https://api.privatbank.ua/p24api/exchange_rates?json&date=01.12.2014')

    exchange, *_ = list(filter(lambda el: el['ccy'] == 'USD', res))
    return f"USD: sale {exchange['sale']} purchase {exchange['buy']}"

async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())












