import os
import json
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, FunctionMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

# 设置环境变量
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["TAVILY_API_KEY"] = "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"
os.environ["SERPER_API_KEY"] = "575447666cc1aeeb781162501a327aca29467b31"
os.environ["OPENAI_API_KEY"] = "sk-TYQdd18bab79e439b0c4248517a66af4827b9746bfadE5Pe"

# 初始化搜索工具
search = GoogleSerperAPIWrapper()
tools = [
    Tool(
        name="search",
        func=search.run,
        description="useful for when you need to ask with search",
    )
]

# 初始化模型
model = ChatOpenAI(
    base_url="https://api.gptsapi.net/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-3.5-turbo"
)

agent_executor = create_react_agent(model, tools)

response = agent_executor.invoke(
    {
        "messages": [
            # SystemMessage(content="You are very powerful assistant, but bad at finding latest news, price, weather, etc. If they ask you about latest situation, use search tool"),
            HumanMessage(content="What is the latest price of Bitcoin? How to buy bit coin on Biance?")
        ]
    }
)
print(response["messages"])