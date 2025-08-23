import requests
import json
import os
import time
from datetime import datetime, timedelta



def get(weather_code="130010"):
    """
		    天気コードの天気情報をAPIから取得。デフォルトは東京
        天気APIの利用条件等は以下のページから確認すること
				https://weather.tsukumijima.net/
		"""
    if not weather_code.isdigit():
        return {"message": "天気コードが誤っています"}

    url = "https://weather.tsukumijima.net/api/forecast/city/{code}".format(code=weather_code)
    cache_dir = "/tmp"
    cache_file = os.path.join(cache_dir, "weather_cache_{code}.json").format(code=weather_code)
    cache_duration = timedelta(hours=3)

    # キャッシュディレクトリがなければ作成
    os.makedirs(cache_dir, exist_ok=True)

    # キャッシュが存在し、3時間以内ならそれを使う
    if os.path.exists(cache_file):
        last_modified = datetime.fromtimestamp(os.path.getmtime(cache_file))
        if datetime.now() - last_modified < cache_duration:
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                print("✅ キャッシュから取得しました")
                # print(json.dumps(cached_data, indent=2, ensure_ascii=False))
                return cached_data

    # GETリクエストを送信
    response = ""

    try:
        response = requests.get(url)
    except Exception as e:
        print("API ERROR: {e}".format(e))
        return {"message": "APIエラー"}
    
    # ステータスコードを確認
    if response.status_code == 200:
        # JSONデータを辞書として取得
        data = response.json()

        if(data.get("error")):
            print("❌ データ取得に失敗しました。: ", data.get("error"))
            return {"message": data.get("error")}

        # 不要なフィールドを削除
        data["copyright"] = ""
        data["description"]["bodyText"] = ""
        data["description"]["headlineText"] = ""
        data["link"] = ""

        # キャッシュに保存
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print("🌐 APIから取得しました")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return data
    else:
        print("❌ データ取得に失敗しました。ステータスコード:", response.status_code)
        return {"message": "データ取得に失敗しました"}


if __name__ == "__main__":
    get()

