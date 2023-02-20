#!/usr/bin/env python3

import argparse
import requests
import socket
import time

import numpy as np

from dataclasses import dataclass
from httpsuite import Response

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
    response = Response.parse(raw_data)
    end_time = time.perf_counter_ns()

    assert response.status.integer < 400
    return Measurement(
            time=end_time - start_time,
            recv=len(raw_data),
            size=len(response.body))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="name of the file to get")
    parser.add_argument("-c", "--count", type=int, default=1, help="number of times the requested file should be downloaded")
    parser.add_argument("--host", default="localhost", help="host to connect to")
    parser.add_argument("--port", type=int, default=80, help="port to connect to")

    args = parser.parse_args()

    data = [measure_download_time(args.host, args.port, f"/{args.file}") for _ in range(args.count)]

    times = np.array([d.time for d in data])
    recv = np.array([d.recv for d in data])
    sizes = [d.size for d in data]
    assert len(set(sizes)) == 1
    size = sizes[0]


    print(f"Receive time:   {np.mean(times)} ± {np.std(times)} ns")
    print(f"Bytes received: {np.mean(recv)} ± {np.std(recv)} bytes")
    overhead = recv / size
    print(f"Overhead:       {np.mean(overhead)} ± {np.std(overhead)}")

    # Size is in bytes, and speed is needed in kbps, so multiply by 8
    throughput = size / (times / 10**9) * 8 / 1000
    print(f"Throughput:     {np.mean(throughput)} ± {np.std(throughput)} kbps")


if __name__ == "__main__":
    main()

