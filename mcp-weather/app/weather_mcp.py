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

