"""Stream type classes for tap-brillium."""

from pathlib import Path

from tap_brillium.client import SCHEMAS_DIR, BrilliumStream

class AccountsStream(BrilliumStream):
    """Define custom stream."""
    name = "Accounts"
    path = "/Accounts"
    primary_keys = ["Id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "Accounts.json"
