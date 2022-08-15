# cs145-pull-client

in partial fulfillment of the requirements of the CS 145 course
for the second semester of Academic Year 2021-2022

# About

This is an implementation of a client for the pull-centric UDP-based protocol for CS 145, written in Python 3.

# Requirements

The program was developed on Python 3.8.10, which is the version of Python 3
that comes with new Ubuntu instances on AWS. It should work on Python 3.8+ given
that the requirements are also installed.

Make sure you have a compatible version of Python installed. Create a virtual
environment by running

```bash
python3 -m venv .venv
```

Then activate the virtual environment by running

```bash
# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

Then install the requirements by running

```bash
pip install -r requirements.txt
```

# Running

The program accepts 5 optional flags, 4 of which are mandated by the project specifications. They are as follows:

|Flag|Parameter|Description|
|-----|-----|-----|
|`-a`, `--address`|`<IP address>`|IP address of the server|
|`-s`, `--server-port`|`<port number>`|Port of the server|
|`-c`, `--client-port`|`<port number>`|Port of the client (make sure it is unused, or the program will not bind to it!)|
|`-i`, `--id`|`<unique ID>`|Assigned unique ID to the client|
|`-q`, `--quiet`|N/A|Include this flag if you want to silence all logs except for warnings and errors. Disabled by default (i.e. will log everything)|

All of the flags except for `-q` have default values set in `util/constants.py`; if they are not supplied on the command line, the default values will be used instead.

Running the program is as easy as

```bash
python3 client.py <arguments>
```
