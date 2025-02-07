import sqlite3


class Database:
    connection: sqlite3.Connection
    cursor: sqlite3.Cursor

    def __init__(self) -> None:
        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()

    def _create_tables(self) -> None:
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Guilds (
                id INTEGER NOT NULL PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Channels (
                id INTEGER NOT NULL PRIMARY KEY,
                name TEXT NOT NULL,
                GuildId INTEGER NOT NULL,
                FOREIGN KEY (GuildId) REFERENCES Guilds(id) ON DELETE CASCADE
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                id INTEGER NOT NULL PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Messages (
                id INTEGER NOT NULL PRIMARY KEY,
                content TEXT NOT NULL,
                userId INTEGER NOT NULL,
                channelId INTEGER NOT NULL,
                FOREIGN KEY (userId) REFERENCES Users(id) ON DELETE CASCADE,
                FOREIGN KEY (channelId) REFERENCES Channels(id) ON DELETE CASCADE
            )
        """)
