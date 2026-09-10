# UK VPN routing domain subscription

A combined set of plain-text domain lists for policy-based VPN routing on GL.iNet routers. Data is aggregated from:

- OSA Tracker: https://osatracker.co.uk/api/export?format=txt&nsfw=true (includes adult domains)
- Open Rights Group / Blocked.org.uk: https://www.blocked.org.uk/osa-blocks
- Blocked.org.uk court-order reports: https://www.blocked.org.uk/legal-blocks/sites
- Blocked.org.uk historical UK ISP results export: https://api.blocked.org.uk/data/export.csv.gz

The latest comparison with alternative OSA sources is documented in [SOURCE_REVIEW.md](SOURCE_REVIEW.md).

## Coverage

`domains.txt` combines every extracted target from the two OSA sources, all pages of the public UK court-block listing, and all valid targets with a `blocked` result in the downloadable historical export. All recorded historical block types are included. It is NOT the complete current Blocked.org.uk ISP-filter database. The site's headline blocked-site count is a statistic, not this feed's expected entry count.

**The historical export was last modified on 17 January 2020.** Those entries are retained as historical coverage; they may now be unblocked, inactive or owned by someone else. The updater refreshes the OSA sources and court pages, but does not turn historical ISP records into current observations. The publicly downloadable export also excludes some source datasets in its upstream export code.

Entries on the OSA page include shutdowns, relaunches and some non-OSA geoblocking reports; inclusion is not a claim that a site is currently blocked or that a VPN can restore a closed service. Court-page results also have varying check dates.

Domains are lowercased, deduplicated, and stripped of URL paths and a leading `www.`. Other subdomains are preserved. GL.iNet routes by domain, so a report about one forum or page can route other traffic to that same domain too. Related media/CDN domains are included only when present in the sources.

## Subscription feeds

| Feed | Coverage |
| --- | --- |
| [`glinet-live-sources-domains.txt`](https://raw.githubusercontent.com/dj-chalky/uk-vpn-routing-domains/main/glinet-live-sources-domains.txt) | Recommended GL.iNet feed: OSA sources and public court pages, excluding historical ISP results |
| [`glinet-osa-domains.txt`](https://raw.githubusercontent.com/dj-chalky/uk-vpn-routing-domains/main/glinet-osa-domains.txt) | GL.iNet-compatible OSA-only feed |
| [`osa-domains.txt`](https://raw.githubusercontent.com/dj-chalky/uk-vpn-routing-domains/main/osa-domains.txt) | Unmodified OSA feed, including valid digit-led domains rejected by the observed GL.iNet validator |
| [`court-domains.txt`](https://raw.githubusercontent.com/dj-chalky/uk-vpn-routing-domains/main/court-domains.txt) | Public UK court-block pages only |
| [`live-sources-domains.txt`](https://raw.githubusercontent.com/dj-chalky/uk-vpn-routing-domains/main/live-sources-domains.txt) | Unmodified OSA and court feeds |
| [`domains.txt`](https://raw.githubusercontent.com/dj-chalky/uk-vpn-routing-domains/main/domains.txt) | Everything available in this build, including historical ISP results; exceeds the observed GL.iNet limit |
| `glinet-full-part-1.txt` / `glinet-full-part-2.txt` | Full historical coverage adjusted for GL.iNet and split at the observed 200,000-line limit |
| `data/historical-blocked.txt` | Blocked targets in the January 2020 export only |
| `glinet-rejected-numeric-domains.txt` | Valid digit-led domains omitted from GL.iNet feeds |

`provenance.csv` records each target's sources. `metadata.json` records source counts and the last published build time. `data/historical-metadata.json` records the historical export hash, row counts and result dates. Invalid historical hostnames are listed in `data/historical-rejected.csv` instead of being silently inserted into the router feed. IP addresses, if present, are preserved in canonical form.

## GL.iNet setup

1. Copy the URL for the required feed from the table above. `glinet-live-sources-domains.txt` is the recommended default.
2. In GL.iNet VPN routing, choose **Specified Domain / IP List → Subscription URL**.
3. Paste the URL and select **Detect**.
4. Set **Use VPN** to the required tunnel and apply the rule.

The feeds use the plain-text format documented by GL.iNet. Compatibility findings below were observed with firmware v4.9.0 and may differ on other versions or models.

The workflow checks daily. The router's documented subscription refresh is daily, so publication and router refresh can occur at different times. GitHub can disable scheduled workflows in inactive public repositories; check Actions if updates stop. Failed downloads, invalid domains, suspiciously small sources or a loss of more than 20% of existing entries stop the update and preserve the published list. Review the cause before using `python update.py --allow-large-change` manually.

## GL.iNet v4.9.0 compatibility

Testing with GL.iNet firmware v4.9.0 identified two undocumented validator behaviours:

- Domain names whose first character is a digit are rejected, although such names are valid DNS names. IPv4 addresses beginning with a digit are accepted. In the first 200,000 lines of `domains.txt`, this exactly explains all 18,225 rejected entries: 18,270 targets began with a digit and 45 of those were accepted IPv4 addresses.
- The detector examined exactly 200,000 of the 339,635 input lines.

The `glinet-*` feeds remove digit-led domain names while retaining IP addresses. The full feed is split into two files of at most 200,000 lines. Using both full parts requires two destination rules aimed at the same VPN tunnel, if the router interface permits that configuration. The recommended single subscription is `glinet-live-sources-domains.txt`; it avoids historical data and remains far below the observed limit.

## Refresh locally

With Python 3.10 or later, run `python update.py`. No third-party packages are required. All live sources must succeed before generated files change.

The court collector follows the public pagination at a modest request rate and refuses empty or repeated pages. To rebuild the historical extraction, download the export and run `python import_history.py /path/to/export.csv.gz` (Python 3.11+). The large raw archive is not stored in this repository or downloaded on every scheduled run. If the upstream export changes, review its date and replace the historical extraction explicitly.

## Attribution

Blocked.org.uk data: Open Rights Group, licensed under Creative Commons Attribution 4.0 International unless otherwise specified: https://www.blocked.org.uk/licence . Changes: extraction of hostnames, normalization and merging.

OSA Tracker: https://osatracker.co.uk/ . Section 6 of its terms makes the published list and exports freely available for reuse: https://osatracker.co.uk/terms . No ownership or blanket license over that source's data is asserted here.

GL.iNet format documentation: https://docs.gl-inet.com/router/en/4/tutorials/how_to_configure_domain_and_ip_filtering_rules_for_glinet_routers_via_an_online_text_file/

GL.iNet subscription refresh documentation: https://docs.gl-inet.com/router/en/4/interface_guide/vpn_dashboard_v4.8/
