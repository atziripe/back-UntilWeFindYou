from typing import Union, Optional
from datetime import date
from fastapi import FastAPI, HTTPException, Depends, Query
from model.user_connection import UserConnection
import scheme.user_schema as User
import scheme.case_schema as Case
import scheme.riskassesment_schema as Risk
import scheme.textanalysis_schema as TextA
import joblib
import pandas as pd
import helpers
import pickle
import tensorflow as tf
from tensorflow.keras.models import load_model
import numpy as np


app = FastAPI()
conn = UserConnection()

risk_model = joblib.load("./ml_models/risk_model.pkl")
model = load_model('./ml_models/multilabel_model.h5')

with open('./ml_models/vocab.pkl', 'rb') as f:
    vocabulary = pickle.load(f)

with open('./ml_models/config.pkl', 'rb') as f:
    config = pickle.load(f)

max_length = config['max_length']
label_columns = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']

@app.get("/")
def read_root():
    conn
    return {"Hello": "World"}
@app.post("/auth/register")
def insert_user(user_data: User.UserCreate):
    data = user_data.dict()
    user = conn.create_user(data)
    if user:
        return {"message": "User Created!", "user": user}
    else:
        raise HTTPException(status_code=500, detail="Internal Server Error")
   

@app.post("/auth/login")
def login_ong(login_data: User.LoginData):
    data = login_data
    user = conn.login_ong(data.email, data.password)

    if user:
        # JWT token
        return {"message": "Login successful", "user": user}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
@app.post("/cases")
def insert_case(case_data: Case.CaseCreate):
    data = case_data.dict()
    case = conn.create_case(data)
    if case:
        return {"message": "Case Created Succesfully!", "user": case}
    else:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/cases")
def read_cases(
    gender: Optional[str] = Query(None, description="Filter by gender"),
    status: Optional[str] = Query(None, description="Filter by case status"), 
    reported_by: Optional[int] = Query(None, description="Filter by reporting user ID"),
    created_at: Optional[date] = Query(None, description="Date or reported"),
    date_missing: Optional[date] = Query(None, description="Date of mising")
    ):
    cases = conn.get_all_cases_with_filter(gender=gender, status=status, reported_by=reported_by, created_at=created_at, date_missing=date_missing)
    if not cases:
        raise HTTPException(status_code=404, detail="No cases to show")
    else:
       return cases
    
@app.get("/cases/{case_id}")
def read_case(case_id: str):
    case = conn.get_case_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    else:
       return case
    
@app.put("/cases/{case_id}")
def update_case(case_id: str, case_data: Case.CaseCreate):
    data = case_data.dict()

    case_changed = conn.update_case_by_id(case_id, data)
    if case_changed:
        return {"message": "Case Updated Succesfully!", "changes": case_changed}
    else:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.post("/ml/risk-predict/{case_id}")
def risk_predict(case_id: str):
    data = conn.get_case_by_id(case_id)
    input_data = helpers.get_prediction_input(data)
    input_prediction_df = pd.DataFrame([input_data])
    prediction = risk_model.predict(input_prediction_df)[0]
    pred_str =  "HIGH" if prediction == 1 else "LOW"
    update_id = conn.insert_risk_level(case_id, pred_str)
    return Risk.RiskAssessmentCreate(
        case_id = case_id,
        risk_level =  pred_str,
        model_version = "riskAssesment 1.0"
    )

@app.post("/ml/alert/{case_id}")
def text_analysis_prediction(case_id:str,comment: TextA.CommentInput):
    result = {}
    pred = []
    pred_dict = {}
    sequence = helpers.text_to_sequence(comment.text, vocabulary,max_length)
    sequence = np.array([sequence])
    prediction = model.predict(sequence)[0]
    for label, value in zip(label_columns, prediction):
        if value > 0.5:
            pred.append(label)
        print(f"{label}: {value}")
        result["prediction"]=pred
        pred_dict[label]=True if float(value) >= 0.5 else False
    update_id = conn.insert_text_prediction(pred_dict, case_id)
    return result


@app.get("/dashboard/kpis")
def read_metrics ():
    data = conn.get_metrics()
    if not data:
        raise HTTPException(status_code=404, detail="No cases to show")
    else:
       return data