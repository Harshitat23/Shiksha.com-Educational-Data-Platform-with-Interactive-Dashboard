from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import json
import os
import re

app = FastAPI(title="Shiksha College Data API")

# Enable CORS so frontend apps can access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "colleges_simple.json"
colleges_data = []

@app.on_event("startup")
def load_data():
    global colleges_data
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            colleges_data = json.load(f)
    else:
        print(f"⚠️ Warning: {DATA_FILE} not found. Please run the scraper first.")

@app.get("/")
async def root():
    return {"message": "Welcome to Shiksha College Data API"}

def parse_fee_to_lakhs(fee_str: str) -> Optional[float]:
    """Parse fee string like '₹ 2.5 lakh' or '₹ 1 crore' into lakhs (float)."""
    if not fee_str:
        return None
    fee_str = fee_str.replace(",", "").lower()
    match = re.search(r'₹\s*([\d.]+)\s*(lakh|lac|crore)?', fee_str)
    if match:
        amount = float(match.group(1))
        unit = match.group(2)
        if unit in ['lakh', 'lac']:
            return amount
        elif unit == 'crore':
            return amount * 100
        else:
            # Assume amount is in rupees, convert to lakhs
            return amount / 100000
    return None

@app.get("/colleges", summary="Get list of colleges with optional filters")
async def get_colleges(
    name: Optional[str] = Query(None, description="Filter by college name (case-insensitive substring)"),
    location: Optional[str] = Query(None, description="Filter by location (case-insensitive exact match)"),
    min_ranking: Optional[int] = Query(None, description="Minimum ranking (inclusive)"),
    max_ranking: Optional[int] = Query(None, description="Maximum ranking (inclusive)"),
    min_fee: Optional[float] = Query(None, description="Minimum fee in lakhs (inclusive)"),
    max_fee: Optional[float] = Query(None, description="Maximum fee in lakhs (inclusive)"),
    limit: int = Query(50, gt=0, le=100, description="Max number of results to return"),
):
    results = colleges_data

    # Filter by name substring (case-insensitive)
    if name:
        results = [c for c in results if name.lower() in c.get("name", "").lower()]

    # Filter by location exact match (case-insensitive), only if location is set on college
    if location:
        results = [
            c for c in results
            if c.get("location") and c["location"].lower() == location.lower()
        ]

    # Filter by min ranking (include colleges missing ranking)
    if min_ranking is not None:
        results = [
            c for c in results
            if (c.get("ranking") and c["ranking"].isdigit() and int(c["ranking"]) >= min_ranking)
            or (not c.get("ranking"))
        ]

    # Filter by max ranking (include colleges missing ranking)
    if max_ranking is not None:
        results = [
            c for c in results
            if (c.get("ranking") and c["ranking"].isdigit() and int(c["ranking"]) <= max_ranking)
            or (not c.get("ranking"))
        ]

    # Filter by min fee (include colleges with missing/invalid fee)
    if min_fee is not None:
        results = [
            c for c in results
            if (fee := parse_fee_to_lakhs(c.get("fees", ""))) is None or fee >= min_fee
        ]

    # Filter by max fee (include colleges with missing/invalid fee)
    if max_fee is not None:
        results = [
            c for c in results
            if (fee := parse_fee_to_lakhs(c.get("fees", ""))) is None or fee <= max_fee
        ]

    return {"count": len(results), "colleges": results[:limit]}
