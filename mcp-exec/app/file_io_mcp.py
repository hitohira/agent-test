from mcp.server.fastmcp import FastMCP
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

mcp = FastMCP("FileIO")

tmp_dir = "/tmp"

@mcp.tool()
def create_file(filename: str, content: str = "") -> str:
    """
    指定されたファイル名で /tmp/ 以下にファイルを作成し、初期内容を書き込みます。

    Args:
        filename (str): 作成するファイル名。セキュリティのため basename のみ使用されます。
        content (str, optional): ファイルに書き込む初期内容。省略時は空文字列。

    Returns:
        str: 作成されたファイルの絶対パス。作成に失敗した場合は空文字列。
    """

    # パスを正規化して /tmp/ 以下に限定
    safe_filename = os.path.basename(filename)  # パスの逆走防止
    full_path = os.path.join(tmp_dir, safe_filename)

    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[✓] 作成完了: {full_path}")
        return full_path
    except Exception as e:
        print(f"[✗] 作成失敗: {e}")
        return ""


@mcp.tool()
def edit_file(filename: str, new_content: str) -> bool:
    """
    /tmp/ 以下に存在する指定ファイルの内容を新しい内容で上書きします。

    Args:
        filename (str): 編集対象のファイル名。basename のみ使用されます。
        new_content (str): ファイルに書き込む新しい内容。

    Returns:
        bool: 編集に成功した場合は True、ファイルが存在しないかエラーが発生した場合は False。
    """
    safe_filename = os.path.basename(filename)
    full_path = os.path.join(tmp_dir, safe_filename)

    if not os.path.exists(full_path):
        print(f"[✗] 編集失敗: ファイルが存在しません → {full_path}")
        return False

    try:
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"[✓] 編集完了: {full_path}")
        return True
    except Exception as e:
        print(f"[✗] 編集失敗: {e}")
        return False

@mcp.tool()
def delete_file(filename: str) -> bool:
    """
    /tmp/ 以下に存在する指定ファイルを削除します。

    Args:
        filename (str): 削除対象のファイル名。basename のみ使用されます。

    Returns:
        bool: 削除に成功した場合は True、ファイルが存在しないか削除に失敗した場合は False。
    """
    safe_filename = os.path.basename(filename)
    full_path = os.path.join(tmp_dir, safe_filename)

    if not os.path.exists(full_path):
        print(f"[✗] 削除失敗: ファイルが存在しません → {full_path}")
        return False

    try:
        os.remove(full_path)
        print(f"[✓] 削除完了: {full_path}")
        return True
    except Exception as e:
        print(f"[✗] 削除失敗: {e}")
        return False


@mcp.tool()
def read_and_print_file(filename: str) -> str:
    """
    /tmp/ 以下に存在する指定ファイルの内容を読み取り、文字列として返しつつ標準出力にも表示します。

    Args:
        filename (str): 読み取り対象のファイル名。basename のみ使用されます。

    Returns:
        str: ファイルの内容。ファイルが存在しないか読み取りに失敗した場合は空文字列。
    """
    safe_filename = os.path.basename(filename)
    full_path = os.path.join(tmp_dir, safe_filename)

    if not os.path.exists(full_path):
        print(f"[✗] 読み取り失敗: ファイルが存在しません → {full_path}")
        return ""

    try:
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"[✓] 読み取り成功: {full_path}")
        print("--- ファイル内容 ---")
        print(content)
        print("--------------------")
        return content
    except Exception as e:
        print(f"[✗] 読み取り失敗: {e}")
        return ""


if __name__ == "__main__":
    mcp.run(transport="stdio")

