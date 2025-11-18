from __future__ import annotations
from configparser import ConfigParser


class KeysBook:
    private_view_key: str = ''
    public_view_key: str = ''
    private_spend_key: str = ''
    public_spend_key: str = ''
    invalid_private_view_key: str = ''
    invalid_public_view_key: str = ''
    invalid_private_spend_key: str = ''
    invalid_public_spend_key: str = ''

    @classmethod
    def parse(cls, parser: ConfigParser) -> KeysBook:
        if not parser.has_section('keys'):
            raise Exception("Section [keys] not found")
        book = cls()
        book.private_view_key = parser.get('keys', 'private_view_key')
        book.public_view_key = parser.get('keys', 'public_view_key')
        book.private_spend_key = parser.get('keys', 'private_spend_key')
        book.public_spend_key = parser.get('keys', 'public_spend_key')
        book.invalid_private_view_key = parser.get('keys', 'invalid_private_view_key')
        book.invalid_public_view_key = parser.get('keys', 'invalid_public_view_key')
        book.invalid_private_spend_key = parser.get('keys', 'invalid_private_spend_key')
        book.invalid_public_spend_key = parser.get('keys', 'invalid_public_spend_key')
        return book
