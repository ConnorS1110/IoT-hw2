#!/usr/bin/env python3

import aiocoap
import argparse
import asyncio
import logging
import socket
import time

import numpy as np

import aiocoap.transports.udp6

from dataclasses import dataclass

class CountingSocket(socket.socket):
    bytes_received = 0

    def recvmsg(self, *args, **kwargs):
        ret = super().recvmsg(*args, **kwargs)
        self.increase_recv_counter(len(ret[0]))
        return ret

    @classmethod
    def reset_recv_counter(cls):
        cls.bytes_received = 0

    @classmethod
    def increase_recv_counter(cls, count):
        cls.bytes_received += count

    @classmethod
    def get_recv_counter(cls):
        return cls.bytes_received


@classmethod
async def new_create_client_transport_endpoint(cls, ctx, log, loop):
    sock = CountingSocket(family=socket.AF_INET6, type=socket.SOCK_DGRAM)
    sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)

    return await cls._create_transport_endpoint(sock, ctx, log, loop)

# Monkeypatching aiocoap to use our counting sockets
aiocoap.transports.udp6.MessageInterfaceUDP6.create_client_transport_endpoint = new_create_client_transport_endpoint


@dataclass
class Measurement:
    time: int
    recv: int
    size: int


async def measure_download_time(protocol, uri):
    CountingSocket.reset_recv_counter()
    start_time = time.perf_counter_ns()
    msg = aiocoap.Message(code=aiocoap.GET, uri=uri)
    response = await protocol.request(msg).response
    end_time = time.perf_counter_ns()
    return Measurement(
            time=end_time - start_time,
            recv=CountingSocket.get_recv_counter(),
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

