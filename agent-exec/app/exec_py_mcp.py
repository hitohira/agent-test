from mcp.server.fastmcp import FastMCP
import sys
import io
import os
import subprocess

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

mcp = FastMCP("ExecutePythonByFilename")

tmp_dir = "/tmp"

@mcp.tool()
def run_python_file(python_filename: str) -> dict:
    """
    指定された Python ファイルをsubprocessとして実行し、
    終了コード・標準出力・標準エラー出力を dict 型で返します。

    Args:
        filename (str): 実行するPython ファイル名。

    Returns:
        dict: 実行結果を含む辞書。以下のキーを持ちます：
            - "returncode": 終了コード（int）
            - "stdout": 標準出力（str）
            - "stderr": 標準エラー出力（str）
    """
    # パスを正規化して /tmp/ 以下に限定
    filename = python_filename
    safe_filename = os.path.basename(filename)  # パスの逆走防止
    full_path = os.path.join(tmp_dir, safe_filename)

    if not os.path.exists(full_path):
        return {
            "returncode": 1,
            "stdout": "",
            "stderr": "filename(" + filename +") does not exist."
        }

    try:
        result = subprocess.run(
            ["python", full_path],
            capture_output=True,
            text=True,
            check=False
        )
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        return {
            "returncode": 1,
            "stdout": "",
            "stderr": str(e)
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")

