import asyncpg
import os

class DB:
    def __init__(self):
        self.con = None

    async def on_startup(self):
        self.con = await asyncpg.connect(os.environ["DATABASE_URL"])

        # Создание таблиц, если их нет
        await self.con.execute("""
            CREATE TABLE IF NOT EXISTS users (
                verifed TEXT DEFAULT '0',
                user_id BIGINT PRIMARY KEY,
                lang TEXT
            )
        """)
        await self.con.execute("""
            CREATE TABLE IF NOT EXISTS desc (
                id SERIAL PRIMARY KEY,
                ref TEXT
            )
        """)
        # Установка начального значения рефералки, если таблица пуста
        count = await self.con.fetchval("SELECT COUNT(*) FROM desc")
        if count == 0:
            await self.con.execute("INSERT INTO desc (ref) VALUES ('https://your-default-link.com')")

    async def get_ref(self) -> str:
        query = 'SELECT ref FROM desc LIMIT 1'
        result = await self.con.fetchrow(query)
        return result['ref'] if result else 'https://your-default-link.com'

    async def set_ref(self, url: str) -> None:
        query = 'INSERT INTO desc (ref) VALUES ($1) ON CONFLICT (id) DO UPDATE SET ref = $1'
        await self.con.execute(query, url)
        await self.con.commit()

    async def get_users_count(self) -> int:
        query = "SELECT COUNT(*) FROM users"
        result = await self.con.fetchval(query)
        return result if result else 0

    async def get_verified_users_count(self) -> int:
        query = "SELECT COUNT(*) FROM users WHERE verifed = 'verifed'"
        result = await self.con.fetchval(query)
        return result if result else 0

    async def register(self, user_id, language: str, verifed="0"):
        try:
            query = "INSERT INTO users (verifed, user_id, lang) VALUES ($1, $2, $3) ON CONFLICT (user_id) DO NOTHING"
            await self.con.execute(query, (verifed, user_id, language))
            await self.con.commit()
        except Exception as e:
            print(f"Error registering user: {e}")

    async def update_verifed(self, user_id, verifed="verifed"):
        query = "UPDATE users SET verifed = $1 WHERE user_id = $2"
        await self.con.execute(query, (verifed, user_id))
        await self.con.commit()

    async def get_user(self, user_id):
        ver = "verifed"
        query = 'SELECT * FROM users WHERE user_id = $1 AND verifed = $2'
        result = await self.con.execute(query, (user_id, ver))
        return await result.fetchone()

    async def get_user_info(self, user_id):
        query = 'SELECT * FROM users WHERE user_id = $1'
        result = await self.con.execute(query, (user_id,))
        return await result.fetchone()

    async def get_users(self):
        query = "SELECT * FROM users"
        result = await self.con.execute(query)
        return await result.fetchall()

    async def update_lang(self, user_id, language: str):
        query = "UPDATE users SET lang = $1 WHERE user_id = $2"
        await self.con.execute(query, (language, user_id))
        await self.con.commit()

    async def get_lang(self, user_id):
        query = "SELECT lang FROM users WHERE user_id = $1"
        result = await self.con.execute(query, (user_id,))
        row = await result.fetchone()
        return row['lang'] if row else None

    async def close(self):
        if self.con:
            await self.con.close()

DataBase = DB()