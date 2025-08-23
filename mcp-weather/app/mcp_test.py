from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_community.callbacks.manager import get_openai_callback
from langchain_core.messages import HumanMessage, SystemMessage
import os
import json
import asyncio
from dotenv import load_dotenv

# OpenAI APIキーを環境変数に設定しておく
# .envというファイルを作成し、OPENAI_API_KEY=<API KEY>を記載する
load_dotenv()

# OpenAIのモデルのインスタンスを作成
llm = ChatOpenAI(
    model_name="gpt-4.1",
    temperature=0,
)

client = MultiServerMCPClient(
    {
        "Weather": {
            "command": "python",
            "args": ["/app/weather_mcp.py"],
            "transport": "stdio",
        },
        "RoomStatusNow": {
            "command": "python",
            "args": ["/app/room_mcp.py"],
            "transport": "stdio",
        },
    }
)

async def main():
    response = None
    tools = await client.get_tools()
    agent = create_react_agent(
        llm,
        tools,
    )

    messages = [
        SystemMessage(
            content=(
                "あなたは親しみやすいアナウンサーです。"
                "音声読み上げしやすいような150字程度の文章にしてください。"
            )            
        ),
        HumanMessage(
            content=(
                "明日の天気とおすすめの服装は？"
            )
        )
    ]

    with get_openai_callback() as cb:
        response = await agent.ainvoke(
            {"messages": messages}
        )

        for msg in response["messages"]:
            msg.pretty_print()

        print(f"🔢 使用トークン数: {cb.total_tokens}")
        print(f"📥 入力トークン: {cb.prompt_tokens}")
        print(f"📤 出力トークン: {cb.completion_tokens}")
        print(f"💰 推定コスト: ${cb.total_cost:.6f}")
    
    return response


if __name__ == "__main__":
    resp = asyncio.run(main())

