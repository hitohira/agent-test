from mcp.server.fastmcp import FastMCP
import sys
import io
import os
import subprocess

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

mcp = FastMCP("ExecuteCommand")

tmp_dir = "/tmp"

@mcp.tool()
def exec_shell_command(command_string: str) -> dict:
    """
    指定された shellのコマンド文字列をsubprocessとして実行し、
    終了コード・標準出力・標準エラー出力を dict 型で返します。

    Args:
        command_string (str): shellの実行コマンド。例: 'ls -l'、'python test.py'

    Returns:
        dict: 実行結果を含む辞書。以下のキーを持ちます：
            - "returncode": 終了コード（int）
            - "stdout": 標準出力（str）
            - "stderr": 標準エラー出力（str）
    """
    try:
        result = subprocess.run(
            command_string,
            capture_output=True,
            text=True,
            shell=True,
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

