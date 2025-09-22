from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_community.callbacks.manager import get_openai_callback
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import Command
import os
import sys
import json
import asyncio
import traceback
from dotenv import load_dotenv
from add_interrupt import add_human_in_the_loop, human_in_the_loop_prompt

# OpenAI APIキーを環境変数に設定しておく
# .envというファイルを作成し、OPENAI_API_KEY=<API KEY>を記載する
load_dotenv()

# OpenAIのモデルのインスタンスを作成
# max_tokensで使用トークン量に制限をかける
# max_token*100くらいが実際の制限値？
llm = ChatOpenAI(
    model_name="gpt-5",
    temperature=0,
    max_tokens=100000,
)

initial_messages = [
    SystemMessage(
        content=(
            "あなたは優秀なオペレータです。"
            "ファイルを読み書きしたいときは/tmpディレクトリ以下を使ってください。"
            "exec_shell_commandツールでコマンド実行できます。"
        )
    ),
]

client = MultiServerMCPClient(
    {
        "ExecuteCommand": {
            "command": "python",
            "args": ["/app/exec_mcp.py"],
            "transport": "stdio",
        },
    }
)


async def agent_invoke(agent, messages):
    response = None
    thread_config = {"configurable": {"thread_id": "1"}}

    with get_openai_callback() as cb:
        response = await agent.ainvoke(
            {"messages": messages},
            thread_config
        )

        while True:
            interrupt = response.get("__interrupt__")
            if interrupt is None:
                break
            else:
                cmd = human_in_the_loop_prompt(interrupt)
                response = await agent.ainvoke(cmd, thread_config)

        for msg in response["messages"]:
            msg.pretty_print()

        print(f"🔢 使用トークン数: {cb.total_tokens}")
        print(f"📥 入力トークン: {cb.prompt_tokens}")
        print(f"📤 出力トークン: {cb.completion_tokens}")
        print(f"💰 推定コスト: ${cb.total_cost:.6f}")

    return response


async def main():
    tools = await client.get_tools()

    # human in the loopをtoolsに追加
    checked_tools = []
    for tool in tools:
        checked_tool = add_human_in_the_loop(tool)
        checked_tools.append(checked_tool)

    # human in the loop用のメモリ機能
    checkpointer = InMemorySaver()

    agent = create_react_agent(
        model=llm,
        tools=checked_tools,
        checkpointer=checkpointer
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

            # InMemorySaverで状態保持のため新規メッセージのみ追加
            result_response = await agent_invoke(agent, [human_message])
            messages = result_response["messages"]
        except Exception as e:
            print(f"[✗] エージェント実行エラー: {e}")
            traceback.print_exc()
            messages = old_messages

if __name__ == "__main__":
    asyncio.run(main())

