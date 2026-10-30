"""
check_output.py OLD_DB NEW_DB fails when any table that exists in both
lost more than 10% of its rows, so a broken scrape is never published
"""
import sqlite3
import sys

MAX_DROP = 0.10


def counts(path: str) -> dict[str, int]:
    db = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    tables = [r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
    return {t: db.execute(f'SELECT COUNT(*) FROM "{t}"').fetchone()[0] for t in tables}


def check(old: dict[str, int], new: dict[str, int]) -> list[str]:
    return [f"{t}: {old[t]} -> {new.get(t, 0)} rows"
            for t in old if new.get(t, 0) < old[t] * (1 - MAX_DROP)]


if __name__ == "__main__":
    assert check({"A": 100}, {"A": 95}) == []
    assert check({"A": 100}, {"A": 80}) == ["A: 100 -> 80 rows"]
    assert check({"A": 100}, {}) == ["A: 100 -> 0 rows"]
    assert check({}, {"NEW": 5}) == []

    old_counts, new_counts = counts(sys.argv[1]), counts(sys.argv[2])
    for table in sorted(new_counts):
        print(f"{table}: {old_counts.get(table, '-')} -> {new_counts[table]}")
    failures = check(old_counts, new_counts)
    if failures:
        sys.exit("Row counts dropped by more than 10%, not publishing:\n" + "\n".join(failures))
