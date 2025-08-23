from mcp.server.fastmcp import FastMCP
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

mcp = FastMCP("RoomStatusNow")

@mcp.tool()
def get_room_status_now() -> dict:
    """
    現在の室内の気温、湿度、不快指数を取得する。
    不快指数の目安
    〜55	寒い
    55〜60	肌寒い
    60〜65	何も感じない
    65〜70	快適
    70〜75	人によっては暑い
    75〜80	半数以上が暑い
    80~	暑い
    """
    # ダミー実装
    return {"temperature": 27, "humidity": 60, "discomfort_index": 75.6}


if __name__ == "__main__":
    mcp.run(transport="stdio")

