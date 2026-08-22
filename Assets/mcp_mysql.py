
from mcp.server.fastmcp import FastMCP
import mysql.connector
import os

mcp = FastMCP("mcp-mysql")

# --- MySQL 連線設定 ---
# 建議使用環境變數來設定這些值以策安全
DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = "howareyou"
DB_NAME = "sales"

def get_db_connection():
    """建立到 MySQL 資料庫的連線。"""
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

@mcp.tool()
def sql_query(sql):
    """
    輸入 SQL 指令，會從 MySQL 中執行。
    將搜尋到的資料回傳成字串，每列換行，每欄位用逗號分隔。
    當不知道資料庫結構時，可以先呼叫get_schema()

    Args:
        sql: str, SQL 查詢語句

    Returns:
        str: 查詢結果的文字表示
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        # 將每列資料轉成逗號分隔的字串
        result_lines = [", ".join(map(str, row)) for row in rows]
        result_str = "\n".join(result_lines)
        return result_str
    except mysql.connector.Error as e:
        return f"SQL 執行錯誤: {e}"
    finally:
        if conn and conn.is_connected():
            conn.close()


@mcp.tool()
def get_schema():
    """
    回傳整個 MySQL 資料庫的 schema (所有資料表的建立語法)
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 取得所有資料表名稱
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        
        schemas = []
        for (table_name,) in tables:
            # 取得每個資料表的 CREATE TABLE 語法
            cursor.execute(f"SHOW CREATE TABLE `{table_name}`;")
            # SHOW CREATE TABLE 的結果是一個元組 (table_name, create_statement)
            schema_result = cursor.fetchone()
            if schema_result and len(schema_result) > 1:
                schemas.append(schema_result[1])

        # 將所有 schema 組合成一個字串
        schema_text = ";\n\n".join(schemas) + ";"
        return schema_text       
    except mysql.connector.Error as e:
        return f"SQL 執行錯誤: {e}"
    finally:
        if conn and conn.is_connected():
            conn.close()


if __name__ == "__main__":
    mcp.run(transport='stdio')

