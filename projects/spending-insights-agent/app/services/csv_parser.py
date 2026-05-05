# csv -> returns a list of clean, normalised transaction dicts that match the DB schema.

import io
import pandas as pd
from datetime import datetime

REQUIRED_COLUMNS = {'txn_id', 'date', 'description', 'amount'}
OPTIONAL_COLUMNS = {'currency','merchant','account_id'}

class CSVParseError(Exception):
    """Raised when the CSV is missing required columns or has bad data."""
    pass

def parse_csv_file(filepath:str)->list[dict]:
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        raise CSVParseError(f"Error reading CSV file: {e}")
    return _normalise(df)

def parse_csv_bytes(content:bytes)->list[dict]:
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as e:
        raise CSVParseError(f"Error reading CSV file: {e}")
    return _normalise(df)

def _normalise(df:pd.DataFrame)->list[dict]:

    #normalise column names
    df.columns = [col.strip().lower() for col in df.columns]

    #check required columns
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise CSVParseError(f"CSV is missing required columns: {missing}")
    
    # drop row if required field is missing or empty
    before = len(df)
    df =df.dropna(subset=list(REQUIRED_COLUMNS))
    dropped = before - len(df)
    if dropped:
       print(f"Warning: dropped {dropped} rows with null required fields")


    #parse and normalise each row 

    transactions = []
    for _, row in df.iterrows():
        try:
            txn = {
                "txn_id":      str(row["txn_id"]).strip(),
                "date":        _parse_date(row["date"]),
                "description": str(row["description"]).strip(),
                "amount":      float(row["amount"]),
                "currency":    str(row.get("currency", "GBP")).strip(),
                "merchant":    str(row["merchant"]).strip() if pd.notna(row.get("merchant")) else None,
                "account_id":  str(row["account_id"]).strip() if pd.notna(row.get("account_id")) else None,
            }
            transactions.append(txn)
        except (ValueError, TypeError) as e:
            print(f"Warning: skipping row {row.get('txn_id', '?')} — {e}")
            continue

    return transactions

def _parse_date(value)-> str:
    #Accept multiple date formats and return a consistent YYYY-MM-DD string

    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
 
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S"]
    for fmt in formats:
        try:
            return datetime.strptime(str(value).strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
 
    raise ValueError(f"Unrecognised date format: '{value}'")
   

   