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
            err_msg = str(e)
            logger.critical(
                f"MongoDB connection failed: {err_msg}."
            )
            if "SSL handshake failed" in err_msg or "TLSV1_ALERT_INTERNAL_ERROR" in err_msg:
                logger.warning(
                    "⚠️ MongoDB connection failed due to SSL handshake / TLS alert. "
                    "This is almost always caused by MongoDB Atlas IP Whitelist (Network Access) restrictions. "
                    "Please log in to your MongoDB Atlas dashboard -> Network Access -> Add IP Address, "
                    "and add '0.0.0.0/0' (allow connection from anywhere, required for dynamic cloud hosts like Render) "
                    "or your current IP address to the whitelist to resolve this issue."
                )
            self.client = None
            self.db = None
            self.users_collection = None
            raise e

    def get_user_password(self, username: str) -> str:
        username = username.strip()
        if not self.is_connected or self.users_collection is None:
            raise RuntimeError("Database connection not established. Cannot fetch credentials.")
        try:
            user = self.users_collection.find_one({"username": username})
            if user:
                return user.get("password")
            return None
        except Exception as e:
            logger.error(f"Error fetching user from MongoDB: {e}")
            raise e

    def save_user(self, username: str, password: str) -> bool:
        username = username.strip()
        if not self.is_connected or self.users_collection is None:
            raise RuntimeError("Database connection not established. Cannot save credentials.")
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
            raise e

db_client = DatabaseClient()

