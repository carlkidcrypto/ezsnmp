---
name: Python Version Watcher

on:
  schedule:
    - cron: "0 9 1 * *"
  workflow_dispatch:
  skip-if-match:
    query: "is:pr is:open head:automation/python-version-watcher label:automated-pr"

permissions:
  actions: read
  contents: read

safe-outputs:
  create-pull-request:
    title-prefix: "[python-version]"
    labels:
      - automated-pr
    draft: true
    preserve-branch-name: true
    if-no-changes: ignore

timeout-minutes: 45

network: defaults

tools:
  edit:
  bash: true

engine:
  id: copilot
  model: gpt-4o
---

## Python Version Watcher and Auto-Sync

Monitor https://devguide.python.org/versions/ for changes to the set of actively supported Python
versions and automatically update the repository to stay in sync.

## Goals

- Detect which Python versions are currently supported (status = "bugfix", "security", or
  "prerelease") vs. end-of-life (status = "end-of-life").
- Update `setup.cfg` (`python_requires` range, `[tool:black]` `target-version` list, and
  `Programming Language :: Python :: 3.x` classifier lines) to reflect the current supported set.
- Update all four workflow files that declare a `python-version: [...]` matrix list (five
  occurrences total, because `tests_homebrew.yml` has two):
  - `.github/workflows/tests_native.yml`
  - `.github/workflows/tests_homebrew.yml` (has **two** occurrences of the matrix line)
  - `.github/workflows/tests_macports.yml`
  - `.github/workflows/integration_tests.yml`
- Open a draft PR only when changes are actually needed.
## Steps

### 1. Fetch the Python versions page

Use `curl` to download the Python versions page:

```bash
curl -fsSL https://devguide.python.org/versions/ -o /tmp/pyversions.html
```

- If the command fails (non-zero exit code), stop immediately and report the error.
- Check that `/tmp/pyversions.html` is at least 500 bytes. If not, stop and report that the
  page content looks truncated or empty.

### 2. Parse supported versions

Use Python to extract the currently supported version numbers from the downloaded page:

```python
import re

with open('/tmp/pyversions.html') as f:
    content = f.read()

# The devguide page includes a table where each row has a version number and a status.
# Supported statuses are: bugfix, security, prerelease.
# End-of-life versions are excluded.
#
# Match rows that contain a supported status and extract the 3.x version number.
# The page structure typically contains version numbers like "3.10", "3.11", etc.
# and status strings like "bugfix", "security", "prerelease", "end-of-life".
#
# Strategy: find all version+status pairs from the HTML table content.
# Look for patterns like: >3.12<  ...  >bugfix<  or similar table cell patterns.

# Extract version-status pairs from the versions table.
# The table rows look like: <td>3.13</td> ... <td>bugfix</td>
# Use a broad pattern then filter by status.
rows = re.findall(
    r'<tr[^>]*>.*?</tr>',
    content,
    re.DOTALL | re.IGNORECASE
)

supported = []
for row in rows:
    # Look for a 3.x version number in this row
    ver_match = re.search(r'\b(3\.\d+)\b', row)
    if not ver_match:
        continue
    version = ver_match.group(1)
    # Check if this row contains a supported status
    if re.search(r'\b(bugfix|security|prerelease)\b', row, re.IGNORECASE):
        supported.append(version)

# Sort numerically by minor version
supported = sorted(set(supported), key=lambda v: int(v.split('.')[1]))
print(supported)
```

- If fewer than 3 supported versions are found, stop and report a parsing error (the page
  structure may have changed).
- Log the list of discovered supported versions before proceeding.

### 3. Read current repo state

Read the following files to determine what versions are currently declared in the repository:

- `setup.cfg`: read `python_requires`, `target-version`, and all
  `Programming Language :: Python :: 3.x` classifier lines.
- `.github/workflows/tests_native.yml`: read the `python-version: [...]` matrix line.
- `.github/workflows/tests_homebrew.yml`: read **both** occurrences of the
  `python-version: [...]` matrix line (there are two — one near line 47, one near line 291).
- `.github/workflows/tests_macports.yml`: read the `python-version: [...]` matrix line.
- `.github/workflows/integration_tests.yml`: read the `python-version: [...]` matrix line.

Extract the currently declared version list from these files and compare it to the
`supported` list obtained in Step 2.

### 4. Check whether updates are needed

Compute the expected new values:

- **`python-version` matrix list** (for all five workflow files):
  A JSON-style array of the supported versions, e.g. `["3.10", "3.11", "3.12", "3.13"]`.
  The line format is: `        python-version: ["3.10", "3.11", ...]`
  (8 spaces of indentation, versions as double-quoted strings, separated by `, `).

- **`python_requires`** (in `setup.cfg`):
  `>={min},<{max_minor_plus_one}` where `min` is the lowest supported version and
  `max_minor_plus_one` is `3.{N+1}` where `N` is the minor of the highest supported version.
  Example: if supported = ["3.10", "3.11", "3.12", "3.13"], then
  `python_requires = >=3.10,<3.14`.

- **`target-version`** (in `setup.cfg`):
  A list of `pyXYZ` tokens, e.g. `['py310', 'py311', 'py312', 'py313']`.

- **Classifier lines** (in `setup.cfg`):
  One line per supported version:
  `    Programming Language :: Python :: 3.x`
  (4 spaces of indentation).

If all current values already match the expected new values exactly, call the `noop` safe
output tool with a message like:
"No update needed. Supported versions are already [list]. All files are up to date."
Then stop.

### 5. Update `setup.cfg`

Apply the following edits to `setup.cfg`:

1. **`python_requires`**: Replace the existing `python_requires = ...` line with the new range.

2. **`target-version`**: Replace the existing `target-version = [...]` line with the new list.

3. **Classifier lines**: Replace the entire block of consecutive
   `Programming Language :: Python :: 3.x` classifier lines with the new set of classifier
   lines (one per supported version, in ascending order, each indented with 4 spaces).

### 6. Update the four workflow files (five occurrences total)

For each of the four workflow files listed in the Goals section, replace every occurrence of the
`python-version: [...]` matrix definition line with the new version list.

The exact pattern to match and replace is the line:
```
        python-version: ["3.10", "3.11", "3.12", "3.13", "3.14"]
```
(with whatever version values are currently present).

Replace it with:
```
        python-version: [<new comma-separated quoted versions>]
```

- For `.github/workflows/tests_homebrew.yml`, there are **two** occurrences of this line.
  Both must be updated.
- Apply these edits using the `edit` tool.

### 7. Open a draft PR

After all edits are applied, create a pull request using:

- **Branch**: `automation/python-version-watcher`
- **Base**: `main`
- **Title**: `chore: sync supported Python versions`
- **Commit message**: `chore: sync supported Python versions to devguide.python.org`

Include the following information in the PR body:

- Source checked: https://devguide.python.org/versions/
- Newly detected supported versions (with their statuses if available)
- Summary of changes made per file
- Note that this was generated automatically by the Python Version Watcher workflow
