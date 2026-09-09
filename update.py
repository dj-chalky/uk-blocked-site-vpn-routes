"""Build a GL.iNet domain subscription from two public OSA lists (Python 3.10+)."""
import argparse
import csv
import io
import json
import re
import tempfile
import time
import ipaddress
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, urljoin, unquote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
SOURCES = {
    "osatracker": "https://osatracker.co.uk/api/export?format=txt&nsfw=true",
    "blocked-osa": "https://www.blocked.org.uk/osa-blocks",
    "blocked-court": "https://www.blocked.org.uk/legal-blocks/sites/gb/1?sort=url",
    "blocked-historical": "https://api.blocked.org.uk/data/export.csv.gz",
}
LABEL = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\Z")


def domain(value):
    value = value.strip()
    host = urlsplit(value).hostname if "://" in value else value
    if not host:
        raise ValueError(f"Missing hostname: {value!r}")
    try:
        return str(ipaddress.ip_address(host))
    except ValueError:
        pass
    host = host.rstrip(".").encode("idna").decode("ascii").lower()
    # Include bare domain and www traffic, without expanding hosted subdomains.
    while host.startswith("www."):
        host = host[4:]
    parts = host.split(".")
    if len(host) > 253 or len(parts) < 2 or not all(LABEL.fullmatch(p) for p in parts) or parts[-1].isdigit():
        raise ValueError(f"Invalid domain: {value!r}")
    return host


class SiteHeadings(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_heading = False
        self.urls = []

    def handle_starttag(self, tag, attrs):
        if tag == "h3":
            self.in_heading = True
        if tag == "a" and self.in_heading:
            href = dict(attrs).get("href", "")
            if href.startswith(("http://", "https://")):
                self.urls.append(href)

    def handle_endtag(self, tag):
        if tag == "h3":
            self.in_heading = False


def parse_sources(tracker, blocked):
    tracker_domains = {domain(line) for line in tracker.splitlines() if line.strip()}
    parser = SiteHeadings()
    parser.feed(blocked)
    blocked_domains = {domain(url) for url in parser.urls}
    # Stop instead of replacing the list with an error page or broken extraction.
    if len(tracker_domains) < 10 or len(blocked_domains) < 10:
        raise ValueError("Unexpectedly few domains: check source format before publishing.")
    return {"osatracker": tracker_domains, "blocked-osa": blocked_domains}


def fetch(url):
    req = Request(url, headers={"User-Agent": "OSA-VPN-List/1.0 (public domain-list aggregator)"})
    with urlopen(req, timeout=45) as response:
        data = response.read(5_000_001)
    if len(data) > 5_000_000:
        raise ValueError("Source exceeds expected size")
    return data.decode("utf-8-sig")


class CourtPage(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []
        self.last = None

    def handle_starttag(self, tag, attrs):
        if tag != "a":
            return
        attrs = dict(attrs)
        href = attrs.get("href", "")
        if href.startswith("/site/"):
            self.urls.append(unquote(href[len("/site/"):]))
        if attrs.get("aria-label") == "Last":
            self.last = href


def fetch_courts():
    first = fetch(SOURCES["blocked-court"])
    page = CourtPage()
    page.feed(first)
    if not page.last:
        raise ValueError("Court pagination missing")
    last_page = int(urlsplit(page.last).path.rstrip("/").split("/")[-1])
    if not 1 <= last_page <= 200:
        raise ValueError("Unexpected court page count")
    urls = set(page.urls)
    fingerprints = {tuple(sorted(page.urls))}
    for number in range(2, last_page + 1):
        time.sleep(0.5)
        current = CourtPage()
        current.feed(fetch(f"https://www.blocked.org.uk/legal-blocks/sites/gb/{number}?sort=url"))
        if not current.urls:
            raise ValueError(f"Empty court page {number}")
        fingerprint = tuple(sorted(current.urls))
        if fingerprint in fingerprints:
            raise ValueError(f"Repeated court page {number}: pagination may be broken")
        fingerprints.add(fingerprint)
        urls.update(current.urls)
        if number % 10 == 0:
            print(f"Court pages: {number}/{last_page}", flush=True)
    if len(urls) < 100:
        raise ValueError("Unexpectedly few court URLs")
    return {domain(value) for value in urls}


def build(source_sets, allow_large_change=False):
    domains = sorted(set.union(*source_sets.values()))
    meta_path = ROOT / "metadata.json"
    if meta_path.exists() and not allow_large_change:
        old_counts = json.loads(meta_path.read_text(encoding="utf-8")).get("source_counts", {})
        for name, old_count in old_counts.items():
            if name not in source_sets or len(source_sets[name]) < old_count * 0.8:
                raise ValueError(f"Source {name} lost over 20% of entries; review required")
    target = ROOT / "domains.txt"
    if target.exists():
        previous = set(target.read_text(encoding="utf-8").splitlines())
        removed = previous - set(domains)
        if previous and len(removed) / len(previous) > 0.20 and not allow_large_change:
            raise ValueError("Over 20% of previous domains disappeared; manual review required.")
    provenance = io.StringIO(newline="")
    writer = csv.writer(provenance, lineterminator="\n")
    writer.writerow(["domain", "sources"])
    for host in domains:
        writer.writerow([host, ";".join(name for name, items in source_sets.items() if host in items)])
    metadata = {
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "OSA Tracker including NSFW; Blocked.org.uk OSA and public court pages; blocked-status entries from the historical ORG export. Not a complete current ISP-block database.",
        "domain_count": len(domains),
        "source_counts": {name: len(items) for name, items in source_sets.items()},
        "sources": SOURCES,
        "normalization": "Lowercase IDNA; remove URL paths and leading www.; preserve other subdomains; deduplicate.",
        "blocked_data_license": "CC BY 4.0 — Open Rights Group, https://www.blocked.org.uk/licence",
        "historical_source_last_modified": "2020-01-17T00:34:14Z",
    }
    outputs = {
        "domains.txt": "\n".join(domains) + "\n",
        "provenance.csv": provenance.getvalue(),
        "metadata.json": json.dumps(metadata, indent=2) + "\n",
        "osa-domains.txt": "\n".join(sorted(source_sets["osatracker"] | source_sets["blocked-osa"])) + "\n",
    }
    if "blocked-court" in source_sets:
        outputs["court-domains.txt"] = "\n".join(sorted(source_sets["blocked-court"])) + "\n"
        outputs["live-sources-domains.txt"] = "\n".join(sorted(set.union(*(items for name, items in source_sets.items() if name != "blocked-historical")))) + "\n"
    # Validate all sources before writing; each replacement is atomic.
    for name, content in outputs.items():
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="\n", dir=ROOT, delete=False) as tmp:
            tmp.write(content)
            temp_path = Path(tmp.name)
        temp_path.replace(ROOT / name)
    print(json.dumps({"domains": len(domains), "source_counts": metadata["source_counts"]}))


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--tracker-file", type=Path)
    cli.add_argument("--blocked-file", type=Path)
    cli.add_argument("--allow-large-change", action="store_true")
    cli.add_argument("--court-file", type=Path)
    cli.add_argument("--skip-courts", action="store_true", help="Only for initial OSA-only validation")
    args = cli.parse_args()
    tracker = args.tracker_file.read_text(encoding="utf-8-sig") if args.tracker_file else fetch(SOURCES["osatracker"])
    blocked = args.blocked_file.read_text(encoding="utf-8-sig") if args.blocked_file else fetch(SOURCES["blocked-osa"])
    source_sets = parse_sources(tracker, blocked)
    if not args.skip_courts:
        source_sets["blocked-court"] = {domain(line) for line in args.court_file.read_text().splitlines()} if args.court_file else fetch_courts()
    history_file = ROOT / "data" / "historical-blocked.txt"
    if history_file.exists():
        source_sets["blocked-historical"] = {domain(line) for line in history_file.read_text(encoding="utf-8").splitlines()}
    build(source_sets, args.allow_large_change)
