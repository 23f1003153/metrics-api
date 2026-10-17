import time
import uuid
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

EMAIL = "23f1003153@ds.study.iitm.ac.in"
ALLOWED_ORIGIN = "https://dash-3hsbzh.example.com"

app = FastAPI()

# The bouncer: only ONE origin is allowed, no "*"
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Process-Time"],
)

# The stamp machine: added AFTER the CORS one, so it wraps everything
# (even preflight replies get stamped)
@app.middleware("http")
async def add_stamps(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.6f}"
    return response


@app.get("/stats")
def stats(values: str = Query(...)):
    try:
        nums = [int(v) for v in values.split(",") if v.strip() != ""]
    except ValueError:
        raise HTTPException(status_code=400, detail="values must be integers")
    if not nums:
        raise HTTPException(status_code=400, detail="no values given")

    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": sum(nums),
        "min": min(nums),
        "max": max(nums),
        "mean": sum(nums) / len(nums),
    }
