import os
import json
from langchain.agents import AgentType, create_self_ask_with_search_agent
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI

# 设置环境变量
os.environ["SERPER_API_KEY"] = "575447666cc1aeeb781162501a327aca29467b31"
os.environ["OPENAI_API_KEY"] = "sk-TYQdd18bab79e439b0c4248517a66af4827b9746bfadE5Pe"

# 初始化搜索工具
search = GoogleSerperAPIWrapper()

# 初始化模型
model = ChatOpenAI(
    base_url="https://api.gptsapi.net/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-3.5-turbo"
)

# 定义工具
tools = [
    Tool(
        name="Intermediate Answer",
        func=search.run,
        description="useful for when you need to ask with search",
    )
]

# 使用新的代理构造方法创建代理
self_ask_with_search = create_self_ask_with_search_agent(
    llm=model,
    tools=tools
)

# 定义消息历史
inputs = {
    "messages": [
        {
            "role": "user",
            "content": "What is the latest price of Bitcoin? Where should I buy it?"
        }
    ]
}

# 将消息历史传递给代理并运行
response = self_ask_with_search(inputs)
print(response)
