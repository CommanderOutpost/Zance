import time
from celery.utils.log import get_task_logger
from app.celery_app import celery_app
from app.sync_mongo import (
    get_sync_conversation_by_id,
    update_sync_conversation_history,
)

logger = get_task_logger(__name__)


@celery_app.task
def deliver_chunks_task(chat_id: str, chunks: list):
    """
    Celery task that delivers chunked messages according to scheduling_plan.
    Uses PyMongo for synchronous Mongo calls (no Motor).
    """
    logger.warning(f"Scheduling plan chunks: {chunks}")

    for chunk_info in chunks:
        delay_seconds = chunk_info.get("delay_seconds", 0)
        chunk_content = chunk_info.get("content", "")

        logger.info(
            f"Sleeping for {delay_seconds} seconds before sending next chunk..."
        )
        time.sleep(delay_seconds)

        # Fetch latest conversation
        conversation_doc = get_sync_conversation_by_id(chat_id)
        if not conversation_doc:
            logger.error("Conversation not found. Stopping chunk delivery.")
            break
        if conversation_doc.get("interrupted", False):
            logger.warning("Conversation was interrupted. Stopping chunk delivery.")
            break

        # Update conversation history
        conversation_history = conversation_doc.get("history", [])
        conversation_history.append({"role": "assistant", "content": chunk_content})
        logger.info(f"Appending chunk: {chunk_content} to conversation {chat_id}")

        update_result = update_sync_conversation_history(chat_id, conversation_history)

        if not update_result:
            logger.error(
                f"Failed to update conversation {chat_id}. Stopping chunk delivery."
            )
            break

    logger.info(f"Chunk delivery completed for {chat_id}")
