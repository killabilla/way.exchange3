from fastapi import FastAPI, HTTPException
from decimal import Decimal, ROUND_DOWN
import requests

app = FastAPI()

cmc_api = "00bbfede-4e31-4ff0-bbac-5adcc5a0ebc1"
base_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

def get_exchange_rate(base_currency:str, quote_currency: str) -> Decimal:
    #Получаем курс через api coinmarketcap
    headers = {
        "Coinmarketcap_api": cmc_api,
        "Accept": "application/json",
    }

    params = {
    'start' : '1',
    'limit': '20',
    'convert': 'USD',
    }

    response = requests.get(base_url, headers=headers, params=params)
    data = response.json()

    # Находим нужные данные для пары обмена
    exchange_rate = None
    for crypto in data['data']:
        if crypto['symbol'] == base_currency:
                base_price = crypto['quote']['USD']['price']
        if crypto['symbol'] == base_currency:
            quote_price = crypto['quote']['USD']['price']

        if base_price and quote_price:
            exchange_rate = Decimal(quote_price) / Decimal(base_price)
            break

    if exchange_rate is None:
        raise HTTPException(status_code=404, detail= "Не удалось получить курс для выбранных валют")

    return exchange_rate


@app.get("/")
async def root():
    return {"Hi"}

@app.get("/exchange")
async def exchange(usdt_amount: float, pair: str):
    if usdt_amount <= 0:
        raise HTTPException(status_code=400,detail="Сумма должна быть больше 0")

    # Выбираем пару
    pairs = {
            "USDT-BTC": ("USDT", "BTC"),
            "USDT-BTC": ("USDT", "BTC"),
            "USDT-ETH": ("USDT", "ETH"),
            "ETH-USDT": ("ETH", "BTC"),
            "USDT-TON": ("USDT", "ETH"),
            "TON-USDT": ("TON", "BTC"),
        }

    # Проверяем корректность пары
    if pair not in pairs:
        raise HTTPException(status_code=400, detail="Неверная валютная пара")
    
    base_currency, quote_currency = pairs[pair]

    # Получаем курс обмена для пары
    exchange_rate = get_exchange_rate(base_currency, quote_currency)

    # Считаем сколько пользователь получит после обмена с учетом комиссии
    commission = Decimal("0.005")
    transaction_amount = Decimal(usdt_amount) * exchange_rate
    transaction_amount -= transaction_amount * commission

    # Округление до 10 знаков после запятой
    transaction_amount = transaction_amount.quantize(Decimal("0.0000000001"), rounding=ROUND_DOWN)
    
    return {
        "base_currency": base_currency,
        "quote_currency": quote_currency,
        "input_amount": usdt_amount,
        "exchange_rate": float(exchange_rate),
        "transaction_amount": float(transaction_amount),
        "commission": float(commission * 100),
    }