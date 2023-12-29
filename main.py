import asyncio
import logging
import sys
from datetime import datetime, timedelta

import aiohttp

logging.basicConfig(level=logging.INFO)

async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    r = await response.json()
                    return r
                logging.error(f'Error status {response.status} for {url}')
                return None
        except aiohttp.ClientConnectionError as e:
            logging.error(f'Connection error {url} : {e}')
        return None

async def get_exchange(incoming_data):
    date = incoming_data.strftime("%d.%m.%Y")
    res = await request(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={date}')
    if res:
        rates = res.get('exchangeRate')
        exchangeEUR, *_ = list(filter(lambda el: el['currency'] == 'EUR', rates))
        exchangeUSD, *_ = list(filter(lambda el: el['currency'] == 'USD', rates))
        f_str = f"{date}: EUR: sale {exchangeEUR['saleRate']} purchase {exchangeEUR['purchaseRate']}, USD: sale {exchangeUSD['saleRate']} purchase {exchangeUSD['purchaseRate']}"
        return f_str

async def main():

    if len(sys.argv) == 2:
        count_days = int(sys.argv[1])
        print(count_days)

        if count_days > 10:
            count_days = 10
        date = datetime.now().date()
        r = list()
        for day in range(0, count_days):
            data = date + timedelta(days=-day)
            r.append(get_exchange(data))
        result = await asyncio.gather(*r)
        return result
    else:
        print(len(sys.argv))
        print('Вкажіть кількість днів для отримання курсу валют, але не більше 10')

if __name__ == '__main__':
    result = asyncio.run(main())
    for r in result:
        print(r)











