import time
import uuid

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request

app = FastAPI()

ALLOWED_ORIGIN = "https://dash-7ot2nh.example.com"
EMAIL = "24f2006261@ds.study.iitm.ac.in"

# --- CORS (added first so it wraps OUTSIDE the timing middleware below) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


# --- Custom middleware: X-Request-ID + X-Process-Time on every response ---
@app.middleware("http")
async def add_custom_headers(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{duration:.6f}"
    return response


@app.get("/stats")
async def stats(values: str = Query(..., description="Comma-separated integers")):
    raw_parts = values.split(",")
    parsed = []
    for part in raw_parts:
        part = part.strip()
        if part == "":
            continue
        try:
            parsed.append(int(part))
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid integer value: '{part}'",
            )

    if not parsed:
        raise HTTPException(status_code=400, detail="No valid integers provided")

    count = len(parsed)
    total = sum(parsed)
    minimum = min(parsed)
    maximum = max(parsed)
    mean = total / count

    return {
        "email": EMAIL,
        "count": count,
        "sum": total,
        "min": minimum,
        "max": maximum,
        "mean": mean,
    }


@app.get("/")
async def root():
    return {"status": "ok"}
