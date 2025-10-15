# requirementsreadwrite

# Oscilloscope & Function Generator – Reader/Writer (requirementsreadwrite)

Implements `reqfRead` and `reqfWrite` with a file-backed mock device (no hardware needed). 
Includes a CLI test driver and hooks to verify throughput/latency requirements.

## Build
```bash
mkdir -p build && cd build
c++ -O2 -std=c++17 ../src/main.cpp ../src/reader_writer.cpp -o oscifgen
