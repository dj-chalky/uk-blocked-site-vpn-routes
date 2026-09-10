# Contributing

Thanks for helping improve the lists or their updater.

## Reporting a list problem

Open an issue and include:

- The affected domain.
- The list in which it appears or should appear.
- A link to the relevant OSA Tracker or Blocked.org.uk report, when available.
- The GL.iNet model and firmware version if the problem concerns router detection.

The text, CSV and JSON data files are generated, so corrections should normally be made in the upstream source or in the extraction and normalization code. Please do not manually add or remove an entry from a generated list without explaining why it cannot be corrected upstream.

## Proposing a code change

Keep changes focused and update or add a meaningful unit test when behaviour changes. Run `python -m unittest -v` before opening a pull request. The project supports Python 3.10 or later for normal updates.

Do not include private browsing records, router configuration exports, credentials or other personal data in issues or pull requests.
