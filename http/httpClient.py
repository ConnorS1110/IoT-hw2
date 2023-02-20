#!/usr/bin/env python3

import argparse
import socket
import time

import numpy as np

from dataclasses import dataclass
from http_parser.parser import HttpParser

@dataclass
class Measurement:
    time: int
    recv: int
    size: int

    def __str__(self):
        return f"<Measurement total: {self.recv} size: {self.size} time: {self.time}>"


def get_raw_http(host, port, path):
    request = f"GET {path} HTTP/1.1\r\nHost:{host}\r\n\r\n".encode("utf-8")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(request)

        response_chunks = []
        while True:
            d = s.recv(4096)
            if not d:
                break
            response_chunks.append(d)
        return b"".join(response_chunks)


def measure_download_time(host, port, path):
    start_time = time.perf_counter_ns()
    raw_data = get_raw_http(host, port, path)
    parser = HttpParser()
    nparsed = parser.execute(raw_data, len(raw_data))
    assert nparsed == len(raw_data)
    end_time = time.perf_counter_ns()

    assert parser.get_status_code() < 400
    return Measurement(
            time=end_time - start_time,
            recv=len(raw_data),
            size=len(parser.recv_body()))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost", help="host to connect to")
    parser.add_argument("--port", type=int, default=80, help="port to connect to")

    files_list = [["1MB", 100], ["10KB", 1000], ["10MB", 10], ["100B", 10000]]

    args = parser.parse_args()

    for file in files_list:
        data = [measure_download_time(args.host, args.port, f"/{file[0]}") for _ in range(file[1])]

        times = np.array([d.time for d in data])
        recv = np.array([d.recv for d in data])
        sizes = [d.size for d in data]
        assert len(set(sizes)) == 1
        size = sizes[0]

        print(f"Current file: {file[0]}")
        print(f"Receive time:   {np.mean(times)} ± {np.std(times)} ns")
        print(f"Bytes received: {np.mean(recv)} ± {np.std(recv)} bytes")
        overhead = recv / size
        print(f"Overhead:       {np.mean(overhead)} ± {np.std(overhead)}")

        # Size is in bytes, and speed is needed in kbps, so multiply by 8
        throughput = size / (times / 10**9) * 8 / 1000
        print(f"Throughput:     {np.mean(throughput)} ± {np.std(throughput)} kbps\n")


if __name__ == "__main__":
    main()
