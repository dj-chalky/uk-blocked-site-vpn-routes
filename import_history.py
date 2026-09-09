"""Extract blocked results from ORG's historical compressed CSV export."""
import argparse
import csv
import gzip
import hashlib
import json
from collections import Counter
from pathlib import Path
from update import ROOT, domain


def extract(path):
    domains = set()
    rejected = set()
    statuses = Counter()
    categories = Counter()
    newest = ""
    with gzip.open(path, "rt", encoding="utf-8-sig", newline="") as stream:
        first = next(stream)
        if "Latest results per URL/Network" not in first:
            raise ValueError("Unexpected export preamble")
        reader = csv.DictReader(stream)
        if not {"URL", "Status", "Result Timestamp", "Block Type"}.issubset(reader.fieldnames):
            raise ValueError("Unexpected export columns")
        for number, row in enumerate(reader, 1):
            statuses[row["Status"]] += 1
            if row["Status"].lower() == "blocked":
                categories[row["Block Type"] or "unspecified"] += 1
                newest = max(newest, row["Result Timestamp"])
                try:
                    domains.add(domain(row["URL"]))
                except (ValueError, UnicodeError) as error:
                    rejected.add((row["URL"], str(error)))
            if number % 2_000_000 == 0:
                print(f"Historical rows read: {number:,}; unique blocked targets: {len(domains):,}", flush=True)
    if len(domains) < 1000:
        raise ValueError("Historical extraction unexpectedly small")
    # gzip CRC/end-of-file validation completes before any output is written.
    data_dir = ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "historical-blocked.txt").write_text("\n".join(sorted(domains)) + "\n", encoding="utf-8")
    with path.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    metadata = {
        "source": "https://api.blocked.org.uk/data/export.csv.gz",
        "source_last_modified": "2020-01-17T00:34:14Z",
        "sha256": digest,
        "rows": sum(statuses.values()),
        "statuses": dict(statuses),
        "blocked_rows_by_type": dict(categories),
        "newest_blocked_result": newest,
        "unique_targets": len(domains),
        "rejected_urls": len(rejected),
        "coverage": "Only rows whose Status is blocked, across all recorded block types and UK networks in the historical export. Not a current ISP block list or a complete database export.",
    }
    (data_dir / "historical-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    with (data_dir / "historical-rejected.csv").open("w", encoding="utf-8", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(["url", "reason"])
        writer.writerows(sorted(rejected))
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("export", type=Path)
    extract(parser.parse_args().export)
