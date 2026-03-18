"""主程序入口"""
from fastapi import FastAPI

app = FastAPI(title="湖北电信AI配案系统")

@app.get("/")
async def root():
    return {"message": "系统运行正常"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
