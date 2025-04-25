import uuid
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import time
import json
import psycopg
from psycopg.rows import dict_row

from ..utils import log

logger = log.get_logger(__name__)

class PostgresChatClient:
    def __init__(
        self,
        hostname: str,
        db: str,
        username: str,
        port: int = 5432,
        password: str = None,
    ):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.db = db
        self.conn = None
        self._is_query_service_ready = False
        self._tables_created = False

    def connect(self) -> None:
        """Establish connection to PostgreSQL database."""
        try:
            self.conn = psycopg.connect(
                host=self.hostname,
                port=self.port,
                user=self.username,
                password=self.password,
                dbname=self.db,
                autocommit=True
            )

            try:
                self.init()
            except Exception as init_err:
                logger.warning(f"Tables not ready yet: {str(init_err)}")

            logger.info("Connected to PostgreSQL database")
        except Exception as conn_err:
            logger.warning(f"Database connection failed: {str(conn_err)}")
            raise

    def init(self) -> None:
        """Create the tables if they don't exist."""
        if not self.conn:
            self.connect()

        if self._tables_created:
            return

        try:
            with self.conn.cursor() as cursor:
                # Create schema if it doesn't exist
                cursor.execute(f"""
                CREATE SCHEMA IF NOT EXISTS {self.db}
                """)

                # Create chats table
                cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.db}.chats (
                    id VARCHAR(36) PRIMARY KEY,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    metadata JSONB NOT NULL DEFAULT '{{}}'
                )
                """)

                # Create messages table
                cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.db}.messages (
                    id BIGINT,
                    chat_id VARCHAR(36) REFERENCES {self.db}.chats(id) ON DELETE CASCADE,
                    role VARCHAR(50) NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    metadata JSONB NOT NULL DEFAULT '{{}}',
                    PRIMARY KEY (chat_id, id)
                )
                """)

                # Create index on chat_id for faster lookups
                cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_messages_chat_id
                ON {self.db}.messages(chat_id)
                """)

                # Create index on created_at for sorting
                cursor.execute(f"""
                CREATE INDEX IF NOT EXISTS idx_messages_created_at
                ON {self.db}.messages(created_at)
                """)

                self._tables_created = True
                logger.info("Database tables initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing tables: {str(e)}")
            raise

    def await_up(self, max_retries: int = 30, initial_delay: float = 1.0, max_delay: float = 10.0) -> None:
        """
        Wait until the PostgreSQL database is available by running a simple query in a loop.

        Args:
            max_retries: Maximum number of retry attempts.
            initial_delay: Initial delay between retries in seconds.
            max_delay: Maximum delay between retries in seconds.
        """
        # If we already know the service is ready, skip the check
        if self._is_query_service_ready:
            return

        if not self.conn:
            self.connect()

        delay = initial_delay
        for attempt in range(1, max_retries + 1):
            try:
                with self.conn.cursor() as cursor:
                    # Try a simple query
                    cursor.execute("SELECT 1")
                    cursor.fetchone()

                # If we got here, the database is ready
                self._is_query_service_ready = True
                logger.info("PostgreSQL database is ready")
                return
            except Exception as e:
                logger.warning(
                    f"Attempt {attempt}/{max_retries}: PostgreSQL database not available yet. "
                    f"Retrying in {delay:.1f} seconds... Error: {str(e)}"
                )
                time.sleep(delay)
                # Exponential backoff with a cap
                delay = min(max_delay, delay * 1.5)

                # Try to reconnect
                try:
                    if self.conn.closed:
                        self.connect()
                except Exception:
                    pass

        # If we've exhausted all retries
        raise Exception(f"PostgreSQL database not available after {max_retries} attempts")

    def create_chat(self, metadata: Dict[str, Any] = None) -> str:
        """
        Create a new chat session.

        Args:
            metadata: Optional metadata for the chat session

        Returns:
            The UUID of the created chat session
        """
        if not self.conn or self.conn.closed:
            self.connect()

        self.init()  # Ensure tables exist

        chat_id = str(uuid.uuid4())
        now = datetime.utcnow()

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(
                    f"""
                    INSERT INTO {self.db}.chats
                    (id, created_at, updated_at, metadata)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (
                        chat_id,
                        now,
                        now,
                        json.dumps(metadata or {})
                    )
                )

            logger.info(f"Created chat session with ID: {chat_id}")
            return chat_id
        except Exception:
            logger.exception("Failed to create chat")
            raise

    def add_message(
        self,
        chat_id: str,
        role: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> Tuple[int, str]:
        """
        Add a message to an existing chat session.

        Args:
            chat_id: The UUID of the chat session
            role: The role of the message sender (e.g., 'user', 'assistant')
            content: The content of the message
            metadata: Optional metadata for the message

        Returns:
            The ID of the added message
        """
        if not self.conn or self.conn.closed:
            self.connect()

        self.init()  # Ensure tables exist

        try:
            chat = self.get_chat(chat_id)
            now = datetime.utcnow()
            if not chat:
                raise ValueError(f"Chat with ID {chat_id} not found")

            # Update chat's timestamp
            with self.conn.cursor() as cursor:
                cursor.execute(
                    f"""
                    UPDATE {self.db}.chats
                    SET updated_at = %s
                    WHERE id = %s
                    """,
                    (now, chat_id)
                )

            # NOTE: Message ID is just a timestamp, for sortability
            message_id = int(now.timestamp() * 1000)

            with self.conn.cursor() as cursor:
                cursor.execute(
                    f"""
                    INSERT INTO {self.db}.messages
                    (id, chat_id, role, content, created_at, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        message_id,
                        chat_id,
                        role,
                        content,
                        now,
                        json.dumps(metadata or {})
                    )
                )

            logger.info(f"Added message with ID {message_id} to chat {chat_id}")
            return message_id, now.isoformat()
        except Exception:
            logger.exception("Failed to add message.")
            raise

    def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a chat session by ID.

        Args:
            chat_id: The UUID of the chat session

        Returns:
            The chat session details or None if not found
        """
        if not self.conn or self.conn.closed:
            self.connect()

        self.init()  # Ensure tables exist

        try:
            with self.conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    f"""
                    SELECT id, created_at, updated_at, metadata
                    FROM {self.db}.chats
                    WHERE id = %s
                    """,
                    (chat_id,)
                )

                result = cursor.fetchone()

                if not result:
                    return None

                # Convert to the same format as Postgres
                chat_data = dict(result)

                # Convert datetime objects to isoformat strings
                for field in ['created_at', 'updated_at']:
                    if isinstance(chat_data[field], datetime):
                        chat_data[field] = chat_data[field].isoformat()

                # Parse metadata JSON if it's a string
                if isinstance(chat_data['metadata'], str):
                    chat_data['metadata'] = json.loads(chat_data['metadata'])

                return chat_data
        except Exception as e:
            logger.warning(f"Failed to get chat: {str(e)}")
            return None

    def get_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        """
        Get all messages for a chat session.

        Args:
            chat_id: The UUID of the chat session

        Returns:
            List of messages in the chat session
        """
        if not self.conn or self.conn.closed:
            self.connect()

        self.init()  # Ensure tables exist

        # Make sure the database is available
        self.await_up()

        try:
            with self.conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(
                    f"""
                    SELECT id, chat_id, role, content, created_at, metadata
                    FROM {self.db}.messages
                    WHERE chat_id = %s
                    ORDER BY created_at ASC
                    """,
                    (chat_id,)
                )

                messages = []
                for row in cursor.fetchall():
                    message = dict(row)

                    # Convert datetime objects to isoformat strings
                    if isinstance(message['created_at'], datetime):
                        message['created_at'] = message['created_at'].isoformat()

                    # Parse metadata JSON if it's a string
                    if isinstance(message['metadata'], str):
                        message['metadata'] = json.loads(message['metadata'])

                    messages.append(message)

                return messages
        except Exception:
            logger.exception("Failed to get messages.")
            raise

    def delete_chat(self, chat_id: str) -> bool:
        """
        Delete a chat session and all its messages.

        Args:
            chat_id: The UUID of the chat session

        Returns:
            True if the chat was deleted, False otherwise
        """
        if not self.conn or self.conn.closed:
            self.connect()

        self.init()  # Ensure tables exist

        # Make sure the database is available
        self.await_up()

        try:
            chat = self.get_chat(chat_id)
            if not chat:
                return False

            with self.conn.cursor() as cursor:
                # The messages will be deleted automatically due to CASCADE constraint
                cursor.execute(
                    f"""
                    DELETE FROM {self.db}.chats
                    WHERE id = %s
                    """,
                    (chat_id,)
                )

                rows_deleted = cursor.rowcount

            if rows_deleted > 0:
                logger.info(f"Deleted chat {chat_id} and its messages")
                return True
            return False
        except Exception:
            logger.error("Failed to delete chat.")
            raise

    def close(self) -> None:
        """Close the database connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()
            logger.info("Database connection closed")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
