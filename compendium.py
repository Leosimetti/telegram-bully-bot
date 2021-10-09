import sqlite3
import os

DB_PATH = "chats.db"
conn = sqlite3.connect(DB_PATH)


def with_cursor(func):
    def wrapper(*args, **kwargs):
        cursor = conn.cursor()
        func(cursor=cursor, *args, **kwargs)
        cursor.close()
        conn.commit()

    return wrapper


@with_cursor
def create_chat(chat_id: int, cursor: sqlite3.Cursor):
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS chat(?) (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT UNIQUE NOT NULL,
            frequency INTEGER NOT NULL DEFAULT 0
        )
        """, (chat_id,))


@with_cursor
def insert_message(chat_id: int, text: str, cursor: sqlite3.Cursor) -> None:
    cursor.execute(
        """
        UPDATE OR IGNORE
            chat(?) 
        SET
            frequency = frequency + 1
        WHERE
            text = (?) 
        """, (chat_id, text)
    )

    cursor.execute(
        """
        INSERT OR IGNORE INTO chat(?) VALUES(?)
        """, (chat_id, text)
    )


@with_cursor
def read_dataset(chat_id: int, cursor: sqlite3.Cursor) -> str:
    cursor.execute(
        """
        SELECT 
            text
        FROM
            chat(?)
        """,
        (chat_id, )
    )
    text = cursor.fetchall()
    return "\n".join(text)


def holy_words() -> str:
    import random
    return random.choice(["BEBRA", "BUBRA", "ХУЙ", "LALKA"])
