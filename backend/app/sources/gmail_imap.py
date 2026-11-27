"""Recent inbox subjects over IMAP with a Google app password. No OAuth, read-only."""

import asyncio
import email
import imaplib
from email.header import decode_header, make_header

from pydantic import BaseModel


class MailItem(BaseModel):
    sender: str
    subject: str


def _decode(v: str) -> str:
    return str(make_header(decode_header(v or "")))


def _fetch(user: str, password: str, limit: int, imap_cls=imaplib.IMAP4_SSL) -> list[MailItem]:
    m = imap_cls("imap.gmail.com")
    try:
        m.login(user, password)
        m.select("INBOX", readonly=True)
        _, data = m.search(None, "ALL")
        ids = data[0].split()[-limit:]
        items: list[MailItem] = []
        for i in reversed(ids):
            _, parts = m.fetch(i, "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")
            msg = email.message_from_bytes(parts[0][1])
            items.append(MailItem(sender=_decode(msg["From"]), subject=_decode(msg["Subject"])))
        return items
    finally:
        try:
            m.logout()
        except Exception:
            pass


async def recent_mail(user: str, password: str, limit: int = 8, imap_cls=imaplib.IMAP4_SSL) -> list[MailItem]:
    return await asyncio.to_thread(_fetch, user, password, limit, imap_cls)
