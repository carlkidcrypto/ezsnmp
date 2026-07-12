Analysis
========

This folder stores historical integration-test analysis reports and the raw data that backs them.

Folder layout
-------------

::

    analysis/
    ├── README.rst                            # this file
    ├── integration_test_results_history.rst  # human-readable report (Sphinx-compatible)
    └── data/                                 # raw CSV data files
        ├── integration_test_results_history_overview.csv
        ├── integration_test_results_history_recent_20.csv
        ├── integration_test_results_history_performance_raw.csv
        ├── integration_test_results_history_fd_raw.csv
        ├── integration_test_results_history_fd_status.csv
        ├── integration_test_results_history_fd_summary.csv
        ├── integration_test_results_history_multi_process_tests_summary.csv
        └── integration_test_results_history_multi_thread_tests_summary.csv

Adding new results
------------------

When new integration-test data becomes available, **append** to the existing CSV files instead of
regenerating the full history from PR comments.  GitHub overwrites PR comments in place, so
older result bodies are lost over time; the CSVs in ``data/`` are the authoritative long-term
record.

Steps for a future update run:

1. Fetch the latest successful ``<!-- integration-test-summary -->`` PR comments.
2. Deduplicate against rows already present in ``data/integration_test_results_history_overview.csv``
   (use the PR number + ``updated_at`` timestamp as the composite key).
3. Append only the new rows to the relevant ``data/*.csv`` files.
4. Regenerate ``integration_test_results_history.rst`` with an updated **Report generated** timestamp
   and updated Dataset counts (comments analyzed, newest/oldest PR, rows parsed).
5. Commit the updated ``data/*.csv`` files and the updated ``.rst`` together.

Report timestamp
----------------

Each ``.rst`` report carries a **Report generated** field near the top showing the UTC timestamp
of when the report was last regenerated.  Update this field every time a new data batch is added.
