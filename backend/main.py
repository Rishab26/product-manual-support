from fastapi import FastAPI
from pydantic import BaseModel
from agent import manual_agent
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ManualRequest(BaseModel):
    topic: str

@app.post("/generate-manual")
async def generate_manual(request: ManualRequest):
    result = await manual_agent.run(request.topic)
    print(f"Result type: {type(result)}")
    print(f"Result dir: {dir(result)}")
    return {"manual": result.data}

@app.get("/health")
async def health():
    return {"status": "ok"}
