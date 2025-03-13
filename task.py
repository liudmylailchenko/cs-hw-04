import os
import time
import threading
import multiprocessing


def search_in_file(file_path, keywords):
    file_result = {}
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        for keyword in keywords:
            if keyword in content:
                file_result.setdefault(keyword, []).append(file_path)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
    return file_result


# ======= Threading =======
def worker_thread(files, keywords, shared_result, lock):
    local_result = {}
    for file_path in files:
        result = search_in_file(file_path, keywords)
        for key, paths in result.items():
            local_result.setdefault(key, []).extend(paths)
    with lock:
        for key, paths in local_result.items():
            shared_result.setdefault(key, []).extend(paths)


def search_files_threading(file_list, keywords, num_threads=4):
    threads = []
    shared_result = {}
    lock = threading.Lock()

    chunk_size = (len(file_list) + num_threads - 1) // num_threads
    for i in range(num_threads):
        chunk = file_list[i * chunk_size : (i + 1) * chunk_size]
        thread = threading.Thread(
            target=worker_thread, args=(chunk, keywords, shared_result, lock)
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return shared_result


# ======= Multiprocessing =======
def worker_process(files, keywords, queue):
    local_result = {}
    for file_path in files:
        result = search_in_file(file_path, keywords)
        for key, paths in result.items():
            local_result.setdefault(key, []).extend(paths)
    queue.put(local_result)


def search_files_multiprocessing(file_list, keywords, num_processes=4):
    processes = []
    queue = multiprocessing.Queue()
    results = {}

    chunk_size = (len(file_list) + num_processes - 1) // num_processes
    for i in range(num_processes):
        chunk = file_list[i * chunk_size : (i + 1) * chunk_size]
        proc = multiprocessing.Process(
            target=worker_process, args=(chunk, keywords, queue)
        )
        processes.append(proc)
        proc.start()

    for _ in processes:
        local_result = queue.get()
        for key, paths in local_result.items():
            results.setdefault(key, []).extend(paths)

    for proc in processes:
        proc.join()

    return results


if __name__ == "__main__":
    file_list = [
        "./files/file1.txt",
        "./files/file2.txt",
        "./files/file3.txt",
        "./files/file4.txt",
        "./files/file5.txt",
    ]
    keywords = ["multiprocessing", "threading", "critical", "qwerty", "lorem", "test"]

    # ======= Threading =======
    start_time = time.time()
    result_threading = search_files_threading(file_list, keywords, num_threads=4)
    threading_time = time.time() - start_time

    print("Results (threading):")
    for keyword, files_found in result_threading.items():
        print(f"{keyword}: {files_found}")
    print(f"Time (threading): {threading_time:.4f} s\n")

    # ======= Multiprocessing =======
    start_time = time.time()
    result_multiprocessing = search_files_multiprocessing(
        file_list, keywords, num_processes=4
    )
    multiprocessing_time = time.time() - start_time

    print("Results (multiprocessing):")
    for keyword, files_found in result_multiprocessing.items():
        print(f"{keyword}: {files_found}")
    print(f"Time (multiprocessing): {multiprocessing_time:.4f} s")
