import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import pandas as pd

from .models import AnalysisRequest
from .agents import analyze_debt, savings_strategy, budget_advice, debt_payoff, rag

load_dotenv()

app = FastAPI(title="Personalized Multi-Agent Financial Advisor")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory user doc store for demo
USER_DOCS = {}

@app.post('/ingest/upload_csv')
async def upload_csv(file: UploadFile = File(...), doc_id: str = None):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail='Only CSV supported in this endpoint')
    contents = await file.read()
    df = pd.read_csv(pd.io.common.BytesIO(contents))
    # for tabular RAG, join rows into text
    texts = []
    for idx, row in df.iterrows():
        texts.append(str(dict(row)))
    rag.add_texts(texts)
    if doc_id:
        USER_DOCS[doc_id] = texts
    return {"status": "ingested", "rows": len(texts)}

@app.post('/analyze/debt')
async def api_analyze_debt(req: AnalysisRequest):
    res = analyze_debt(req.user.dict())
    return res

@app.post('/analyze/savings')
async def api_savings(req: AnalysisRequest):
    res = savings_strategy(req.user.dict())
    return res

@app.post('/analyze/budget')
async def api_budget(req: AnalysisRequest):
    res = budget_advice(req.user.dict())
    return res

import os
import io
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import pandas as pd

from .models import AnalysisRequest
from .agents import analyze_debt, savings_strategy, budget_advice, debt_payoff, rag
from .market import get_quote, get_history

load_dotenv()

app = FastAPI(title="Personalized Multi-Agent Financial Advisor")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory user doc store for demo
USER_DOCS = {}


@app.post('/ingest/upload_csv')
async def upload_csv(file: UploadFile = File(...), doc_id: str = None):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail='Only CSV supported in this endpoint')
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    # for tabular RAG, join rows into text
    texts = []
    for idx, row in df.iterrows():
        texts.append(str(dict(row)))
    rag.add_texts(texts)
    if doc_id:
        USER_DOCS[doc_id] = texts
    return {"status": "ingested", "rows": len(texts)}


@app.get('/market/quote')
async def api_market_quote(symbol: str):
    try:
        q = get_quote(symbol)
        return q
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/market/history')
async def api_market_history(symbol: str, period: str = '1mo'):
    try:
        h = get_history(symbol, period=period)
        return h
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/analyze/debt')
async def api_analyze_debt(req: AnalysisRequest):
    res = analyze_debt(req.user.dict())
    return res


@app.post('/analyze/savings')
async def api_savings(req: AnalysisRequest):
    res = savings_strategy(req.user.dict())
    return res


@app.post('/analyze/budget')
async def api_budget(req: AnalysisRequest):
    res = budget_advice(req.user.dict())
    return res


@app.post('/analyze/debt_payoff')
async def api_debt_payoff(req: AnalysisRequest):
    res = debt_payoff(req.user.dict())
    return res


@app.get('/health')
async def health():
    return {"status": "ok"}


from fastapi import WebSocket, WebSocketDisconnect
import asyncio


@app.websocket('/ws/analyze')
async def websocket_analyze(ws: WebSocket):
    await ws.accept()
    try:
        payload = await ws.receive_json()
        action = payload.get('action')
        user = payload.get('user') or {}

        await ws.send_json({'type': 'status', 'msg': 'Starting analysis'})

        # simulate incremental progress and stream updates
        for i in range(3):
            await asyncio.sleep(0.5)
            await ws.send_json({'type': 'progress', 'percent': int((i+1) * 33), 'msg': f'Step {i+1} complete'})

        # dispatch to agent
        if action == 'debt':
            result = analyze_debt(user)
        elif action == 'savings':
            result = savings_strategy(user)
        elif action == 'budget':
            result = budget_advice(user)
        elif action == 'debt_payoff':
            result = debt_payoff(user)
        else:
            result = {'summary': f'Unknown action: {action}'}

        # final result
        await ws.send_json({'type': 'result', 'result': result})
        await ws.close()
    except WebSocketDisconnect:
        return
