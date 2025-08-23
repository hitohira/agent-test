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

human_message =( 
    "1+1の結果を変数resultに入れた後resultの内容を出力するPythonコードを作成してファイルに書き出して。"
		"そのファイルを実行して結果を教えて。"
)

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

async def main(message=human_message):
    response = None
    tools = await client.get_tools()
    agent = create_react_agent(
        llm,
        tools,
    )

    messages = [
        SystemMessage(
            content=(
                "あなたは優秀なオペレータです。"
								"create_fileでpythonのファイルを作成した後にrun_python_fileを実行すれば実装した内容を実行できます。"
                "日付等の最新情報はpythonで計算する必要があります。"
            )            
        ),
        HumanMessage(
            content=message
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
    message_text = input("指示を入力してください: ").strip()
    if message_text == "":
        resp = asyncio.run(main())
    else:
        resp = asyncio.run(main(message_text))

