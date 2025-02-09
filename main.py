from fastapi import FastAPI, HTTPException
from decimal import Decimal, ROUND_DOWN

app = FastAPI()

#Курс фиксируется в приложении и имитируется получение его от CoinMarketCap
#Структура данных как из API

fixed_exchange_data = {
    "USDT":{"price":1.00},
    "BTC":{"price":97000.00},         
    "ETH":{"price":2600.00},
    "TON":{"price":3.80},      
}

def get_exchange_rate(base_currency: str, quote_currency: str) -> Decimal:

    if base_currency not in fixed_exchange_data or quote_currency not in fixed_exchange_data:
        raise HTTPException(status_code=404, detail="Не удалось найти данные для одной из валют")
    
    base_price = Decimal(fixed_exchange_data[base_currency]["price"])
    quote_price = Decimal(fixed_exchange_data[quote_currency]["price"])

    exchange_rate = base_price / quote_price
    return exchange_rate

@app.get("/")
async def root():
    return {"Hi"}

@app.get("/exchange")
async def exchange(amount: float, pair: str):
#amount - валюта отправления, pair - валюта получения в паре. Комиссия забирается с суммы отправления

    if amount <= 0:
        raise HTTPException(status_code=400,detail="Сумма должна быть больше 0")

    # Выбираем пару
    pairs = {
            "USDT-BTC": ("USDT", "BTC"),
            "BTC-USDT": ("BTC", "USDT"),
            "USDT-ETH": ("USDT", "ETH"),
            "ETH-USDT": ("ETH", "BTC"),
            "USDT-TON": ("USDT", "ETH"),
            "TON-USDT": ("TON", "BTC"),
        }

    if pair not in pairs:
        raise HTTPException(status_code=400, detail="Неверная валютная пара")
    
    base_currency, quote_currency = pairs[pair]

    # Получаем курс обмена для пары
    exchange_rate = get_exchange_rate(base_currency, quote_currency)

    commission = Decimal("0.005")

    # Вычитаем комиссию
    effective_amount = Decimal(str(amount)) * (Decimal("1")) - commission

    transaction_amount = effective_amount * exchange_rate

    # Округление до 10 знаков после запятой
    transaction_amount = transaction_amount.quantize(Decimal("0.0000000001"), rounding=ROUND_DOWN)
    
    return {
        "base_currency": base_currency,
        "quote_currency": quote_currency,
        "input_amount": amount,
        "exchange_rate": float(exchange_rate),
        "commission_percent": float(commission*100),
        "transaction_amount": float(transaction_amount),
    }