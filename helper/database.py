import motor.motor_asyncio
from config import DB_URL, DB_NAME

class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.user  # Collection for users
        self.channels = self.db.channels  # Collection for channels
        self.formatting = self.db.formatting  # Collection for formatting templates
        self.admins = self.db.admins  # Collection for admins
        self.posts = self.db.posts  # Collection for storing posts and their message IDs

    #============ User System ============#
    def new_user(self, id):
        return dict(
            _id=int(id),
            file_id=None,
            caption=None,
            prefix=None,
            suffix=None,
            metadata=False,
            metadata_code="By :- @Madflix_Bots"
        )

    async def add_user(self, id):
        if not await self.is_user_exist(id):
            user = self.new_user(id)
            await self.col.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return bool(user)

    async def total_users_count(self):
        return await self.col.count_documents({})

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_one({'_id': int(user_id)})

    # Thumbnail
    async def set_thumbnail(self, id, file_id):
        await self.col.update_one({'_id': int(id)}, {'$set': {'file_id': file_id}})

    async def get_thumbnail(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('file_id', None)

    # Caption
    async def set_caption(self, id, caption):
        await self.col.update_one({'_id': int(id)}, {'$set': {'caption': caption}})

    async def get_caption(self, id):
        user = await self.col.find_one({'_id': int(id)})
        return user.get('caption', None)

    #============ Channel System ============#
    async def add_channel(self, channel_id, channel_name):
        """Add a new channel to the database."""
        existing_channel = await self.channels.find_one({"_id": int(channel_id)})
        if not existing_channel:
            await self.channels.insert_one({"_id": int(channel_id), "name": channel_name})
            return True
        return False

    async def is_channel_exist(self, channel_id):
        """Check if a channel exists in the database."""
        return bool(await self.channels.find_one({"_id": int(channel_id)}))

    async def delete_channel(self, channel_id):
        """Remove a channel from the database."""
        await self.channels.delete_one({"_id": int(channel_id)})

    async def get_all_channels(self):
        """Retrieve all connected channels."""
        return await self.channels.find().to_list(None)

    #============ Post System ============#
    async def save_post_messages(self, post_id, sent_messages):
        """Save sent message IDs of a post for tracking and deletion."""
        await self.posts.update_one(
            {"_id": post_id},
            {"$set": {"messages": sent_messages}},
            upsert=True
        )

    async def get_post_messages(self, post_id):
        """Retrieve message IDs of a post."""
        post_data = await self.posts.find_one({"_id": post_id})
        return post_data["messages"] if post_data else {}

    async def delete_post_messages(self, post_id):
        """Delete post tracking data from the database."""
        await self.posts.delete_one({"_id": post_id})

    #============ Formatting System ============#
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
