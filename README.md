# agent-test

AIエージェントの動作理解用のテスト実装です。

## simple-weather

MCPを使わずにLangChainからOpenAIのAPIを実行して天気予報します。

## mcp-weather

MCPを使ってLangGraphからOpenAIのAPIを実行して天気予報します。  
MCPサーバとして天気情報を取得するWeatherとダミーのRoomStatusNowを作成しています。  
賢いモデルだとWeatherのみ呼び出しますが、そうでないモデルは両方呼び出すことがあります。

## file-edit

FileIO用のMCPサーバを定義してAIエージェントがファイル操作します。  
make runではDocker上の/tmpで操作され、実行終了後ファイルはなくなります。  
make localするとmount/以下にファイル生成されます。  

## agent-exec

file-editにさらにAIエージェントが作成したPythonファイルを実行できる機能を付加しました。  
AIが計算して答えを導くことが可能です。  
エージェントが強い実行権限を持っているので扱いは気を付けてください。  
Docker上で実行させること、デフォルトとrequirements.txtでインストールしたモジュールしか使えないことでAIの実行影響を制限しています。  
対話できないので最初に一回指示を与えることしかできません。  


## 注意事項

天気予報には天気予報APIを使用しています。  
コードを実行する場合は事前に使用条件等をご確認ください。  
https://weather.tsukumijima.net/

OpenAIのAPIは利用者がAPIキーを取得し、.envファイルに設定する必要があります。  
`OPENAI_API_KEY=APIキーの値`  

APIの料金は利用者が支払うことになります。
