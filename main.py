from fastapi import FastAPI
import json
from fastapi import Path
app = FastAPI()
def load_data():
    try:
        with open('patients.json', 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


app.get("/")
def read_root():
    return {"Message": "Patient Management System API"}

app.get("/about")
def read_about():
    return {
        "name": "Patient Management System API",
        "version": "1.0.0",
        "description": "API for managing patient records and appointments."
    }
    
@app.get('/view')
def view():
    data = load_data()

    return data

@app.get('/search/{patient_id}')
def search(patient_id: str = Path(..., title='Patient ID', description='ID of the patient', example='P001')):
    data = load_data()

    if patient_id in data:
        return data[patient_id]
    return {'Error':'Patient not found'}