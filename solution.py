#!/usr/bin/env python3
"""Week 01: inspect real SQLite records and disagreements between copies.

Logic overview
1. Create a real, file-backed SQLite database (the "central ledger").
2. Insert 4 approved events (the 4th, C-003, is the required extension).
3. Read them back in order and export them to CSV.
4. Make two in-memory copies (registrar / employer), tamper with one,
   and detect the disagreement.
5. Assert the expected outcome and print PASS.
"""
import argparse
import csv
import sqlite3

# ---- 1. Command-line options (so a second run can use different file names)
p = argparse.ArgumentParser()
p.add_argument('--database', default='week01_ledger.sqlite')
p.add_argument('--export', default='week01_ledger.csv')
args = p.parse_args()

# ---- 2. Create the database and table
con = sqlite3.connect(args.database)           # opens or creates the file
con.execute('DROP TABLE IF EXISTS events')     # training data ONLY; use a disposable DB name
con.execute('CREATE TABLE events ('
            'seq INTEGER PRIMARY KEY, '        # auto-increasing sequence number
            'event TEXT NOT NULL, '
            'approved_by TEXT NOT NULL)')

# ---- 3. Insert the four approved events (4th = required extension)
records = [
    ('Issue certificate C-001', 'Registrar'),
    ('Issue certificate C-002', 'Registrar'),
    ('Revoke certificate C-001', 'Registrar'),  # NOTE: hyphen fixed (PDF source had "C001")
    ('Issue certificate C-003', 'Registrar'),   # EXTENSION
]
con.executemany('INSERT INTO events(event, approved_by) VALUES(?, ?)', records)
con.commit()

# ---- 4. Read back in chronological order and export to CSV
rows = con.execute('SELECT seq, event, approved_by FROM events ORDER BY seq').fetchall()
with open(args.export, 'w', newline='', encoding='utf-8') as output:
    w = csv.writer(output)
    w.writerow(['seq', 'event', 'approved_by'])
    w.writerows(rows)

print('CENTRAL DATABASE (SQLite):')
for r in rows:
    print(' ', r)

# ---- 5. Shared-copy experiment: two copies, one silently modified
registrar_copy = list(rows)
employer_copy = list(rows)
employer_copy[1] = (employer_copy[1][0], 'Issue certificate C-999', employer_copy[1][2])

print('SHARED-COPY EXPERIMENT (a fourth event does not resolve conflicts):')
for a, b in zip(registrar_copy, employer_copy):
    if a != b:
        print('CONFLICT DETECTED:', a, 'versus', b)
print('Audit question: WHO is authorized to decide the correct record?')

# ---- 6. Verification
assert len(rows) == 4 and registrar_copy != employer_copy
print('PASS: central ledger stored; independently modified copies disagree.')
con.close()
