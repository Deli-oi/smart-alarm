"""Recent inbox subjects over IMAP with a Google app password. No OAuth, read-only."""

import asyncio
import email
import email.utils
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


class GmailSentAdapter:
    """Evidence for the 10:30pm check: mail you sent since the given time counts as done work."""

    name = "gmail"

    def __init__(self, user: str, password: str, imap_cls=imaplib.IMAP4_SSL):
        self.user, self.password, self.imap_cls = user, password, imap_cls

    def _sent(self, since_iso: str):
        from datetime import datetime

        from .base import SourceRecord

        since = datetime.fromisoformat(since_iso.replace("Z", "+00:00"))
        m = self.imap_cls("imap.gmail.com")
        try:
            m.login(self.user, self.password)
            m.select('"[Gmail]/Sent Mail"', readonly=True)
            _, data = m.search(None, "SINCE", since.strftime("%d-%b-%Y"))
            out = []
            for i in data[0].split():
                _, parts = m.fetch(i, "(BODY.PEEK[HEADER.FIELDS (SUBJECT DATE MESSAGE-ID)])")
                msg = email.message_from_bytes(parts[0][1])
                when = email.utils.parsedate_to_datetime(msg["Date"]) if msg["Date"] else since
                if when.astimezone(since.tzinfo) < since:
                    continue
                out.append(
                    SourceRecord(
                        source="gmail",
                        external_id=(msg["Message-ID"] or i.decode()).strip(),
                        when=when.isoformat(),
                        text=_decode(msg["Subject"]),
                    )
                )
            return out
        finally:
            try:
                m.logout()
            except Exception:
                pass

    async def fetch_since(self, since_iso: str):
        return await asyncio.to_thread(self._sent, since_iso)
