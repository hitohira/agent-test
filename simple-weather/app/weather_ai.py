import weather
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.callbacks.manager import get_openai_callback
import os
from dotenv import load_dotenv

# OpenAI APIキーを環境変数に設定しておく
# .envというファイルを作成し、OPENAI_API_KEY=<API KEY>を記載する
load_dotenv()

# OpenAIのモデルのインスタンスを作成
llm = ChatOpenAI(model_name="gpt-4.1-nano", temperature=0)

# プロンプトのテンプレート文章を定義
template = """
次のデータから{date}の天気とおすすめの服装を150文字程度で教えて。
音声読み上げしやすいように記号は使わず「30度」などの表記にして
======
{weather_data}
"""

# テンプレート文章にあるチェック対象の単語を変数化
prompt = ChatPromptTemplate.from_messages([
    ("system", "あなたは天気予報士です。"),
    ("user", template)
])

# チャットメッセージを文字列に変換するための出力解析インスタンスを作成
output_parser = StrOutputParser()

# OpenAIのAPIにこのプロンプトを送信するためのチェーンを作成
chain = prompt | llm | output_parser

def suggest(date="今日"):
    # チェーンを実行し、結果を表示
    with get_openai_callback() as cb:
        weather_data = weather.get()
        result = chain.invoke({"weather_data": weather_data, "date" : date})
        print(result)
        print(f"🔢 使用トークン数: {cb.total_tokens}")
        print(f"📥 入力トークン: {cb.prompt_tokens}")
        print(f"📤 出力トークン: {cb.completion_tokens}")
        print(f"💰 推定コスト: ${cb.total_cost:.6f}")

if __name__ == "__main__":
    # ユーザーに「今日」か「明日」を選ばせる
    choice = input("天気を知りたい日を入力してください（今日 / 明日）: ").strip()

    if choice in ["今日", "明日"]:
        suggest(date=choice)
    else:
        print("「今日」または「明日」と入力してください。")

