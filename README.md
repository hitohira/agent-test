# agent-test

AIエージェントの動作理解用のテスト実装です。

## simple-weather

MCPを使わずにLangChainからOpenAIのAPIを実行して天気予報します。

## mcp-weather

MCPを使ってLangGraphからOpenAIのAPIを実行して天気予報します。
MCPサーバとして天気情報を取得するWeatherとダミーのRoomStatusNowを作成しています。
賢いモデルだとWeatherのみ呼び出しますが、そうでないモデルは両方呼び出すことがあります。

## 注意事項

天気予報には天気予報APIを使用しています。
コードを実行する場合は事前に使用条件等をご確認ください。
https://weather.tsukumijima.net/

OpenAIのAPIは利用者がAPIキーを取得し、.envファイルに設定する必要があります。
OPENAI\_API\_KEY=APIキーの値
APIの料金は利用者が支払うことになります。


