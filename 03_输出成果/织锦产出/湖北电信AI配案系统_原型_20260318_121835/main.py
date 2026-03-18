#!/usr/bin/env python3
"""主程序入口"""

from fastapi import FastAPI

app = FastAPI(title="AI智能系统")

@app.get("/")
async def root():
    return {"message": "系统运行正常"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
