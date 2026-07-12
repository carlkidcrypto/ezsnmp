Integration Test Results History ⏱️
==================================

This report aggregates every currently recoverable successful PR comment tagged with
``<!-- integration-test-summary -->``.

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

* ``integration_test_results_history_overview.csv`` — all recoverable source comments
* ``integration_test_results_history_recent_20.csv`` — the newest 20 source comments
* ``integration_test_results_history_performance_raw.csv`` — every parsed performance row
* ``integration_test_results_history_fd_raw.csv`` — every parsed file-descriptor row
* ``integration_test_results_history_fd_status.csv`` — file-descriptor status counts
* ``integration_test_results_history_fd_summary.csv`` — aggregated file-descriptor metrics
* ``integration_test_results_history_multi_process_tests_summary.csv`` — aggregated multi process tests performance metrics
* ``integration_test_results_history_multi_thread_tests_summary.csv`` — aggregated multi thread tests performance metrics

Performance Details
-------------------

Multi Process Tests
^^^^^^^^^^^^^^^^^^^

.. csv-table:: Historical aggregate for multi process tests
   :file: integration_test_results_history_multi_process_tests_summary.csv
   :header-rows: 1

Multi Thread Tests
^^^^^^^^^^^^^^^^^^

.. csv-table:: Historical aggregate for multi thread tests
   :file: integration_test_results_history_multi_thread_tests_summary.csv
   :header-rows: 1

File Descriptor Tests
---------------------

.. csv-table:: File descriptor status counts
   :file: integration_test_results_history_fd_status.csv
   :header-rows: 1

.. csv-table:: Aggregated file descriptor metrics
   :file: integration_test_results_history_fd_summary.csv
   :header-rows: 1

Recent Successful Results
-------------------------

.. csv-table:: The newest 20 successful integration-test summary comments in the recoverable sample
   :file: integration_test_results_history_recent_20.csv
   :header-rows: 1

