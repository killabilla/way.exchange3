from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class ExchangeRequest(BaseModel):
    usdt_amount: float

@app.get("/")
async def root():
    return {"Hi"}

@app.get("/exchange")
async def exchange(usdt_amount: float):
    if usdt_amount <= 0:
        raise HTTPException(status_code=400,detail="Сумма должна быть больше 0")
    
    btc_amount = usdt_amount * 0.00003
    return {"btc_amount": "{:.8f}".format(btc_amount)}