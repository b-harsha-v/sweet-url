from fastapi import FastAPI

app = FastAPI(
    title="Enterprise URL Shortener",
    description="A high-throughput, low-latency URL shortening service.",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Returns the operational status of the service."""
    return {"status": "healthy", "service": "url-shortener"}