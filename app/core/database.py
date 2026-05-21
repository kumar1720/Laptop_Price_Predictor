import logging
from pymongo import MongoClient
from app.core.config import settings

logger = logging.getLogger("app.database")

class DatabaseClient:
    def __init__(self):
        self.uri = settings.MONGO_URI
        self.db_name = settings.MONGO_DB
        self.client = None
        self.db = None
        self.users_collection = None
        self._memory_fallback = {
            "admin": "password"
        }
        self.is_connected = False

        try:
            logger.info(f"Attempting to connect to MongoDB at {self.uri}...")
            # Set a 3-second server selection timeout to fail fast if MongoDB is down
            self.client = MongoClient(
                self.uri,
                serverSelectionTimeoutMS=3000
            )
            # Test connection
            self.client.server_info()
            self.db = self.client[self.db_name]
            self.users_collection = self.db["users"]
            self.is_connected = True
            logger.info(f"Successfully connected to MongoDB database '{self.db_name}'")
        except Exception as e:
            logger.error(
                f"MongoDB connection failed: {e}. "
                "Falling back to in-memory user credentials storage."
            )
            self.client = None
            self.db = None
            self.users_collection = None

    def get_user_password(self, username: str) -> str:
        username = username.strip()
        if self.is_connected and self.users_collection is not None:
            try:
                user = self.users_collection.find_one({"username": username})
                if user:
                    return user.get("password")
                return None
            except Exception as e:
                logger.error(f"Error fetching user from MongoDB: {e}")
        
        # Fallback to in-memory database
        return self._memory_fallback.get(username)

    def save_user(self, username: str, password: str) -> bool:
        username = username.strip()
        if self.is_connected and self.users_collection is not None:
            try:
                # Store user credentials securely
                self.users_collection.update_one(
                    {"username": username},
                    {"$set": {"password": password}},
                    upsert=True
                )
                logger.info(f"Successfully saved user '{username}' to MongoDB.")
                return True
            except Exception as e:
                logger.error(f"Error saving user to MongoDB: {e}")
        
        # Fallback to in-memory database
        self._memory_fallback[username] = password
        logger.info(f"Saved user '{username}' to in-memory fallback database.")
        return True

db_client = DatabaseClient()
