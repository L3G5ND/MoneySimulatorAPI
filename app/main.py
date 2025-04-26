from fastapi import FastAPI, Depends
from sqlalchemy.orm.attributes import flag_modified 
from sqlalchemy.orm import Session
import database as db

app = FastAPI()

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