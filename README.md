# requirementsreadwrite

# Oscilloscope & Function Generator – Python (reqfRead / reqfWrite)

Implements `reqfRead` and `reqfWrite` in Python with a file-backed mock device.
CLI supports **acquire** and **generate**; prints bytes, duration, throughput, and latency percentiles (read).

## Setup
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
