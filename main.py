from fastapi import FastAPI, HTTPException
from decimal import Decimal, ROUND_DOWN

app = FastAPI()


@app.get("/")
async def root():
    return {"Hi"}

@app.get("/exchange")
async def exchange(usdt_amount: float):
    if usdt_amount <= 0:
        raise HTTPException(status_code=400,detail="Сумма должна быть больше 0")
    
    btc_amount = Decimal(usdt_amount) * Decimal("0.00003")
    btc_amount = btc_amount.quantize(Decimal("0.00000001"), rounding=ROUND_DOWN)
    return {"btc_amount": float(btc_amount)}