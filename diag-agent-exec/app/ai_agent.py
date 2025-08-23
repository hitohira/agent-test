from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_community.callbacks.manager import get_openai_callback
from langchain_core.messages import HumanMessage, SystemMessage
import os
import sys
import json
import asyncio
from dotenv import load_dotenv

# OpenAI APIキーを環境変数に設定しておく
# .envというファイルを作成し、OPENAI_API_KEY=<API KEY>を記載する
load_dotenv()

# OpenAIのモデルのインスタンスを作成
# max_tokensで使用トークン量に制限をかける
# max_token*100くらいが実際の制限値？
llm = ChatOpenAI(
    model_name="gpt-4.1",
    temperature=0,
    max_tokens=1000,
)

initial_messages = [
    SystemMessage(
        content=(
            "あなたは優秀なオペレータです。"
            "create_fileでpythonのファイルを作成した後にrun_python_fileを実行すれば実装した内容を実行できます。"
            "日付等の最新情報はpythonで計算する必要があります。"
        )
    ),  
]

client = MultiServerMCPClient(
    {
        "FileIO": {
            "command": "python",
            "args": ["/app/file_io_mcp.py"],
            "transport": "stdio",
        },
        "ExecutePythonByFilename": {
            "command": "python",
            "args": ["/app/exec_py_mcp.py"],
            "transport": "stdio",
        },
    }
)


async def agent_invoke(agent, messages):
    response = None

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

async def main():
    tools = await client.get_tools()
    agent = create_react_agent(
        llm,
        tools,
    )

    messages = initial_messages
    print("🔁 入力を開始してください（'exit', 'quit', 空入力で終了）")

    while True:
        old_messages = messages.copy()
        user_input = input("user>>> ").strip()
        if user_input in ("exit", "quit", ""):
            print("👋 終了します")
            break
        try:
            human_message = HumanMessage(content=user_input)
            messages.append(human_message)

            result_response = await agent_invoke(agent, messages)
            messages = result_response["messages"]
        except Exception as e:
            print(f"[✗] エージェント実行エラー: {e}")
            messages = old_messages

if __name__ == "__main__":
    asyncio.run(main())

