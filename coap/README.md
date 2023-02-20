## CoAP client/server

To run the client and the server, you will need Python version 3.8 or higher on both machines.

### Create Python venv (optional)

If you don't want to affect your global Python installation, you can create a virtual environment and activate it:

```bash
$ python3 -m venv venv
$ source ./venv/bin/activate
```

### Install required packages

Install the packages using the following command:

```bash
$ pip3 install -r requirements.txt
```

This command will install packages required for both the server and the client.

### Running the server

To run the server on the default port, run

```bash
$ ./server.py /path/to/data/root
```

If you want to change the address the server will bind to, you can use `--host` and `--port` options

### Running the client

To run the client, run a command like this:
```bash
./client.py --count 10 100B
```

You should get an output similar to this:
```bytes
Receive time:   1325142.6 ± 854621.0851073358 ns
Bytes received: 109.0 ± 0.0 bytes
Overhead:       1.09 ± 0.0
Throughput:     719.5109695378906 ± 187.775259730763 kbps
```

Here, the `--count` option specifies how many times a download will be performed, and the output gives
you aggregated metrics of all runs (in this case, 10).

You can also specify the host and port of the server with `--host` and `--port` options, respectively.

