"""This module contains the Conversations class and the Message class."""
class Message:
    """
    The Message class represents a single message in a conversation.

    Attributes:
        role (str): The role of the sender of the message.
        content (str): The content of the message.

    Examples:
        >>> message = Message(role="user", content="Hello!")
    """

    def __init__(self, role: str, content: str):
        """
        Initialize the Message class with a sender's role and message content.

        Args:
            role (str): The role of the sender of the message.
            content (str): The content of the message.
        """
        self.role: str = role
        self.content: str = content

    def to_dict(self) -> dict[str,str]:
        """
        Convert the message into a dictionary format.

        Returns:
            dict[str, str]: Dictionary with the 'role' and 'content' of the message.

        Examples:
            >>> message = Message(role="user", content="Hello!")
            >>> message.to_dict()
        """
        return {"role": self.role, "content": self.content}


class Conversations:
    """
    The Conversations class represents a collection of Message objects.

    Attributes:
        messages (list[Message]): A list of messages in the conversation.

    Examples:
        >>> conversations = Conversations()
        >>> conversations.add_message(role="user", content="Hello!")
        >>> conversations.add_message(role="assistant", content="Hi!")
        >>> conversations.get_messages()
        [Message(role='user', content='Hello!'), Message(role='assistant', content='Hi!')]

    """

    def __init__(self):
        """Initialize the Conversations class with an empty list of messages."""
        self.messages: list[Message] = []

    def add_message(self, role: str, content: str) -> None:
        """
        Add a new message to the conversation.

        Args:
            role (str): The role of the sender of the message.
            content (str): The content of the message.
        """
        message = Message(role=role, content=content)
        self.messages.append(message)

    def get_messages(self) -> list[Message]:
        """
        Return the list of Message objects in the conversation.

        Returns:
            list[Message]: A list of Message objects.
        """
        return self.messages

    def get_message_dict_list(self) -> list[dict[str,str]]:
        """
        Return a list of dictionary representation of all messages in the conversation.

        Returns:
            list[dict[str, str]]: A list of dictionaries, each representing a Message.
        """
        return [m.to_dict() for m in self.messages]

    def get_messages_by_role(self, role: str) -> list[Message]:
        """
        Return a list of all messages sent by a specific role.

        Args:
            role (str): The role of the sender of the messages.

        Returns:
            list[Message]: A list of Message objects sent by the specified role.

        Examples:
            >>> conversations = Conversations()
            >>> conversations.add_message(role="user", content="Hello!")
            >>> conversations.add_message(role="assistant", content="Hi!")
            >>> conversations.get_messages_by_role(role="user")
            [Message(role='user', content='Hello!')]
        """
        return [message for message in self.messages if message.role == role]
