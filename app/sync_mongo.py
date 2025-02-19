from pymongo import MongoClient
from bson.objectid import ObjectId
from app.config import settings
import logging

logger = logging.getLogger("sync_mongo")
logger.setLevel(logging.INFO)

# Connect with PyMongo
mongo_uri = settings.mongo_uri
client = MongoClient(mongo_uri)

db_name = settings.mongo_db_name
sync_db = client[db_name]


def get_sync_conversation_by_id(conversation_id: str):
    try:
        oid = ObjectId(conversation_id)
    except:
        logger.error(f"Invalid conversation ID: {conversation_id}")
        return None

    doc = sync_db.conversations.find_one({"_id": oid})
    if doc:
        doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
    return doc


def update_sync_conversation_history(
    conversation_id: str, history: list, interrupted: bool = None
):
    """
    Update the conversation's history and optionally 'interrupted' field.
    """
    try:
        oid = ObjectId(conversation_id)
    except:
        logger.error(f"Invalid conversation ID: {conversation_id}")
        return None

    logger.info(f"Updating conversation {conversation_id} with history: {history}")

    update_doc = {"history": history}
    if interrupted is not None:
        update_doc["interrupted"] = interrupted

    result = sync_db.conversations.update_one({"_id": oid}, {"$set": update_doc})

    if result.modified_count == 1:
        logger.info(f"Successfully updated conversation {conversation_id}")
        return get_sync_conversation_by_id(conversation_id)

    logger.warning(f"Conversation {conversation_id} was not modified.")
    return None
