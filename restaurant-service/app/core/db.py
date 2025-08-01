from prisma import Prisma

class Database:
    _instance: Prisma = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = Prisma()
        return cls._instance

    async def connect(self):
        if not self._instance.is_connected():
            await self._instance.connect()

    async def disconnect(self):
        if self._instance.is_connected():
            await self._instance.disconnect()


db = Database()

