from fastapi import FastAPI, Depends, Security, Request, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session
import dotenv
import os
import database as db

dotenv.load_dotenv(dotenv.find_dotenv())

apiKey = os.environ.get('API_KEY')

apiKeyHeader = APIKeyHeader(name="x-api-key")
async def authorize(key: str = Security(apiKeyHeader)):
    if key != apiKey :
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Missing or invalid API key"
        )

app = FastAPI(
    dependencies=[
        Depends(authorize),
    ]
)

@app.middleware('http')
async def encodeJSONData(request: Request, next):
    #print(await request.body())
    # update request headers
    #headers = dict(request.scope['headers'])
    #headers[b'custom-header'] = b'my custom header'
    #request.scope['headers'] = [(k, v) for k, v in headers.items()]
    
    # update request query parameters
    #q_params = dict(request.query_params)
    #q_params['custom-q-param'] = 'my custom query param'
    #request.scope['query_string'] = urlencode(q_params).encode('utf-8')
        
    return await next(request)

import json
from pydantic import BaseModel
class Payload(BaseModel):
    data: str

@app.post("/test")
def test(payload: Payload):
    print(payload, type(payload))
    payload = payload.model_dump()
    print(payload, type(payload))
    assert db.UpdateDataModel(data = payload)
    #return x

@app.post("/pet_data")
def update_data(data: db.UpdateDataModel, database: Session = Depends(db.getDatabase)):
    for newPetData in data.data:
        petData = database.query(db.PetData).filter(db.PetData.id == newPetData.id).one_or_none()
        if petData is None:
            petData = db.PetData(id = newPetData.id)
            database.add(petData)

        petData.count += newPetData.count

        newTransactions = petData.transactions.copy()
        for i in range(len(newTransactions)-100):
            newTransactions.remove(i)
        for sellPrice in newPetData.transactions:
            newTransactions.append(sellPrice)
        petData.transactions = newTransactions

        if len(petData.transactions) > 0:
            newValue = 0
            for sellPrice in petData.transactions:
                newValue += sellPrice
            newValue /= len(petData.transactions)
            petData.value = round(newValue)

    database.commit()
   
@app.get("/pet_data")
def update_data(database: Session = Depends(db.getDatabase)):
    return database.query(db.PetData).all()