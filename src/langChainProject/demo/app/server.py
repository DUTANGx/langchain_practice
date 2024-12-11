#!/usr/bin/env python
"""Example LangChain server exposes an agent that has conversation history.

In this example, the history is stored entirely on the client's side.

Please see other examples in LangServe on how to use RunnableWithHistory to
store history on the server side.

Relevant LangChain documentation:

* Creating a custom agent: https://python.langchain.com/docs/modules/agents/how_to/custom_agent
* Streaming with agents: https://python.langchain.com/docs/modules/agents/how_to/streaming#custom-streaming-with-events
* General streaming documentation: https://python.langchain.com/docs/expression_language/streaming
* Message History: https://python.langchain.com/docs/expression_language/how_to/message_history

**ATTENTION**
1. To support streaming individual tokens you will need to use the astream events
   endpoint rather than the streaming endpoint.
2. This example does not truncate message history, so it will crash if you
   send too many messages (exceed token length).
3. The playground at the moment does not render agent output well! If you want to
   use the playground you need to customize its output server side using astream
   events by wrapping it within another runnable.
4. See the client notebook it has an example of how to use stream_events client-side!
"""  # noqa: E501
import os
from typing import Any, List, Union
from typing_extensions import Annotated

from fastapi import FastAPI, Header, HTTPException, Depends
from langchain.agents import AgentExecutor
from langchain.agents.format_scratchpad.openai_tools import (
    format_to_openai_tool_messages,
)
from langchain.agents.output_parsers.openai_tools import OpenAIToolsAgentOutputParser
from langchain_core.messages import AIMessage, FunctionMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain_core.utils.function_calling import format_tool_to_openai_tool
from langchain_openai import ChatOpenAI

from langserve import add_routes
from langserve.pydantic_v1 import BaseModel, Field

from functions import search, current_price, sentiment_indicator

# 设置环境变量
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["OPENAI_API_KEY"] = "sk-TYQdd18bab79e439b0c4248517a66af4827b9746bfadE5Pe"

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are very powerful assistant on crypto currencies, but bad at finding latest news, price, etc. "
            "Talk with the user as a financial consultant. "
            "If they ask you about latest news of crypto coin or sector, use search tool."
            "If they ask you about latest price of crypto coin, use price tool."
            "If they ask you about the sentiment of crypto coin or sector, use sentiment tool."
            "you can use one tool multiple times during one call.",
        ),
        # Please note the ordering of the fields in the prompt!
        # The correct ordering is:
        # 1. history - the past messages between the user and the agent
        # 2. user - the user's current input
        # 3. agent_scratchpad - the agent's working space for thinking and
        #    invoking tools to respond to the user's input.
        # If you change the ordering, the agent will not work correctly since
        # the messages will be shown to the underlying LLM in the wrong order.
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ]
)

tools = [
    Tool(
        name="search",
        func=search.run,
        description="useful for when you need to ask with search, such as latest information of a cryptocoin",
    ),
    Tool(
        name="price",
        func=current_price,
        description="get the latest price of a cryptocoin",
    ),
    Tool(
        name="sentiment",
        func=sentiment_indicator,
        description="get the latest close price and sentiment score of given symbol(cryptocoin symbol or sector) in past 7 days",
    )
]

# We need to set streaming=True on the LLM to support streaming individual tokens.
# Tokens will be available when using the stream_log / stream events endpoints,
# but not when using the stream endpoint since the stream implementation for agent
# streams action observation pairs not individual tokens.
# See the client notebook that shows how to use the stream events endpoint.
# llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, streaming=True)
llm = ChatOpenAI(
    base_url="https://api.gptsapi.net/v1",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
    model="gpt-4o-mini"
)


llm_with_tools = llm.bind(tools=[format_tool_to_openai_tool(tool) for tool in tools])

# ATTENTION: For production use case, it's a good idea to trim the prompt to avoid
#            exceeding the context window length used by the model.
#
# To fix that simply adjust the chain to trim the prompt in whatever way
# is appropriate for your use case.
# For example, you may want to keep the system message and the last 10 messages.
# Or you may want to trim based on the number of tokens.
# Or you may want to also summarize the messages to keep information about things
# that were learned about the user.
#
def prompt_trimmer(messages: List[Union[HumanMessage, AIMessage, FunctionMessage]]):
    '''Trims the prompt to a reasonable length.'''
    # Keep in mind that when trimming you may want to keep the system message!
    return messages[-10:] # Keep last 10 messages.

agent = (
    {
        "input": lambda x: x["input"],
        "agent_scratchpad": lambda x: format_to_openai_tool_messages(
            x["intermediate_steps"]
        ),
        "chat_history": lambda x: prompt_trimmer(x["chat_history"]),
    }
    | prompt
    # | prompt_trimmer # See comment above.
    | llm_with_tools
    | OpenAIToolsAgentOutputParser()
)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

async def verify_token(x_token: Annotated[str, Header()]):
    if x_token != "AlphaBrainV1":
        raise HTTPException(status_code=400, detail="X-Token header invalid")

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="Spin up a simple API server using LangChain's Runnable interfaces",
    dependencies=[Depends(verify_token)]
)


app.dependency_overrides[Depends] = verify_token


# We need to add these input/output schemas because the current AgentExecutor
# is lacking in schemas.
class Input(BaseModel):
    input: str
    # The field extra defines a chat widget.
    # Please see documentation about widgets in the main README.
    # The widget is used in the playground.
    # Keep in mind that playground support for agents is not great at the moment.
    # To get a better experience, you'll need to customize the streaming output
    # for now.
    chat_history: List[Union[HumanMessage, AIMessage, FunctionMessage]] = Field(
        ...,
        extra={"widget": {"type": "chat", "input": "input", "output": "output"}},
    )


class Output(BaseModel):
    output: Any


# Adds routes to the app for using the chain under:
# /invoke
# /batch
# /stream
# /stream_events
add_routes(
    app,
    agent_executor.with_types(input_type=Input, output_type=Output).with_config(
        {"run_name": "agent"}
    ),
)


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
