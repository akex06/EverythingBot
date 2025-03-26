import sqlite3


class DB:
    def __init__(self, fp: str = "database.sqlite3") -> None:
        self.conn = sqlite3.connect(fp)
        self.c = self.conn.cursor()

        self.create_tables()

    def create_tables(self) -> None:
        self.c.execute("CREATE TABLE IF NOT EXISTS access_tokens (user INTEGER, access_token TEXT)")
        self.conn.commit()

    def get_access_token(self, id_: int) -> str:
        self.c.execute(
            "SELECT access_token FROM access_tokens WHERE user = ?",
            (id_,)
        )
        access_token = self.c.fetchone()

        return access_token[0] if access_token is not None else None

    def set_access_token(self, user: int, access_token: str) -> None:
        if self.get_access_token(user) is None:
            self.c.execute("INSERT INTO access_tokens VALUES (?, ?)", (user, access_token))
        else:
            self.c.execute("UPDATE access_tokens SET access_token = ? WHERE user = ?", (access_token, user))
        self.conn.commit()

    def remove_access_token(self, user: int) -> None:
        self.c.execute("DELETE FROM access_tokens WHERE user = ?", (user, ))
        self.conn.commit()

    def get_all(self) -> list[str]:
        self.c.execute("SELECT * FROM access_tokens")
        return self.c.fetchall()
