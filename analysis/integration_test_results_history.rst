Integration Test Results History ⏱️
==================================

This report aggregates every currently recoverable successful PR comment tagged with
``<!-- integration-test-summary -->``.

**Report generated:** ``2026-07-12T15:36:36Z``

Notes
-----

* GitHub updates these PR comments in place, so older successful run bodies are overwritten.
* Accessible successful comment summaries found: ``41``.
* The requested 100-run window is larger than the number of currently recoverable comment payloads.
* ``Unavailable`` in the status CSV means the older comment body did not expose a file-descriptor status line.

Dataset
-------

* Comments analyzed: ``41``
* Newest PR update in sample: ``2026-07-12T15:09:28Z``
* Oldest PR update in sample: ``2026-02-06T08:59:13Z``
* Performance rows parsed: ``849`` (30 comments with tabular performance data)
* File descriptor rows parsed: ``2520`` (30 comments with tabular FD data)

CSV files
---------

All CSV data files live under the ``data/`` sub-folder next to this report.

* ``data/integration_test_results_history_overview.csv`` — **complete** set: every recoverable
  source comment found at report-generation time (41 entries in the initial run).  This is the
  canonical record; append new rows here on every future update.
* ``data/integration_test_results_history_recent_20.csv`` — **convenience subset**: a fixed
  window of the newest 20 entries, sliced from the overview at report-generation time.  The
  number ``20`` is an arbitrary display cap, not a batch size.  If all recoverable comments fit
  in 20 rows this file is smaller than the overview; once the dataset exceeds 20 entries these
  files will diverge.  Regenerate this slice from the overview whenever a new batch is added.
* ``data/integration_test_results_history_performance_raw.csv`` — every parsed performance row
* ``data/integration_test_results_history_fd_raw.csv`` — every parsed file-descriptor row
* ``data/integration_test_results_history_fd_status.csv`` — file-descriptor status counts
* ``data/integration_test_results_history_fd_summary.csv`` — aggregated file-descriptor metrics
* ``data/integration_test_results_history_multi_process_tests_summary.csv`` — aggregated multi process tests performance metrics
* ``data/integration_test_results_history_multi_thread_tests_summary.csv`` — aggregated multi thread tests performance metrics

Future Results
--------------

New integration-test runs should **append** rows to the existing CSVs in ``data/`` rather than
regenerating from the full PR history.  This keeps the dataset growing incrementally and avoids
re-fetching comment history that GitHub may have already overwritten.  To add a new result set:

1. Run the analysis script against the latest PR comments.
2. Append new rows (deduplicated by PR number / timestamp) to the relevant CSV files in ``data/``.
3. Regenerate this ``.rst`` file with an updated **Report generated** timestamp and updated Dataset counts.
4. Commit both the updated CSVs and the updated ``.rst`` to the ``analysis/`` folder.

Performance Details
-------------------

Multi Process Tests
^^^^^^^^^^^^^^^^^^^

.. csv-table:: Historical aggregate for multi process tests
   :file: data/integration_test_results_history_multi_process_tests_summary.csv
   :header-rows: 1

Multi Thread Tests
^^^^^^^^^^^^^^^^^^

.. csv-table:: Historical aggregate for multi thread tests
   :file: data/integration_test_results_history_multi_thread_tests_summary.csv
   :header-rows: 1

File Descriptor Tests
---------------------

.. csv-table:: File descriptor status counts
   :file: data/integration_test_results_history_fd_status.csv
   :header-rows: 1

.. csv-table:: Aggregated file descriptor metrics
   :file: data/integration_test_results_history_fd_summary.csv
   :header-rows: 1

Recent Successful Results
-------------------------

.. csv-table:: The newest 20 successful integration-test summary comments in the recoverable sample
   :file: data/integration_test_results_history_recent_20.csv
   :header-rows: 1

