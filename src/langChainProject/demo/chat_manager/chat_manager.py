from typing_extensions import Annotated
from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import List, Dict, Any
from pymongo import MongoClient
import requests


# MongoDB 配置
client = MongoClient('mongodb://admin:Qwe123!!!@43.134.11.45:27017/?authSource=admin')
db = client.chat_manager
collection = db.conversations

# LLM Agent 配置
LLM_AGENT_URL = "http://43.134.11.45:8000/invoke"  
headers = {
    'x-token': 'AlphaBrainV1',
    'Content-Type': 'application/json'
}

class QueryRequest(BaseModel):
    query: str
    user_id: str
    session_id: str

class ChatMessage(BaseModel):
    role: str
    content: str

class LLMInput(BaseModel):
    input: str
    chat_history: List[ChatMessage]

class LLMResponse(BaseModel):
    output: str
    # metadata: Dict[str, Any]

async def verify_token(x_token: Annotated[str, Header()]):
    if x_token != "AlphaBrainV1":
        raise HTTPException(status_code=400, detail="X-Token header invalid")

app = FastAPI(dependencies=[Depends(verify_token)])

@app.post("/invoke")
async def invoke_chat_manager(request: QueryRequest):
    user_id = request.user_id
    session_id = request.session_id
    query = request.query
    
    # 从 MongoDB 获取历史对话记录
    conversation = collection.find_one({"user_id": user_id, "session_id": session_id})
    
    if conversation:
        chat_history = conversation.get("chat_history", [])
    else:
        chat_history = []
        conversation = {"user_id": user_id, "session_id": session_id, "chat_history": []}
    
    chat_history.append({"role": "human", "content": query})

    # 构建 LLM Agent 请求的 payload
    llm_input = LLMInput(
        input=query,
        chat_history=[ChatMessage(**msg) for msg in chat_history]
    ).dict()
    
    # 调用 LLM Agent 接口
    response = requests.post(LLM_AGENT_URL, headers=headers, json={"input": llm_input})
    
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="LLM Agent error")
    
    response_json = response.json().get('output')
    print(response_json)
    try:
        llm_response = LLMResponse(**response_json)
    except:
        raise HTTPException(status_code=500, detail="LLM Output format error")
    
    # 将 LLM 的回答添加到对话历史记录中
    chat_history.append({"role": "ai", "content": llm_response.output})
    
    # 更新或插入对话记录到 MongoDB
    collection.update_one(
        {"user_id": user_id, "session_id": session_id},
        {"$set": {"chat_history": chat_history}},
        upsert=True
    )
    
    return llm_response

# 运行 FastAPI 服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)
