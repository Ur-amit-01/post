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
        self.posts = self.db.posts  # Collection for posts

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
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, user_id):
        await self.col.delete_many({'_id': int(user_id)})

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

    #============ Channel System ============#
    async def add_channel(self, channel_id, channel_name=None):
        """Add a channel if it doesn't already exist."""
        channel_id = int(channel_id)  # Ensure ID is an integer
        if not await self.is_channel_exist(channel_id):
            await self.channels.insert_one({"_id": channel_id, "name": channel_name})
            return True  # Successfully added
        return False  # Already exists

    async def delete_channel(self, channel_id):
        """Remove a channel from the database."""
        channel_id = int(channel_id)
        await self.channels.delete_one({"_id": channel_id})

    async def is_channel_exist(self, channel_id):
        """Check if a channel is in the database."""
        return await self.channels.find_one({"_id": int(channel_id)}) is not None

    async def get_all_channels(self):
        """Retrieve all channels as a list."""
        return [channel async for channel in self.channels.find({})]

    #============ Post System ============#
    async def save_post_messages(self, post_id, messages):
        """Save the message IDs of posts sent to channels with a unique post ID."""
        print(f"Saving post ID: {post_id}, Messages: {messages}")  # Debug: Check data being saved
        try:
            # Ensure post_id is a string
            post_id = str(post_id)
            # Ensure messages is a dictionary
            if not isinstance(messages, dict):
                raise ValueError("Messages must be a dictionary.")

            # Save to the database
            await self.posts.update_one(
                {"_id": post_id},
                {"$set": {"messages": messages}},
                upsert=True
            )
            print(f"Post ID {post_id} saved successfully!")  # Debug: Confirm save operation
        except Exception as e:
            print(f"Error saving post messages: {e}")  # Debug: Log any errors

    async def get_post_messages(self, post_id):
        """Retrieve the message IDs of posts sent to channels for a specific post ID."""
        print(f"Retrieving post ID: {post_id}")  # Debug: Check post_id being retrieved
        try:
            post = await self.posts.find_one({"_id": str(post_id)})  # Ensure post_id is treated as a string
            if post:
                print(f"Post found: {post}")  # Debug: Check retrieved post
                return post.get("messages", {})
            else:
                print(f"No post found with ID: {post_id}")  # Debug: Log if post not found
                return {}
        except Exception as e:
            print(f"Error retrieving post messages: {e}")  # Debug: Log any errors
            return {}

    async def delete_post_messages(self, post_id):
        """Delete the message IDs of a specific post."""
        print(f"Deleting post ID: {post_id}")  # Debug: Check post_id being deleted
        try:
            await self.posts.delete_one({"_id": str(post_id)})  # Ensure post_id is treated as a string
            print(f"Post ID {post_id} deleted successfully!")  # Debug: Confirm delete operation
        except Exception as e:
            print(f"Error deleting post messages: {e}")  # Debug: Log any errors

    async def get_most_recent_post_id(self):
        """Retrieve the most recent post ID."""
        print("Retrieving most recent post ID...")  # Debug: Log operation
        try:
            post = await self.posts.find_one(sort=[("_id", -1)])  # Sort by _id in descending order
            if post:
                print(f"Most recent post ID: {post['_id']}")  # Debug: Check retrieved post ID
                return post["_id"]
            else:
                print("No posts found in the database.")  # Debug: Log if no posts exist
                return None
        except Exception as e:
            print(f"Error retrieving most recent post ID: {e}")  # Debug: Log any errors
            return None

# Initialize the database
db = Database(DB_URL, DB_NAME)

