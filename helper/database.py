import motor.motor_asyncio
from config import DB_URL, DB_NAME

class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.users = self.db.user  # Collection for users
        self.channels = self.db.channels  # Collection for channels

    def new_user(self, id):
        return dict(
            _id=int(id),
            file_id=None,
            caption=None
        )

    async def add_user(self, b, m):
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = self.new_user(u.id)
            await self.col.insert_one(user)            
            await send_log(b, u)

    async def is_user_exist(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.col.delete_many({'_id': int(user_id)})

    #======================= Thumbnail ========================#
    async def set_thumbnail(self, id, file_id):
        await self.col.update_one({'_id': int(id)}, {'$set': {'file_id': file_id}})

    async def get_thumbnail(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('file_id', None)

    #======================= Caption ========================#
    async def set_caption(self, id, caption):
        await self.col.update_one({'_id': int(id)}, {'$set': {'caption': caption}})

    async def get_caption(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('caption', None)

    #======================= Prefix ========================#
    async def set_prefix(self, id, prefix):
        await self.col.update_one({'_id': int(id)}, {'$set': {'prefix': prefix}})  

    async def get_prefix(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('prefix', None)      

    #======================= Suffix ========================#
    async def set_suffix(self, id, suffix):
        await self.col.update_one({'_id': int(id)}, {'$set': {'suffix': suffix}})  

    async def get_suffix(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('suffix', None)

    #======================= Metadata ========================#
    async def set_metadata(self, id, bool_meta):
        await self.col.update_one({'_id': int(id)}, {'$set': {'metadata': bool_meta}})

    async def get_metadata(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('metadata', None)

    #======================= Metadata Code ========================#    
    async def set_metadata_code(self, id, metadata_code):
        await self.col.update_one({'_id': int(id)}, {'$set': {'metadata_code': metadata_code}})

    async def get_metadata_code(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('metadata_code', None)   

    #======================= CHANNEL SYSTEM ========================#
    async def add_channel(self, channel_id):
        """Add a channel if it doesn't already exist."""
        channel_id = int(channel_id)  # Ensure ID is an integer
        if not await self.is_channel_exist(channel_id):
            await self.channels.insert_one({"_id": channel_id})
            return True  # Successfully added
        return False  # Already exists

    async def remove_channel(self, channel_id):
        """Remove a channel from the database."""
        channel_id = int(channel_id)
        await self.channels.delete_one({"_id": channel_id})

    async def is_channel_exist(self, channel_id):
        """Check if a channel is in the database."""
        return await self.channels.find_one({"_id": int(channel_id)}) is not None

    async def get_all_channels(self):
        """Retrieve all channel IDs as a list."""
        return [channel["_id"] async for channel in self.channels.find({})]

    #======================= FORMATTING SYSTEM ========================#
    async def save_formatting(self, channel_id, formatting_text):
        """Save or update formatting text for a channel."""
        await self.formatting.update_one(
            {"_id": int(channel_id)},
            {"$set": {"formatting_text": formatting_text}},
            upsert=True
        )

    async def get_formatting(self, channel_id):
        """Retrieve formatting text for a channel."""
        result = await self.formatting.find_one({"_id": int(channel_id)})
        return result.get("formatting_text") if result else None

# Initialize the database
db = Database(DB_URL, DB_NAME)

