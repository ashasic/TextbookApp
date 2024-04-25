import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from textbook import textbook_router

app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Serve the main HTML page
@app.get("/")
async def read_index():
    return FileResponse("./frontend/index.html")


# Include the textbook router
app.include_router(textbook_router)

# Serve static files
app.mount("/", StaticFiles(directory="frontend"), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
