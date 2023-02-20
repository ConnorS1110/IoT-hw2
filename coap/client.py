#!/usr/bin/env python3

import aiocoap
import argparse
import asyncio
import logging
import time

import numpy as np

import aiocoap.transports.udp6

from dataclasses import dataclass


@dataclass
class Measurement:
    time: int
    recv: int
    size: int


async def measure_download_time(protocol, uri):
    start_time = time.perf_counter_ns()
    msg = aiocoap.Message(code=aiocoap.GET, uri=uri)
    response = await protocol.request(msg).response
    end_time = time.perf_counter_ns()
    return Measurement(
            time=end_time - start_time,
            recv=len(response.encode()),
            size=len(response.payload))


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file", help="name of the file to get")
    parser.add_argument("-c", "--count", type=int, default=1, help="number of times the requested file should be downloaded")
    parser.add_argument("--host", default="localhost", help="host to connect to")
    parser.add_argument("--port", default="5683", help="port to connect to")

    args = parser.parse_args()

    protocol = await aiocoap.Context.create_client_context()
    uri = f"coap://{args.host}:{args.port}/hw_files/{args.file}"

    data = [await measure_download_time(protocol, uri) for _ in range(args.count)]

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
    asyncio.run(main())

