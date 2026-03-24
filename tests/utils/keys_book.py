from __future__ import annotations
from configparser import ConfigParser


class KeysBook:
    """Test wallet keys book loaded from test configuration."""

    private_view_key: str = ''
    """Test wallet private view key."""
    public_view_key: str = ''
    """Test wallet public view key."""
    private_spend_key: str = ''
    """Test wallet private spend key."""
    public_spend_key: str = ''
    """Test wallet public spend key."""
    invalid_private_view_key: str = ''
    """An invalid private view key."""
    invalid_public_view_key: str = ''
    """An invalid public view key."""
    invalid_private_spend_key: str = ''
    """An invalid private spend key."""
    invalid_public_spend_key: str = ''
    """An invalid public spend key."""
    seed: str = ''
    """Test wallet seed."""

    @classmethod
    def parse(cls, parser: ConfigParser) -> KeysBook:
        """
        Parse test wallet keys book configuration.

        :param ConfigParser parser: configuration parser.
        :returns KeysBook: test wallet keys book configuration.
        """
        # check for keys section
        if not parser.has_section('keys'):
            raise Exception("Section [keys] not found")
        # load configuration
        book = cls()
        book.private_view_key = parser.get('keys', 'private_view_key')
        book.public_view_key = parser.get('keys', 'public_view_key')
        book.private_spend_key = parser.get('keys', 'private_spend_key')
        book.public_spend_key = parser.get('keys', 'public_spend_key')
        book.invalid_private_view_key = parser.get('keys', 'invalid_private_view_key')
        book.invalid_public_view_key = parser.get('keys', 'invalid_public_view_key')
        book.invalid_private_spend_key = parser.get('keys', 'invalid_private_spend_key')
        book.invalid_public_spend_key = parser.get('keys', 'invalid_public_spend_key')
        book.seed = parser.get('keys', 'seed')
        return book
