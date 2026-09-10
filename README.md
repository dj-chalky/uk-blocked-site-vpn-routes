# UK Blocked-Site VPN Routes

[![Update status](https://github.com/dj-chalky/uk-blocked-site-vpn-routes/actions/workflows/update.yml/badge.svg)](https://github.com/dj-chalky/uk-blocked-site-vpn-routes/actions/workflows/update.yml)

Subscription lists that send domains affected by UK internet restrictions through a VPN while leaving ordinary internet traffic on the normal connection.

The lists are designed for GL.iNet's **VPN Policy → Specified Domain / IP List** feature. Add one subscription URL to the router and it will selectively use the chosen VPN tunnel when a listed domain is requested. This avoids routing every device and every website through the VPN.

The project brings together several kinds of UK restriction:

- Services reported as unavailable, withdrawn or geoblocked in connection with the Online Safety Act (OSA).
- Websites listed in public UK court-blocking reports.
- Historical UK ISP filtering results published by Open Rights Group.

The lists identify destinations to route; they do not operate a VPN, alter DNS settings or guarantee that a service will work. A closed service cannot be restored by routing it through a VPN, and old entries may no longer be blocked.

## Recommended subscription

For most GL.iNet users, use:

**[`glinet-live-sources-domains.txt`](https://raw.githubusercontent.com/dj-chalky/uk-blocked-site-vpn-routes/main/glinet-live-sources-domains.txt)**

This combines the current OSA sources and public court-block pages. It excludes the large, dated ISP-results archive and is adjusted for the domain validation behaviour observed in GL.iNet firmware v4.9.0.

### Add it to a GL.iNet router

1. Open the router's VPN policy settings and select the VPN tunnel to use.
2. Choose **Specified Domain / IP List**.
3. Choose **Subscription URL**.
4. Paste the recommended URL above and select **Detect**.
5. Apply the rule.

The project checks its live sources daily. GL.iNet also documents a daily refresh for subscription URLs, so list changes reach the router automatically after both update cycles have run.

## Available lists

| List | Intended use |
| --- | --- |
| [`glinet-live-sources-domains.txt`](https://raw.githubusercontent.com/dj-chalky/uk-blocked-site-vpn-routes/main/glinet-live-sources-domains.txt) | **Recommended.** Current OSA reports and public court-block pages, adjusted for GL.iNet |
| [`glinet-osa-domains.txt`](https://raw.githubusercontent.com/dj-chalky/uk-blocked-site-vpn-routes/main/glinet-osa-domains.txt) | OSA-related reports only, adjusted for GL.iNet |
| [`live-sources-domains.txt`](https://raw.githubusercontent.com/dj-chalky/uk-blocked-site-vpn-routes/main/live-sources-domains.txt) | Current OSA and court sources without GL.iNet-specific filtering |
| [`osa-domains.txt`](https://raw.githubusercontent.com/dj-chalky/uk-blocked-site-vpn-routes/main/osa-domains.txt) | OSA-related sources without GL.iNet-specific filtering |
| [`court-domains.txt`](https://raw.githubusercontent.com/dj-chalky/uk-blocked-site-vpn-routes/main/court-domains.txt) | Public UK court-block pages only |
| [`domains.txt`](https://raw.githubusercontent.com/dj-chalky/uk-blocked-site-vpn-routes/main/domains.txt) | Full research dataset, including historical ISP results; too large for one observed GL.iNet import |
| `glinet-full-part-1.txt` and `glinet-full-part-2.txt` | Full historical dataset adjusted for GL.iNet and split into two router-sized files |

Supporting files provide auditability:

- `provenance.csv` records which source or sources contributed each target.
- `metadata.json` records source counts and the last successful build.
- `data/historical-metadata.json` records details of the historical export.
- `data/historical-rejected.csv` records invalid historical hostnames that were not published.
- `glinet-rejected-numeric-domains.txt` records valid digit-led names omitted from GL.iNet feeds.

## What is included

The live lists use:

- [OSA Tracker](https://osatracker.co.uk/) including its adult-domain export.
- [Blocked.org.uk's OSA reports](https://www.blocked.org.uk/osa-blocks).
- [Blocked.org.uk's public court-block reports](https://www.blocked.org.uk/legal-blocks/sites).

The full dataset also contains targets marked `blocked` in Blocked.org.uk's downloadable historical UK ISP-results export. That export was last modified on **17 January 2020**. It provides wider historical coverage, but it is not a complete or current list of ISP blocks. Its entries may now be unblocked, inactive or under different ownership.

OSA reports can include services that shut down, relaunched or geoblocked visitors. Inclusion means that a source reported the domain; it is not a claim that the domain is currently inaccessible or that the OSA definitively caused the restriction. Court reports also have different observation dates.

The comparison with other candidate OSA sources and the reasons for the current choices are documented in [SOURCE_REVIEW.md](SOURCE_REVIEW.md).

## How entries are prepared

Targets are converted to lowercase domain names, URL paths and a leading `www.` are removed, and duplicate entries are merged. Other subdomains are kept. Valid IP addresses are preserved.

Domain routing works at hostname level. If a source reports a specific page, the resulting rule can route other requests to that hostname as well. Related media, login or CDN domains are included only when one of the sources lists them.

### GL.iNet v4.9.0 compatibility

Testing with firmware v4.9.0 found that its list detector:

- Rejects domain names beginning with a digit, although they are valid DNS names. IPv4 addresses remain accepted.
- Examines at most 200,000 entries from a subscription.

The `glinet-*` files account for those behaviours. The full historical list is split at 200,000 entries and may require two destination rules pointing to the same VPN tunnel. The recommended live subscription is much smaller and fits in one rule.

Other GL.iNet models and firmware versions may behave differently.

## Updates and safeguards

A GitHub Actions workflow refreshes the live sources each day. If the resulting domain membership changes, it validates and publishes the new files automatically. A monthly maintenance marker keeps the scheduled workflow active during quiet periods.

An update is rejected if a source cannot be downloaded, returns no usable entries, repeats broken pagination, becomes suspiciously small or removes more than 20% of the existing list. The last valid published files remain available if a check fails.

To refresh locally with Python 3.10 or later, run `python update.py`. No third-party packages are required. Rebuilding the historical extraction requires Python 3.11 or later and an explicitly downloaded export; the large archive is not stored in this repository or downloaded during daily updates.

## Licensing

The original updater software and documentation are available under the [MIT License](LICENSE), copyright 2026 dj-chalky. That licence does not apply to third-party source data in the generated files. See [DATA-LICENSING.md](DATA-LICENSING.md) for the source-specific terms, attribution and changes made.

## Data sources and attribution

Blocked.org.uk data is published by Open Rights Group under [Creative Commons Attribution 4.0 International](https://www.blocked.org.uk/licence), unless otherwise specified. This project extracts hostnames, normalizes them and combines the source lists.

OSA Tracker makes its published list and exports available for reuse under [section 6 of its terms](https://osatracker.co.uk/terms). This project does not claim ownership of that source data.

GL.iNet documentation:

- [Online domain and IP filtering-list format](https://docs.gl-inet.com/router/en/4/tutorials/how_to_configure_domain_and_ip_filtering_rules_for_glinet_routers_via_an_online_text_file/)
- [VPN Dashboard and subscription refresh](https://docs.gl-inet.com/router/en/4/interface_guide/vpn_dashboard_v4.8/)

Problems with the generated files or updater can be reported through [GitHub Issues](https://github.com/dj-chalky/uk-blocked-site-vpn-routes/issues). See [CONTRIBUTING.md](CONTRIBUTING.md) before proposing a manual change to a generated list.
