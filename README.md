# requirementsreadwrite

# Oscilloscope & Function Generator – Python (reqfRead / reqfWrite)

Implements `reqfRead` and `reqfWrite` in Python with a file-backed mock device.
CLI supports **acquire** and **generate**; prints bytes, duration, throughput, and latency percentiles (read).

## Setup
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt



## Install
python -m venv .venv
source .venv/bin/activate  # (Windows: .venv\Scripts\activate)
pip install -e .

## One-shot commands
python -m oscifgen acquire --in input.bin --out capture.bin --fs 1000 --n 8192
python -m oscifgen generate --out tx.out --fo 2000 --n 4096 --wave square --amp 1.0

## Command file (UI macro) — satisfies Homework 6
python -m oscifgen run --script scripts/demo.json

# Expected prints
# START (acquire) launched in background.
# WAIT done.
# STOP complete (joined background job).
# WRITE bytes=... time_s=... throughput_Bps=...


## Multi-Threaded Scope (Homework 9)

This repository also contains a multi-threaded scope example, as documented in Chapter 11
("Multi-Threading") of the project PDF.

### Location

- Folder: `scope_mt`
- Entry point: `scope.py`

### How to Run

```bash
git clone https://github.com/ForkyC/requirementsreadwrite_HW_7B
cd requirementsreadwrite_HW_7B/scope_mt
python scope.py start sampleTime=1ms wait=5s stop


# requirementsreadwrite_HW_7B

Oscilloscope & Function Generator in Python, plus a multi-threaded scope that reads from the **microphone**.

---

## 1. Overview

This repo contains two main pieces:

1. **Oscilloscope & Function Generator (`oscifgen`)**

   - Implements the functional requirements:
     - `reqfRead` – acquire samples and write them to a file
     - `reqfWrite` – generate samples and write them to a file
   - Provides a CLI with:
     - `acquire` – read from a device/file and record to `capture.bin`
     - `generate` – synthesize waveforms to an output file
     - `run` – execute commands from a JSON script (UI macro for Homework 6)

2. **Multi-Threaded Scope (`scope_mt`)**

   - Demonstrates a multi-threaded scope for Homework 9.
   - Uses the **computer’s microphone as the input device** (instead of an FTDI).
   - Periodically reads audio samples from the mic in a background thread and prints them to the terminal.

---

## 2. Setup (Virtual Environment & Dependencies)

From the **inner** project folder (the one that contains `requirements.txt` and `scope_mt`):

```bash
# Create a virtual environment
python -m venv .venv

# Activate it
# Windows:
.\.venv\Scripts\activate
# macOS / Linux:
# source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
