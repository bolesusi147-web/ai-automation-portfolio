"""Transactional CRM demonstration: untrusted AI output never controls routing."""
import hashlib
import json
import math
import re
import sqlite3


def validate_analysis(payload) -> dict:
    if isinstance(payload,str):
        try:
            payload = json.loads(payload)
        except (ValueError,TypeError) as error:
            raise ValueError('Malformed model JSON') from error
    if not isinstance(payload,dict) or set(payload)!={'status','summary','confidence','next_action'}:
        raise ValueError('Unexpected analysis fields')
    if payload['status'] not in ('new','quote_requested','follow_up','resolved'):
        raise ValueError('Unsupported status')
    if payload['next_action'] not in ('none','follow_up','review'):
        raise ValueError('Unsupported action')
    confidence = payload['confidence']
    if isinstance(confidence,bool) or not isinstance(confidence,(int,float)) or not 0<=confidence<=1 or not math.isfinite(confidence):
        raise ValueError('Confidence must be finite and between 0 and 1')
    if not isinstance(payload['summary'],str) or not payload['summary'].strip() or len(payload['summary'])>2000:
        raise ValueError('Invalid summary')
    return dict(payload,summary=payload['summary'].strip())


class EventStore:
    def __init__(self,path):
        self.db = sqlite3.connect(str(path))
        self.db.row_factory = sqlite3.Row
        with self.db:
            self.db.execute('CREATE TABLE IF NOT EXISTS customers (id TEXT PRIMARY KEY, status TEXT NOT NULL, summary TEXT NOT NULL)')
            self.db.execute('CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, outcome TEXT NOT NULL, reason TEXT NOT NULL, customer_id TEXT NOT NULL)')
            self.db.execute("INSERT OR IGNORE INTO customers VALUES ('DEMO-CUSTOMER','new','')")

    def __enter__(self):
        return self

    def __exit__(self,*args):
        self.db.close()

    def customer(self,customer_id):
        row = self.db.execute('SELECT * FROM customers WHERE id=?',(customer_id,)).fetchone()
        return dict(row) if row else None

    def event_count(self):
        return self.db.execute('SELECT COUNT(*) FROM events').fetchone()[0]

    def ingest(self,event_id,customer_id,model_output,approved=False):
        """Approval comes from the caller; it must never be accepted from model JSON.

        Identical event retry is a no-op. A human review should use a new event ID
        when submitting an approved version; there is no review UI in this demo.
        """
        if not isinstance(event_id,str) or not re.fullmatch(r'[A-Za-z0-9_-]{1,64}',event_id):
            raise ValueError('Invalid event identifier')
        if type(approved) is not bool:
            raise ValueError('Approval must be an explicit boolean')
        if not isinstance(customer_id,str) or not self.customer(customer_id):
            raise ValueError('Unknown customer')
        try:
            canonical = json.dumps([customer_id,model_output,approved],sort_keys=True,allow_nan=False)
        except (TypeError,ValueError) as error:
            raise ValueError('Input must be finite JSON data') from error
        fingerprint = hashlib.sha256(canonical.encode()).hexdigest()
        try:
            analysis = validate_analysis(model_output)
            review = not approved or analysis['confidence']<0.8 or analysis['next_action']=='review'
            reason = 'Human review required' if review else 'Validated and explicitly approved'
        except ValueError as error:
            analysis = None
            review = True
            reason = str(error)
        outcome = 'review' if review else 'applied'
        # Begin immediate makes duplicate checking and business/audit writes atomic.
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            existing = self.db.execute('SELECT fingerprint FROM events WHERE id=?',(event_id,)).fetchone()
            if existing:
                if existing['fingerprint']!=fingerprint:
                    raise ValueError('Event ID reused with different content')
                return dict(event_id=event_id,outcome='duplicate')
            if not review:
                self.db.execute('UPDATE customers SET status=?,summary=? WHERE id=?',
                                (analysis['status'],analysis['summary'],customer_id))
            self.db.execute('INSERT INTO events VALUES (?,?,?,?,?)',
                            (event_id,fingerprint,outcome,reason,customer_id))
        return dict(event_id=event_id,outcome=outcome,reason=reason)
