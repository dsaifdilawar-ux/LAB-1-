# Lab 01 – SQLite Ledgers and Conflicting Copies
**Course:** Introduction to Blockchain | **Platform:** Ubuntu/Debian Linux | **Type:** Educational / simulated

## 1. Aim
Show that a normal database (SQLite) keeps one authoritative ledger, and that simply making copies does **not** solve the "who is correct?" problem. Copies are **not** a blockchain.

## 2. Setup (Linux)
```bash
sudo apt update && sudo apt install -y python3 sqlite3   # python3 + optional sqlite3 CLI
mkdir -p ~/Week_01 && cd ~/Week_01                       # lab directory
# copy solution.py into this folder
python3 --version
```

## 3. Commands to run (in order)
```bash
python3 solution.py
ls -lh week01_ledger.sqlite week01_ledger.csv
cat week01_ledger.csv
python3 solution.py --database alternate.sqlite --export alternate.csv
```
Optional: inspect the database directly
```bash
sqlite3 week01_ledger.sqlite "SELECT * FROM events;"
```

## 4. Logic of the program (step by step)
| Step | Code | Why |
|---|---|---|
| 1 | `argparse` options `--database`, `--export` | lets the 2nd run use different file names so nothing is overwritten |
| 2 | `sqlite3.connect()` | opens/creates a real file-backed database |
| 3 | `DROP TABLE IF EXISTS` + `CREATE TABLE events(seq, event, approved_by)` | clean training table; `seq INTEGER PRIMARY KEY` gives an ordered sequence |
| 4 | `executemany INSERT` of 4 records | stores the approved events (4th = **required extension**, C-003) |
| 5 | `SELECT ... ORDER BY seq` | reads events back chronologically |
| 6 | `csv.writer` | exports the same rows to CSV (header `seq,event,approved_by`) |
| 7 | `registrar_copy`, `employer_copy` = `list(rows)` | two independent in-memory copies |
| 8 | change event 2 in employer copy to `C-999` | simulates a silent, unauthorised edit |
| 9 | compare copies with `zip` and `!=` | prints `CONFLICT DETECTED` |
| 10 | `assert len(rows)==4 and registrar_copy != employer_copy` | automatic check, then prints PASS |

**Key idea:** the data differs but nothing in the system says which copy is right. Someone with authority (policy) must decide.

## 5. Required extension – complete answer
A fourth approved event `('Issue certificate C-003','Registrar')` was added to `records`; `len(rows)==4` is asserted. The conflict **still remains** because adding rows or copies does not decide whose data is authoritative.

## 6. Conflict policy (Step 5)
- Only an authenticated registrar may issue or revoke certificates.
- Sequence numbers only increase; each event has a signed, unique ID.
- Corrections are new, attributable events – never silent overwrites.
- A documented authority resolves disputes.

## 7. Output (captured from actual run)
```
CENTRAL DATABASE (SQLite):
  (1, 'Issue certificate C-001', 'Registrar')
  (2, 'Issue certificate C-002', 'Registrar')
  (3, 'Revoke certificate C-001', 'Registrar')
  (4, 'Issue certificate C-003', 'Registrar')
SHARED-COPY EXPERIMENT (a fourth event does not resolve conflicts):
CONFLICT DETECTED: (2, 'Issue certificate C-002', 'Registrar') versus (2, 'Issue certificate C-999', 'Registrar')
Audit question: WHO is authorized to decide the correct record?
PASS: central ledger stored; independently modified copies disagree.
```
Full command transcript: see `transcript.txt`.

### Result table
| seq | Registrar copy | Employer copy | Status |
|---|---|---|---|
| 1 | Issue certificate C-001 | Issue certificate C-001 | match |
| 2 | Issue certificate C-002 | Issue certificate C-999 | **CONFLICT** |
| 3 | Revoke certificate C-001 | Revoke certificate C-001 | match |
| 4 | Issue certificate C-003 | Issue certificate C-003 | match |

### Diagram
```
 SQLite file (central ledger, 4 rows)
        |
   ------------------
   |                |
Registrar copy   Employer copy (event 2 edited -> C-999)
   |                |
   +---- compare ---+--> CONFLICT: who decides?
```

## 8. Viva answers
**Q1. Who can correct the record?** The organisation designated as authoritative by a documented policy, through authenticated and audited corrections.

**Q2. Do multiple copies make a blockchain?** No. Replication alone lacks consensus rules, cryptographic ordering and independent validation.

**Q3. When prefer a registrar database?** When one trusted authority issues records; a conventional transactional database with audit trails is simpler and cheaper.

## 9. Safety / common mistakes
- The script **drops the `events` table** – never point `--database` at a file with important data.
- Run from the lab directory; use a new filename for the second run.
- CSV line endings (`\r\n`) are normal for Python's csv module.
- Note: the supplied source had a typo `C001` in event 3; fixed to `C-001` to match the expected output.

## 10. Marking checklist (20)
Linux setup 3 · correct execution 5 · extension 5 · explanation 5 · clear/safe submission 2
