"""Encrypted storage for connector credentials (OAuth refresh tokens, app passwords).

Same idea as n8n and Nango: secrets are encrypted before they reach the database, with a key
that lives only in the host's environment. A database dump alone then reveals nothing.
Generate a key with: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
Losing the key means reconnecting every source, so back it up separately from the database.
"""

import json

from cryptography.fernet import Fernet, InvalidToken


class VaultError(Exception):
    pass


class Vault:
    def __init__(self, key: str):
        if not key:
            raise VaultError("TOKEN_ENC_KEY is not set")
        try:
            self._f = Fernet(key.encode())
        except ValueError as e:
            raise VaultError("TOKEN_ENC_KEY is not a valid Fernet key") from e

    def seal(self, secret: dict) -> str:
        return self._f.encrypt(json.dumps(secret).encode()).decode()

    def open(self, blob: str) -> dict:
        try:
            return json.loads(self._f.decrypt(blob.encode()))
        except InvalidToken as e:
            raise VaultError("wrong key or corrupted blob") from e
