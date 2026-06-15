from fastapi import FastAPI, HTTPException
from parser import parse_gutenberg_book

app = FastAPI(title="Parser API")

@app.post("/parse")
def parse(url: str):
    try:
        result = parse_gutenberg_book(url)
        if result is None:
            raise HTTPException(status_code=500, detail="Failed to parse")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))