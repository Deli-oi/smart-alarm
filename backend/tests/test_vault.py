import pytest
from cryptography.fernet import Fernet

from app.vault import Vault, VaultError


def test_roundtrip_and_ciphertext_hides_secret():
    v = Vault(Fernet.generate_key().decode())
    blob = v.seal({"refresh_token": "abc123"})
    assert "abc123" not in blob
    assert v.open(blob) == {"refresh_token": "abc123"}


def test_wrong_key_fails():
    blob = Vault(Fernet.generate_key().decode()).seal({"a": 1})
    with pytest.raises(VaultError):
        Vault(Fernet.generate_key().decode()).open(blob)


def test_missing_key_is_an_error():
    with pytest.raises(VaultError):
        Vault("")
