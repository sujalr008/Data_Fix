import io
import math
import pandas as pd
import numpy as np
from typing import Tuple, List, Dict, Any

def sanitize_records(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    sanitized = []
    for r in records:
        clean_row = {}
        for k, v in r.items():
            if v is None:
                clean_row[k] = None
            elif isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
                clean_row[k] = None
            elif pd.isna(v):
                clean_row[k] = None
            elif isinstance(v, (np.generic,)):
                item = v.item()
                clean_row[k] = None if (isinstance(item, float) and math.isnan(item)) else item
            else:
                clean_row[k] = v
        sanitized.append(clean_row)
    return sanitized

class ParserService:
    @staticmethod
    def parse_file(content: bytes, filename: str) -> Tuple[List[Dict[str, Any]], List[str], str]:
        ext = filename.lower().split('.')[-1]
        if ext == 'csv':
            file_type = 'csv'
            try:
                df = pd.read_csv(io.BytesIO(content), encoding='utf-8')
            except UnicodeDecodeError:
                df = pd.read_csv(io.BytesIO(content), encoding='latin-1')
        elif ext in ['xlsx', 'xls']:
            file_type = 'xlsx'
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise ValueError('Unsupported file format. Please upload a CSV or XLSX file.')

        df.columns = [str(c).strip() for c in df.columns]
        columns = list(df.columns)
        records = df.to_dict(orient='records')
        clean_records = sanitize_records(records)
        
        return clean_records, columns, file_type

    @staticmethod
    def export_csv(records: List[Dict[str, Any]], columns: List[str]) -> bytes:
        df = pd.DataFrame(records)
        for col in columns:
            if col not in df.columns:
                df[col] = None
        df = df[columns] if len(columns) > 0 else df
        output = io.StringIO()
        df.to_csv(output, index=False)
        return output.getvalue().encode('utf-8')

    @staticmethod
    def export_xlsx(records: List[Dict[str, Any]], columns: List[str]) -> bytes:
        df = pd.DataFrame(records)
        for col in columns:
            if col not in df.columns:
                df[col] = None
        df = df[columns] if len(columns) > 0 else df
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)
        return output.getvalue()
