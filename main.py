from fastapi import FastAPI, HTTPException
from decimal import Decimal, ROUND_DOWN
import subprocess
import os
import logging

# Настройка логирования 
log_file = "app.log"
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler(log_file), 
                              logging.StreamHandler()])
logger = logging.getLogger(__name__)


app = FastAPI()

# Webhook-запрос от GitHub Actions
@app.post("/deploy")
async def deploy():
    try:
        logger.info("Запуск команды git pull для обновления репозитория.")
        result = subprocess.run(["git", "pull"], check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        logger.info("Код успешно обновлен.")
        return {"status": "success", "output": result.stdout.decode()}
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при обновлении кода: {e.stderr.decode()}")
        return {"status": "failed", "error": e.stderr.decode()}

#Курс фиксируется в приложении и имитируется получение его от CoinMarketCap

fixed_exchange_data = {
    "USDT":{"price":1.00},
    "BTC":{"price":97000.00},         
    "ETH":{"price":2600.00},
    "TON":{"price":3.80},      
}

def get_exchange_rate(base_currency: str, quote_currency: str) -> Decimal:

    if base_currency not in fixed_exchange_data or quote_currency not in fixed_exchange_data:
        logger.error(f"Данные для одной из валют не найдены: {base_currency}, {quote_currency}")
        raise HTTPException(status_code=404, detail="Данные для одной из валют не найдены")
    
    base_price = Decimal(fixed_exchange_data[base_currency]["price"])
    quote_price = Decimal(fixed_exchange_data[quote_currency]["price"])

    exchange_rate = base_price / quote_price
    return exchange_rate

@app.get("/")
async def root():
    logger.info("Поступил запрос на корневой путь")
    return {"Hi"}

@app.get("/exchange")
async def exchange(amount: float, pair: str):
    if amount <= 0:
        logger.warning(f"Неверная сумма обмена: {amount}. Сумма должна быть больше 0.")
        raise HTTPException(status_code=400,detail="Сумма должна быть больше 0")

    pairs = {
            "USDT-BTC": ("USDT", "BTC"),
            "BTC-USDT": ("BTC", "USDT"),
            "USDT-ETH": ("USDT", "ETH"),
            "ETH-USDT": ("ETH", "USDT"),
            "USDT-TON": ("USDT", "TON"),
            "TON-USDT": ("TON", "USDT"),
        }

    if pair not in pairs:
        logger.warning(f"Неверная валютная пара: {pair}.")
        raise HTTPException(status_code=400, detail="Неверная валютная пара")
    
    base_currency, quote_currency = pairs[pair]
    logger.info(f"Обмен валюты: {base_currency} -> {quote_currency}, сумма: {amount}")

    exchange_rate = get_exchange_rate(base_currency, quote_currency)

    commission = Decimal("0.005")

    effective_amount = Decimal(str(amount)) * (Decimal("1")) - commission
    transaction_amount = effective_amount * exchange_rate

    transaction_amount = transaction_amount.quantize(Decimal("0.0000000001"), rounding=ROUND_DOWN)
    
    logger.info(f"Транзакция успешно расситана. Сумма обмена: {transaction_amount} {quote_currency}")

    return {
        "base_currency": base_currency,
        "quote_currency": quote_currency,
        "input_amount": amount,
        "exchange_rate": float(exchange_rate),
        "commission_percent": float(commission*100),
        "transaction_amount": float(transaction_amount),
    }