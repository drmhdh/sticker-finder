"""The sqlite model for a chat."""
from stickerfinder.db import base

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    func,
    BigInteger,
    String,
    Table,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from stickerfinder.helper.telegram import call_tg_func
from stickerfinder.helper.tag_mode import TagMode
from stickerfinder.helper.keyboard import get_continue_tagging_keyboard


chat_sticker_set = Table(
    'chat_sticker_set', base.metadata,
    Column('chat_id',
           BigInteger,
           ForeignKey('chat.id', ondelete='CASCADE',
                      onupdate='CASCADE', deferrable=True),
           index=True),
    Column('sticker_set_name',
           String(),
           ForeignKey('sticker_set.name', ondelete='CASCADE',
                      onupdate='CASCADE', deferrable=True),
           index=True),
    UniqueConstraint('chat_id', 'sticker_set_name'),
)


class Chat(base):
    """The model for a chat."""

    __tablename__ = 'chat'

    id = Column(BigInteger, primary_key=True)
    type = Column(String)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Maintenance and chat flags
    is_newsfeed = Column(Boolean, default=False, nullable=False)
    is_maintenance = Column(Boolean, default=False, nullable=False)

    # Tagging process related flags and data
    tag_mode = Column(String)
    last_sticker_message_id = Column(BigInteger)

    # ForeignKeys
    current_task_id = Column(UUID(as_uuid=True), ForeignKey('task.id', ondelete='cascade'), index=True)
    current_sticker_file_id = Column(String, ForeignKey('sticker.file_id'), index=True)

    # Relationships
    current_task = relationship("Task", foreign_keys='Chat.current_task_id')
    current_sticker = relationship("Sticker")

    tasks = relationship("Task", foreign_keys='Task.chat_id')
    sticker_sets = relationship(
        "StickerSet",
        secondary=chat_sticker_set,
        back_populates="chats")

    def __init__(self, chat_id, chat_type):
        """Create a new chat."""
        self.id = chat_id
        self.type = chat_type

    @staticmethod
    def get_or_create(session, chat_id, chat_type):
        """Get or create a new chat."""
        chat = session.query(Chat).get(chat_id)
        if not chat:
            chat = Chat(chat_id, chat_type)
            session.add(chat)
            try:
                session.commit()
            # Handle parallel chat creation
            except IntegrityError as e:
                session.rollback()
                chat = session.query(Chat).get(chat_id)
                if chat is None:
                    raise e

        return chat

    def cancel(self, bot):
        """Cancel all interactions."""
        self.cancel_tagging(bot)

        self.current_task = None
        self.current_sticker_set = None

    def cancel_tagging(self, bot):
        """Cancel the tagging process."""
        if self.tag_mode == TagMode.STICKER_SET:
            keyboard = get_continue_tagging_keyboard(self.current_sticker.file_id)
            call_tg_func(bot, 'edit_message_reply_markup',
                         [self.id, self.last_sticker_message_id],
                         {'reply_markup': keyboard})

        self.tag_mode = None
        self.last_sticker_message_id = None
