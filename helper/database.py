import motor.motor_asyncio
from config import DB_URL, DB_NAME

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.channels = self.db.channels  # Collection for channels
        self.posts = self.db.posts  # Collection for posts

    # Channel System
    async def add_channel(self, channel_id, channel_name=None):
        channel_id = int(channel_id)
        if not await self.is_channel_exist(channel_id):
            await self.channels.insert_one({"_id": channel_id, "name": channel_name})
            return True
        return False

    async def delete_channel(self, channel_id):
        await self.channels.delete_one({"_id": int(channel_id)})

    async def is_channel_exist(self, channel_id):
        return await self.channels.find_one({"_id": int(channel_id)}) is not None

    async def get_all_channels(self):
        return [channel async for channel in self.channels.find({})]

    # Post System
    async def save_latest_post(self, messages):
        await self.posts.update_one(
            {"_id": "latest_post"},
            {"$set": {"messages": messages}},
            upsert=True
        )

    async def get_latest_post(self):
        post = await self.posts.find_one({"_id": "latest_post"})
        return post.get("messages", {}) if post else {}

    async def delete_latest_post(self):
        await self.posts.delete_one({"_id": "latest_post"})

# Initialize the database
db = Database(DB_URL, DB_NAME)
