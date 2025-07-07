# movrs-client

A GUI and CLI client for MOVRS.

## Installation

**All commands listed below must be run with `sudo` privileges.**

### 1. Install Python on Ubuntu 22.04

First, update your package list and install Python 3 and pip:

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip
```

### 2. Install the movrs-client package

You can install this package directly from the public GitHub repository using pip:

```bash
sudo pip install git+https://github.com/Movrs/movrs-client.git
```

Alternatively, if you have already cloned the repository locally:

```bash
sudo pip install .
```

## Usage

To launch the MOVRS GUI application, run the following command with `sudo`:

```bash
sudo movrs-client
```