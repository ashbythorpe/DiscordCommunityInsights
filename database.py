import sqlite3
from discord.message import Message

DATABASE_FILE = "database.db"

class Database:
    connection: sqlite3.Connection
    cursor: sqlite3.Cursor

    def __init__(self) -> None:
        self.connection = sqlite3.connect("database.db")
        self.cursor = self.connection.cursor()

        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.cursor.execute("PRAGMA journal_mode = WAL")

        self._create_tables()

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
                created TIMESTAMP NOT NULL,
                userId INTEGER NOT NULL,
                channelId INTEGER NOT NULL,
                FOREIGN KEY (userId) REFERENCES Users(id) ON DELETE CASCADE,
                FOREIGN KEY (channelId) REFERENCES Channels(id) ON DELETE CASCADE
            )
        """)
    def save_message(self, message: Message) -> None:
        self.cursor.execute("""
            INSERT OR IGNORE INTO Guilds (id, name)
            VALUES (?, ?)
            """,
            (message.guild.id, message.guild.name),
        )

        self.cursor.execute("""
            INSERT OR IGNORE INTO Users (id, name)
            VALUES (?, ?)
        """,
            (message.author.id, message.author.name),
        )

        self.cursor.execute("""
            INSERT OR IGNORE INTO Channels (id, name, GuildId)
            VALUES (?, ?, ?)
        """,
            (message.channel.id, message.channel.name, message.guild.id),
        )

        self.cursor.execute(
        """
            INSERT OR IGNORE INTO Messages (id, content, created, userId, channelId)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                message.id,
                message.content,
                message.created_at,
                message.author.id,
                message.channel.id,
            ),
        )
        self.connection.commit()
    
    def close(self) -> None:
        self.connection.close()

    def get_messages(self) -> list[tuple[int, str, int, int]]:
        self.cursor.execute(
                "SELECT id, content, created, userId, channelId FROM Messages"
        )

        return self.cursor.fetchall()
    
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
    
#read_messages()


