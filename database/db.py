import asyncpg
import os

class DB:
    def __init__(self):
        self.pool = None

    async def on_startup(self):
        database_url = os.environ.get("DATABASE_URL")
        self.pool = await asyncpg.create_pool(dsn=database_url)
        await self.pool.execute("""
            CREATE TABLE IF NOT EXISTS users (
                verifed TEXT,
                user_id BIGINT PRIMARY KEY,
                lang TEXT,
                deposit TEXT DEFAULT 'none'
            )
        """)
        await self.pool.execute("""
            CREATE TABLE IF NOT EXISTS "desc" (
                ref TEXT
            )
        """)

    async def get_ref():
    default_ref = "https://1wzyuh.com/casino/list?open=register&p=xzni"  # Замените на реальный URL
    try:
        # Здесь должна быть ваша логика получения реферальной ссылки
        ref = await some_query()  # Например, из таблицы базы данных
        return ref if ref else default_ref
    except Exception:
        return default_ref

    async def edit_ref(self, url: str) -> None:
        await self.pool.execute('INSERT INTO "desc" (ref) VALUES ($1) ON CONFLICT (ref) DO UPDATE SET ref = $1', url)

    async def get_users_count(self) -> int:
        row = await self.pool.fetchrow("SELECT COUNT(*) FROM users")
        return row['count'] if row else 0

    async def get_verified_users_count(self) -> int:
        row = await self.pool.fetchrow("SELECT COUNT(*) FROM users WHERE verifed = 'verifed'")
        return row['count'] if row else 0

    async def register(self, user_id, language: str, verifed="0"):
        try:
            await self.pool.execute(
                "INSERT INTO users (verifed, user_id, lang, deposit) VALUES ($1, $2, $3, $4)",
                verifed, user_id, language, "none"
            )
        except asyncpg.UniqueViolationError:
            pass

    async def update_verifed(self, user_id, verifed="verifed"):
        await self.pool.execute(
            "UPDATE users SET verifed = $1 WHERE user_id = $2",
            verifed, user_id
        )

    async def get_user(self, user_id):
        row = await self.pool.fetchrow(
            "SELECT * FROM users WHERE user_id = $1 AND verifed = 'verifed'",
            user_id
        )
        return row

    async def get_user_info(self, user_id):
        row = await self.pool.fetchrow(
            "SELECT * FROM users WHERE user_id = $1",
            user_id
        )
        return row

    async def get_users(self):
        return await self.pool.fetch("SELECT * FROM users")

    async def update_lang(self, user_id, language: str):
        await self.pool.execute(
            "UPDATE users SET lang = $1 WHERE user_id = $2",
            language, user_id
        )

    async def get_lang(self, user_id):
        row = await self.pool.fetchrow(
            "SELECT lang FROM users WHERE user_id = $1",
            user_id
        )
        return row['lang'] if row else None

    async def update_deposit(self, user_id, deposit: str):
        await self.pool.execute(
            "UPDATE users SET deposit = $1 WHERE user_id = $2",
            deposit, user_id
        )

DataBase = DB()