# HTTP Instructions

## Setup for Client
There are Python library requirements for the client to work properly. For proper setup run:

```
pip install -r requirements.txt
```

This will install the required libraries. You need to have a `python3-devel` package installed
on your system.


## Starting up the server
To start the server, navigate to the `./data/` directory in a terminal window and run:

For Python 3.x:
```
python -m http.server [port]
```

This will host an HTTP server of the files in `./data`

## Running the client
Once the server is running, the following command will run the client:

```
python httpClient.py --host [VALUE] --port [VALUE]
```

The host and flag values are optional. The default host is `localhost` and the default port is `80`.

The client will run automatically. It will systematically iterate through every file in data, and run it
the required number of times. After each file, the relevant statistics will be output to the console before
moving to the next file. The client will automatically exit upon completion, but the server will continue to
run until you manually stop the server.
