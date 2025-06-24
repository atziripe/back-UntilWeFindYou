from datetime import datetime, timedelta
import pandas as pd
import re
import numpy as np

def classify_hour(hour):
    if pd.isnull(hour):
        return "UNKNOWN"
    h = hour
    if 6 <= h < 12:
        return "MORNING"
    elif 12 <= h < 18:
        return "AFTERNOON"
    elif 18 <= h < 24:
        return "NIGHT"
    else:
        return "EARLY MORNING"
    
def get_prediction_input(data:dict):
    date_missing = data["date_missing"]
    date_report = data["created_at"]
    under_age = 1 if data["age integer"] < 1 else 0
    is_woman = 1 if data["gender"] == "female" else 0
    time_no_report = (date_report - date_missing).total_seconds() / 3600
    hour_day = classify_hour(date_missing.hour)
    weekday_disappearance = date_missing.strftime("%A")

    return {
        "EDAD": data["age integer"],
        "UNDER_AGE": under_age,
        "IS_WOMAN": is_woman,
        "TIME_NO_REPORT": time_no_report,
        "HOUR_DAY": hour_day,
        "WEEKDAY_DESAPARICION": weekday_disappearance,
        "ENTIDAD": data["last_seen_location"].split("-")[1],
        "MUNICIPIO": data["last_seen_location"].split("-")[0]
    }

# Funciones de preprocesamiento
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^a-zA-Z0-9']", " ", text)
    return text.split()

def text_to_sequence(text, vocabulary, max_length):
    tokens = preprocess_text(text)
    sequence = [vocabulary.get(token, vocabulary["<OOV>"]) for token in tokens]
    sequence = sequence[:max_length] + [0] * (max_length - len(sequence))
    return np.array(sequence)