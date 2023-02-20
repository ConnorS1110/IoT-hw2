#!/usr/bin/env python3

import argparse
import logging

from plumbum import local

import asyncio

import aiocoap
import aiocoap.error as error
import aiocoap.resource as resource


class NoSuchFile(error.NotFound): # just for the better error msg
    message = "Error: File not found!"


class FileResource(resource.Resource, resource.PathCapable):
    def __init__(self, root):
        super().__init__()
        self.root = local.path(root)

    def request_to_localpath(self, request):
        path = request.opt.uri_path
        if any('/' in p or p in ('.', '..') for p in path):
            raise InvalidPathError()

        return self.root / "/".join(path)

    async def render_get(self, request):
        p = self.request_to_localpath(request)
        if not p.is_file():
            raise NoSuchFile

        with open(p, "rb") as f:
            data = f.read()
        return aiocoap.Message(
                payload=data,
                content_format=aiocoap.numbers.ContentFormat.OCTETSTREAM
                )


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", help="directory to serve files from")
    parser.add_argument("--host", default="localhost", help="host to bind to")
    parser.add_argument("--port", type=int, default=None, help="port to bind to")

    args = parser.parse_args()

    root = resource.Site()
    root.add_resource([".well-known", "core"],
                      resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(["hw_files"], FileResource(args.root))
    
    await aiocoap.Context.create_server_context(root, bind=(args.host, args.port))

    await asyncio.get_running_loop().create_future()


if __name__ == "__main__":
    asyncio.run(main())

