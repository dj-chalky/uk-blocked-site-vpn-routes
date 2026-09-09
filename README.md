# UK VPN routing domain subscription

A combined plain-text domain list in GL.iNet's documented subscription format, from:

- OSA Tracker: https://osatracker.co.uk/api/export?format=txt&nsfw=true (includes adult domains)
- Open Rights Group / Blocked.org.uk: https://www.blocked.org.uk/osa-blocks
- Blocked.org.uk court-order reports: https://www.blocked.org.uk/legal-blocks/sites
- Blocked.org.uk historical UK ISP results export: https://api.blocked.org.uk/data/export.csv.gz

## Coverage

`domains.txt` combines every extracted target from the two OSA sources, all pages of the public UK court-block listing, and all valid targets with a `blocked` result in the downloadable historical export. All recorded historical block types are included. It is NOT the complete current Blocked.org.uk ISP-filter database. The site's headline blocked-site count is a statistic, not this feed's expected entry count.

**The historical export was last modified on 17 January 2020.** Those entries are retained as historical coverage; they may now be unblocked, inactive or owned by someone else. The updater refreshes the OSA sources and court pages, but does not turn historical ISP records into current observations. The publicly downloadable export also excludes some source datasets in its upstream export code.

Entries on the OSA page include shutdowns, relaunches and some non-OSA geoblocking reports; inclusion is not a claim that a site is currently blocked or that a VPN can restore a closed service. Court-page results also have varying check dates.

Domains are lowercased, deduplicated, and stripped of URL paths and a leading `www.`. Other subdomains are preserved. GL.iNet routes by domain, so a report about one forum or page can route other traffic to that same domain too. Related media/CDN domains are included only when present in the sources.

Available subscriptions:

| File | Coverage |
| --- | --- |
| `domains.txt` | Everything available in this build, including historical ISP results |
| `live-sources-domains.txt` | OSA sources and public court pages, excluding the historical export |
| `osa-domains.txt` | Both OSA sources only |
| `court-domains.txt` | Public UK court-block pages only |
| `data/historical-blocked.txt` | Blocked targets in the January 2020 export only |

`provenance.csv` records each target's sources. `metadata.json` records source counts and the last published build time. `data/historical-metadata.json` records the historical export hash, row counts and result dates. Invalid historical hostnames are listed in `data/historical-rejected.csv` instead of being silently inserted into the router feed. IP addresses, if present, are preserved in canonical form.

## Publish on GitHub

1. Create a public repository with `main` as its default branch.
2. Put the contents of this folder at its root, including `.github/workflows/update.yml`.
3. Enable Actions if prompted. Run **Update OSA VPN domains** once and confirm success.
4. Open `domains.txt`, choose **Raw**, and copy the resulting HTTPS URL.
5. In GL.iNet VPN routing, choose **Specified Domain / IP List → Subscription URL**, paste the Raw URL and Detect. Set **Use VPN** to your chosen tunnel and apply the rule.

The user's firmware is v4.9.0. This output format has been validated locally, but the full feed's size and import behaviour must be tested on the router; no claim is made that the device can accept an arbitrarily large list. The smaller subscriptions above are available at stable URLs if needed.

The workflow checks daily. The router's documented subscription refresh is daily, so publication and router refresh can occur at different times. GitHub can disable scheduled workflows in inactive public repositories; check Actions if updates stop. Failed downloads, invalid domains, suspiciously small sources or a loss of more than 20% of existing entries stop the update and preserve the published list. Review the cause before using `python update.py --allow-large-change` manually.

## Known router import issue

The user's GL.iNet screenshot rejected line 1 of the original OSA Tracker feed (`4chan.org`) while recognising the other 58 entries. The downloaded source had no byte-order mark or malformed first line. The cause is unconfirmed. This list retains valid numeric-leading domains; it does not silently remove them. Test Detect on the actual router before relying on it. If rejection persists, its line number identifies the entry in this file.

## Refresh locally

With Python 3.10 or later, run `python update.py`. No third-party packages are required. All live sources must succeed before generated files change.

The court collector follows the public pagination at a modest request rate and refuses empty or repeated pages. To rebuild the historical extraction, download the export and run `python import_history.py /path/to/export.csv.gz` (Python 3.11+). The large raw archive is not stored in this repository or downloaded on every scheduled run. If the upstream export changes, review its date and replace the historical extraction explicitly.

## Attribution

Blocked.org.uk data: Open Rights Group, licensed under Creative Commons Attribution 4.0 International unless otherwise specified: https://www.blocked.org.uk/licence . Changes: extraction of hostnames, normalization and merging.

OSA Tracker: https://osatracker.co.uk/ . Section 6 of its terms makes the published list and exports freely available for reuse: https://osatracker.co.uk/terms . No ownership or blanket license over that source's data is asserted here.

GL.iNet format documentation: https://docs.gl-inet.com/router/en/4/tutorials/how_to_configure_domain_and_ip_filtering_rules_for_glinet_routers_via_an_online_text_file/

GL.iNet subscription refresh documentation: https://docs.gl-inet.com/router/en/4/interface_guide/vpn_dashboard_v4.8/
