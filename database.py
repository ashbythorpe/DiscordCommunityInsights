import sqlite3

DATABASE_FILE = "database.db"

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

def read_messages():
    """Connect to the database and read all messages"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM Messages")
        messages = cursor.fetchall()

        print("Messages:")
        for msg in messages:
            print(msg)

        conn.close()
    except sqlite3.Error as e:
        print(e)

read_messages()
