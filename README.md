# cs145-pull-client

in partial fulfillment of the requirements of the CS 145 course
for the second semester of Academic Year 2021-2022

## About

This is an implementation of a client for the pull-centric UDP-based protocol for CS 145, written in Python 3.

## Requirements

The program was developed on Python 3.8.10, which is the version of Python 3
that comes with new Ubuntu instances on AWS. It should work on Python 3.8+ given
that the requirements are also installed (see [Installation](#installation)).

## Installation

Make sure you have Pip installed and accessible from your `$PATH`. Check by running

```bash
pip3 --version
```

It should output something like

```
pip 20.0.2 from /usr/lib/python3/dist-packages/pip (python 3.8)
```

If it does not, please install Pip first before proceeding. For example, on Ubuntu systems
such as the instance used for the project, this can be done by running

```bash
sudo apt install python3-pip
```

Once you've verified that Pip is installed, you can install the requirements by running

```bash
pip3 install --user -r requirements.txt
```

from within the project directory. This will install SymPy, along with its dependencies,
which the project uses for factorizing the challenge questions sent by the protocol server.

Verify that SymPy has been installed by opening a Python interactive console:
    
```bash
python3
```

and running

```python
import sympy
```

If an error is thrown, SymPy is not installed. Please make sure it's installed properly before proceeding.

## Running

The program requires 4 arguments, which are mandated by the project specifications. They are as follows:

|Flag|Parameter|Description|
|-----|-----|-----|
|`-a`, `--address`|`<IP address>`|IP address of the server|
|`-s`, `--server-port`|`<port number>`|Port of the server|
|`-c`, `--client-port`|`<port number>`|Port assigned to the client (make sure it is unused, or the program will not bind to it!)|
|`-i`, `--id`|`<unique ID>`|Unique ID assigned to the client|

All of the arguments above have default values set in `util/constants.py`;
if they are not supplied on the command line, the default values will be used instead.

Running the program is as easy as

```bash
python3 client.py <arguments>
```
