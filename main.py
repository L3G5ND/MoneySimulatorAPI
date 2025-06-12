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

@app.post("/item_data")
def update_data(data: db.NewDataModel, database: Session = Depends(db.getDatabase)):
    for newData in data.data:
        itemData = database.query(db.ItemData).filter(db.ItemData.id == newData.id).one_or_none()
        if itemData is None:
            itemData = db.ItemData(id = newData.id)
            if newData.baseValue > 0:
                itemData.transactions = [[0, newData.baseValue]]
                itemData.value = newData.baseValue
            database.add(itemData)

        itemData.baseValue = newData.baseValue
        itemData.count += newData.count


        newTransactions = itemData.transactions.copy()

        for transactionInfo in newData.transactions:
            userId = transactionInfo[0]
            price = transactionInfo[1]

            for i in range(len(newTransactions)):
                print(len(newTransactions), i)
                if userId == newTransactions[i][0]:
                    newTransactions.pop(i)

            value = 0
            for transactionInfo in newTransactions:
                value += transactionInfo[1]
            value /= len(newTransactions)

            for i in range(len(newTransactions)+1-100):
                newTransactions.pop(0)

            newTransactions.append([userId, min(price, (value > 0) and (value * 1.25) or float('inf'))])

        itemData.transactions = newTransactions


        if len(itemData.transactions) > 0:
            value = 0
            for transactionInfo in itemData.transactions:
                value += transactionInfo[1]
            value /= len(newTransactions)
            itemData.value = value

    database.commit()
   
@app.get("/item_data")
def update_data(database: Session = Depends(db.getDatabase)):
    return database.query(db.ItemData).all()