Analysis Scripts
================

These scripts were used to collect, parse, and regenerate the integration-test
history data stored in ``analysis/data/`` and the RST report at
``analysis/integration_test_results_history.rst``.

.. contents::
   :local:
   :depth: 1

Scripts overview
----------------

``collect_integration_test_history.py``
    **Primary script.**  Scans GitHub PR comments tagged
    ``<!-- integration-test-summary -->`` (posted by ``github-actions[bot]`` via
    ``.github/workflows/integration_tests.yml``), parses the embedded performance and
    file-descriptor markdown tables, and writes all eight CSV files plus the RST report.

``update_recent_slice.py``
    **Utility script.**  Re-derives ``data/integration_test_results_history_recent_N.csv``
    from the canonical ``data/integration_test_results_history_overview.csv``.
    Run this after ``collect_integration_test_history.py`` to refresh the
    convenience slice without another API call.

Requirements
------------

* Python 3.9+ (standard library only — no third-party packages needed)
* A GitHub personal access token with ``repo`` scope (or ``public_repo`` for
  public repos) stored in the ``GITHUB_TOKEN`` environment variable, or passed
  via ``--token``.

Quick start
-----------

Incremental update (recommended — only fetches new PRs)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

    export GITHUB_TOKEN=ghp_...
    python3 analysis/scripts/collect_integration_test_history.py

    # Refresh the recent-20 slice
    python3 analysis/scripts/update_recent_slice.py

    # Commit both the updated CSVs and the updated RST
    git add analysis/
    git commit -m "Update integration-test history $(date -u +%Y-%m-%dT%H:%M:%SZ)"

Full regeneration (re-scans all PRs from scratch)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use this when you want a clean re-parse — for example after fixing a parser bug.

.. code-block:: bash

    export GITHUB_TOKEN=ghp_...
    python3 analysis/scripts/collect_integration_test_history.py --mode full

Collecting a larger window
~~~~~~~~~~~~~~~~~~~~~~~~~~

By default the script scans the newest 500 PRs.  Increase ``--max-prs`` if the
repository has more PRs with integration-test comments, but be aware of GitHub
API rate limits (5 000 requests/hour for authenticated requests):

.. code-block:: bash

    python3 analysis/scripts/collect_integration_test_history.py --max-prs 2000

Environment variables
---------------------

Both scripts honour the following environment variables as defaults (all can be
overridden via CLI flags):

============================================  ============================  ========================================
Variable                                      Flag                          Description
============================================  ============================  ========================================
``GITHUB_TOKEN``                              ``--token``                   Required.  GitHub token.
``GITHUB_REPOSITORY``                         ``--repo``                    ``owner/repo`` string (default: ``carlkidcrypto/ezsnmp``).
``MAX_PRS``                                   ``--max-prs``                 Max PRs to scan per run (default: 500).
============================================  ============================  ========================================

``collect_integration_test_history.py`` reference
--------------------------------------------------

.. code-block:: text

    usage: collect_integration_test_history.py [-h] [--token TOKEN] [--repo REPO]
                                               [--max-prs N] [--mode {full,append}]
                                               [--recent-n N] [--no-rst]

    Options:
      --token TOKEN         GitHub personal access token (default: $GITHUB_TOKEN)
      --repo REPO           owner/repo (default: $GITHUB_REPOSITORY or carlkidcrypto/ezsnmp)
      --max-prs N           Maximum PRs to scan newest-first (default: 500)
      --mode {full,append}  append (default): skip PRs already in overview.csv.
                            full: overwrite all CSVs from scratch.
      --recent-n N          Size of the recent_N slice CSV (default: 20)
      --no-rst              Skip regenerating the RST report

``update_recent_slice.py`` reference
-------------------------------------

.. code-block:: text

    usage: update_recent_slice.py [-h] [--n N] [--overview PATH] [--out PATH]

    Options:
      --n N              Number of most-recent rows (default: 20)
      --overview PATH    Path to overview CSV (default: data/integration_test_results_history_overview.csv)
      --out PATH         Output path (default: data/integration_test_results_history_recent_<N>.csv)

Comment format parsed
---------------------

The scripts parse PR comments that match this structure (produced by
``.github/workflows/integration_tests.yml``, ``pr-summary`` job):

.. code-block:: text

    <!-- integration-test-summary -->
    ## Integration Test Results ⏱️

    <details>
    <summary>🚀 Performance Details …</summary>

    #### Multi Process Tests

    | Operation | Workers | Min (s) | Max (s) | Avg (s) | StdDev 📊 |
    |-----------|---------|---------|---------|---------|----------|
    | Bulkwalk  | 2       | 0.903   | 2.684   | 2.040   | 0.703    |
    …

    #### Multi Thread Tests
    …

    </details>

    ### 📁 File Descriptor Tests: ✅ No leaks detected

    <details>
    <summary>📋 FD Test Details …</summary>

    | Session | Operation | Mode     | FD Leak | Exec (s) | Avg/Call (s) |
    |---------|-----------|----------|---------|----------|-------------|
    | V1      | bulk_get  | close    | ✅      | 0.058    | 0.000580    |
    …

    </details>

**Important:** GitHub overwrites the comment body on every CI run, so older
comment bodies are permanently lost.  The CSVs under ``analysis/data/`` are the
only long-term record.  **Never delete them.**

CSV schemas
-----------

overview.csv
    rank, pr_number, pr_title, pr_url, comment_url, updated_at,
    performance_rows, fd_rows, fd_status

recent_N.csv
    Same schema as overview.csv — just the top-N rows.

performance_raw.csv
    pr_number, pr_title, pr_url, comment_url, updated_at,
    category, operation, workers, min_seconds, max_seconds,
    avg_seconds, stddev_seconds

fd_raw.csv
    pr_number, pr_title, pr_url, comment_url, updated_at,
    session, operation, mode, fd_leak, fd_leak_numeric,
    exec_seconds, avg_per_call_seconds, fd_status

fd_status.csv
    Status, Count

fd_summary.csv
    Session, Operation, Mode, Runs, Leak warnings,
    Mean FD leak, Avg Exec (s), Avg Avg/Call (s)

multi_process_tests_summary.csv / multi_thread_tests_summary.csv
    Operation, Workers, Runs, Min (s), Max (s), Avg (s), StdDev (s)

Troubleshooting
---------------

``GitHub API 401``
    Token is invalid or missing the required scope.

``No new data — CSVs are already up to date``
    All PRs found match rows already in ``overview.csv``.  Nothing to do.
    Pass ``--mode full`` to force a complete re-parse.

``Parsed 0 performance rows / 0 fd rows``
    Older PRs (before ~early 2026) do not have the structured table sections —
    those comments only contain plain text.  The script records them in
    ``overview.csv`` with ``performance_rows=0`` / ``fd_rows=0`` and
    ``fd_status=Unavailable``.

``Rate limit exceeded``
    GitHub allows 5 000 authenticated API requests per hour.  Each PR comment
    page costs one request; a typical run over 500 PRs costs roughly
    500–1 500 requests.  If you hit the limit, wait an hour and re-run —
    ``--mode append`` will skip everything already collected.
