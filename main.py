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

@app.post("/pet_data")
def update_data(data: db.UpdateDataModel, database: Session = Depends(db.getDatabase)):
    for newPetData in data.data:
        petData = database.query(db.PetData).filter(db.PetData.id == newPetData.id).one_or_none()
        if petData is None:
            petData = db.PetData(id = newPetData.id)
            if newPetData.baseValue > 0:
                petData.transactions = [newPetData.baseValue]
            database.add(petData)

        petData.baseValue = newPetData.baseValue
        petData.count += newPetData.count

        newTransactions = petData.transactions.copy()

        for i in range(len(newTransactions)+1-100):
            newTransactions.pop(0)
        maxTransactionValue = (petData.value > 0) and (petData.value * 1.2) or float('inf')
        for sellPrice in newPetData.transactions:
            newTransactions.append(min(sellPrice, maxTransactionValue))
        petData.transactions = newTransactions

        if len(petData.transactions) > 0:
            newValue = 0
            for sellPrice in petData.transactions:
                newValue += sellPrice
            newValue /= len(petData.transactions)
            petData.value = newValue

    database.commit()
   
@app.get("/pet_data")
def update_data(database: Session = Depends(db.getDatabase)):
    return database.query(db.PetData).all()

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

@app.get("/migrate_data")
def update_data(database: Session = Depends(db.getDatabase)):
    d = database.query(db.PetData).all()
    for data in d:
        itemData = database.query(db.ItemData).filter(db.ItemData.id == data.id).one_or_none()
        if itemData is None:
            itemData = db.ItemData(id = data.id)
            if data.baseValue > 0:
                itemData.transactions = [[0, data.baseValue]]
                itemData.value = data.baseValue
            database.add(itemData)
        itemData.count = data.count
    database.commit()