from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import json
from app import process_df

app = FastAPI()

class StudentData(BaseModel):
    students: list[dict]

@app.post("/analyze")
def analyze_students(data: StudentData):
    try:
        # Convert incoming JSON list to DataFrame
        df = pd.DataFrame(data.students)
        # Apply the same logic as Streamlit app
        processed_df = process_df(df.to_json())
        
        # We need to parse swot_json back to dict so it serializes cleanly
        records = processed_df.to_dict(orient='records')
        for r in records:
            if 'swot_json' in r:
                r['swot'] = json.loads(r['swot_json'])
                del r['swot_json']
                
        return {"status": "success", "data": records}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
