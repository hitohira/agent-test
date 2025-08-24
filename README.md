# agent-test

AIエージェントの動作理解用のテスト実装です。

## simple-weather

MCPを使わずにLangChainからOpenAIのAPIを実行して明日の天気とおすすめの服装を教えてくれます。

## mcp-weather

MCPを使ってLangGraphからOpenAIのAPIを実行して明日の天気とおすすめの服装を教えてくれます。  
MCPサーバとして天気情報を取得するWeatherとダミーのRoomStatusNowを作成しています。  
賢いモデルだとWeatherのみ呼び出しますが、そうでないモデルは両方呼び出すことがあります。

## file-edit

FileIO用のMCPサーバを定義してAIエージェントがファイル操作します。  
make runではDocker上の/tmpで操作され、実行終了後ファイルはなくなります。  
make localするとmount/以下にファイル生成されます。  

## mcp-exec

file-editにさらにAIエージェントが作成したPythonファイルを実行できる機能を付加しました。  
AIが計算して答えを導くことが可能です。  
エージェントが強い実行権限を持っているので扱いは気を付けてください。  
Docker上の非rootユーザで実行させることでAIの実行影響を制限しています。 
ただし、作成したファイル内でsubprocessを使うことでOSコマンド実行が可能になっています。   
対話できないので最初に一回指示を与えることしかできません。  

## diag-agent-exec

mcp-execを機能強化し、対話形式でユーザが指示を出せるようにしました。  
mcp-exec同様にAIエージェントが強い権限を持つので注意してください。  
Pythonのモジュールがない場合はsys.executable -m pip install モジュール名を実行させることでDocker内にインストールさせられます。。  
対話では過去のメッセージを全て保持するので、やり取りが長くなるほど課金額が大きくなります。  
pytestとflake8のrequirements.txtに追加しました。実行時にはスクリプト内からpytest.main()を実行させるなどする必要があります。  

## 注意事項

天気予報には天気予報APIを使用しています。  
コードを実行する場合は事前に使用条件等をご確認ください。  
https://weather.tsukumijima.net/

OpenAIのAPIは利用者がAPIキーを取得し、.envファイルに設定する必要があります。  
`OPENAI_API_KEY=APIキーの値`  

APIの料金は利用者が支払うことになります。


## 実行方法

makeとdockerがインストール済みであることが前提となります。  

各ディレクトリに入ってdockerイメージをbuildします。
`make build`

次にdockerイメージを起動してPythonスクリプトを実行します。
`make run`または`make local`  
runでは作成したファイルは実行終了時に削除されます。  
localではローカルのmountディレクトリに生成したファイルが残ります。  

実行結果サンプルをlogsディレクトリにいくつか格納しました。


## コードの説明

### ディレクトリ後続
mcp-weatherの場合、以下のようなディレクトリ構造となります。  
他の機能もほぼ同様です。

```
mcp-weather/  
 ├── Makefile  
 ├── Dockerfile  
 ├── requirements.txt  
 └── app/  
     ├── mcp_test.py  
     ├── room_mcp.py  
     ├── weather.py  
     └── weather_mcp.py  
```

Makefileはdockerコマンドをラッパーして実行しやすくするmakeの定義を記載しています。  
Dockerfileはapp以下をデプロイするdockerイメージを記載しています。  
requirements.txtはdockerにインストールするpythonモジュールを記載しています。  
app以下は実行されるPythonファイルと、MCPを定義したファイルを配置しています。  

### コードの内容

MCPサーバを定義しているweather\_mcp.pyについて中身を見ます。
```
from mcp.server.fastmcp import FastMCP
import weather
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

mcp = FastMCP("Weather")

@mcp.tool()
def get_weather(weather_code: str) -> dict:
    """ 天気予報APIからwather_codeの天気を取得する。東京の場合は130010 """
    return weather.get(weather_code)


if __name__ == "__main__":
    mcp.run(transport="stdio")
```
内容はシンプルで、
` mcp = FastMCP("Weather")`にMCPの名前つけるのと、
MCPとして提供したい関数に`@mcp.tool()`をつけていくのが修正箇所で簡単にMCPで機能をAIに提供できます。


次にメイン処理であるmcp\_test.pyを見ます。
```
# OpenAI APIキーを環境変数に設定しておく
# .envというファイルを作成し、OPENAI_API_KEY=<API KEY>を記載する
load_dotenv()
```
こちらで.envというファイルを読み込んでAPIキー情報を環境変数としてexportします。  
.envはgitにアップしていないので利用者が作成する必要があります。

```
# OpenAIのモデルのインスタンスを作成
llm = ChatOpenAI(
    model_name="gpt-4.1",
    temperature=0,
)
```
ここで使用する生成AIの種類を定義しています。今回はgpt-4.1を使用しています。

```
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
```
ここで先ほど定義したWeatherのMCPなどを生成AIが認識できるようなオブジェクトを作成しています。  
argsのファイルパスが/appで始まるのは、Dockerコンテナ上でappを/以下に配置しているためです。

```
async def main():
    response = None
    tools = await client.get_tools()
    agent = create_react_agent(
        llm,
        tools,
    )
```
ここで前2つで定義していた生成AIとMCPのツール群からAIエージェントを作成しています。

```
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
```
最後にagent.ainvokeで生成AIにメッセージを渡して処理を実行させています。

### カスタマイズ性について

このように非常にシンプルな形でMCPを実装することができます。  
MCP部分に自分が提供したい機能を実装していき、`client = MultiServerMCPClient`の部分で読み込ませることで簡単に機能追加できます。

こう考えると、ファイルの読み書きとファイルの実行権限を与えれば勝手にスクリプトを書いて実行してくれるエージェントが作れそうに思えます。  
そうして実際に作ったのがdiag-agent-execになります。

### エージェントの対話機能

エージェントを作るにあたって人間と複数回会話のキャッチボールをする必要があります。

```
        response = await agent.ainvoke(
            {"messages": messages}
        )
```
エージェント実行の戻り値の`response["messages"]`に今までのやり取りが全て含まれています。

```
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
```
このように、ループで
 - ユーザからの入力受け取り
 - メッセージ履歴の末尾に追加
 - エージェント実行

を繰り返すことで対話を継続的に実行することができるようになりました。

## セキュリティ

mcp-execやdiag-agent-execではAIエージェントがかなり強い権限を持っています。  
与える指示によっては問題のある挙動を示す可能性があります。  
利用者の責任で使用してください。  

Dockerの機能でいくつか制限は入れています。  
まず、Dockerを使うことによってホストのコンピュータへの影響を最小限にしています。  
また、実行権限は非rootの一般ユーザとしています。
```
# 一般ユーザ作成
RUN useradd -m pyuser
```
```
# 一般ユーザに切り替え
USER pyuser
```

`make run`で実行の場合、ホストのコンピュータ側のファイルへアクセスできません。
```
run:
	docker run -it --rm $(IMAGE_NAME)
```

`make local`で実行する場合はカレントディレクトリ以下のmountディレクトリのみ操作権限があります。  
これは、dockerコンテナ起動時にmountディレクトリをDocker内の/tmpにマウントしているためです。
```
local:
	docker run -it -v $(CURDIR)/mount:/tmp --rm $(IMAGE_NAME)
```

利用者側で追加で実施できるセキュリティ対策としては、 
 - Dockerから外部への通信を制限する
 - コマンド実行前にユーザ側で確認が必要にする

などが考えられます。
