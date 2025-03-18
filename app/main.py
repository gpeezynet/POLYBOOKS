from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import authentication, inventory, transaction, report

app = FastAPI(title="PolyBooks API", description="API for PolyBooks accounting system", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(authentication.router)
app.include_router(inventory.router)
app.include_router(transaction.router)
app.include_router(report.router)

@app.get("/")
async def root():
    return {"message": "Welcome to PolyBooks API. Visit /docs for documentation."}