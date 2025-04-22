"""
This script is used to test the performance of the SNMP bulkwalk operation using threads and processes.
"""

import multiprocessing
import threading
from time import time
import sys
from globals import worker

if __name__ == "__main__":
    start_time = time()
    # Check if the number of processes/threads is provided as a command line argument
    if len(sys.argv) > 1:
        num_processes = int(sys.argv[1])
    else:
        raise ValueError(
            "Please specify the number of processes/threads as the first argument"
        )

    # Check if the user wants to use threads or processes
    type_of_execution = sys.argv[2]
    if len(sys.argv) > 2 and type_of_execution == "thread":
        # Create and start the specified number of threads
        threads = []
        for _ in range(num_processes):
            thread = threading.Thread(target=worker, args=("bulkwalk",))
            thread.start()
            threads.append(thread)

        # Main thread continues to execute while the worker threads are running
        print(
            f"multi_{type_of_execution}_snmp_bulkwalk: - {num_processes} - Main {type_of_execution} executing"
        )

        # Wait for all worker threads to finish
        for thread in threads:
            thread.join()

    elif len(sys.argv) > 2 and type_of_execution == "process":
        # Create and start the specified number of processes
        processes = []
        for _ in range(num_processes):
            process = multiprocessing.Process(target=worker, args=("bulkwalk",))
            process.start()
            processes.append(process)

        # Main process continues to execute while the worker processes are running
        print(
            f"multi_{type_of_execution}_snmp_bulkwalk: - {num_processes} - Main {type_of_execution} executing"
        )

        # Wait for all worker processes to finish
        for process in processes:
            process.join()

    else:
        raise ValueError("Please specify 'thread' or 'process' as the second argument")

    # All processes/threads have finished, program exits
    print(
        f"multi_{type_of_execution}_snmp_bulkwalk: - {num_processes} - Main {type_of_execution} finished"
    )

    # Calculate and print the total execution time
    execution_time = time() - start_time
    print(
        f"multi_{type_of_execution}_snmp_bulkwalk: - {num_processes} - Total execution time: {execution_time} seconds"
    )
