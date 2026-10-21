"""Back up a trusted local SQLite database without overwriting an existing file."""
import argparse
from contextlib import closing
import hashlib
from pathlib import Path
import sqlite3


def backup(source, destination):
    source, destination = Path(source).resolve(strict=True), Path(destination).resolve()
    if destination.exists() or source == destination:
        raise ValueError("Tujuan harus file baru; database/backup yang ada tidak ditimpa.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation prevents an accidental overwrite between check and open.
    with destination.open("xb"):
        pass
    try:
        with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as src:
            with closing(sqlite3.connect(destination)) as dst:
                src.backup(dst)
                if dst.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise ValueError("Integritas backup gagal.")
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    return hashlib.sha256(destination.read_bytes()).hexdigest()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print("sha256:", backup(args.database, args.output))
