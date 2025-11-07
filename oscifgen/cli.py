import argparse
from .reader import Reader
from .writer import Writer
from .ftdi_device import FtdiDevice
from .wavegen import Wave

def main():
    p = argparse.ArgumentParser(
        prog="oscifgen", description="Oscilloscope & Function Generator (Python)")
    sub = p.add_subparsers(dest="cmd", required=True)

    # Acquire (read)
    a = sub.add_parser(
        "acquire", help="Read bytes from input device and write to output file")
    a.add_argument("--in", required=True, dest="in_path")
    a.add_argument("--out", required=True, dest="out_path")
    a.add_argument("--fs", required=True, type=float, dest="fs",
                   help="sample rate (Hz) for pacing")
    a.add_argument("--n", type=int, dest="n",
                   help="target bytes/samples to collect (optional)")
    a.add_argument("--loops", type=int, dest="loops",
                   help="max loop iterations/chunks (optional)")
    a.add_argument("--chunk", type=int, default=512,
                   help="bytes per read (default: 512)")

    # Generate (write)
    g = sub.add_parser(
        "generate", help="Generate waveform bytes at Fo and write to output file")
    g.add_argument("--out", required=True, dest="out_path")
    g.add_argument("--fo", required=True, type=float, dest="fo",
                   help="output rate (Hz) for pacing")
    g.add_argument("--n", type=int, dest="n",
                   help="target bytes/samples to generate (optional)")
    g.add_argument("--loops", type=int, dest="loops",
                   help="max loop iterations/chunks (optional)")
    g.add_argument("--chunk", type=int, default=512,
                   help="bytes per write (default: 512)")
    g.add_argument("--wave", choices=["sine", "square", "triangle"], default="sine")
    g.add_argument("--amp", type=float, default=1.0)

    args = p.parse_args()

    # Require at least one termination condition (N or loops) for both modes
    if args.cmd in ("acquire", "generate") and (args.n is None and args.loops is None):
        raise SystemExit("Provide --n or --loops (or both). Example: --n 8192 or --loops 100")

    # Device selection (FTDI for real hardware)
    dev = FtdiDevice()
    dev.open('ftdi://::/1')  # TODO: replace with your exact FTDI URL if needed

    if args.cmd == "acquire":
        Reader().run(
            dev=dev,
            in_path=args.in_path,
            out_path=args.out_path,
            fs=args.fs,
            n=args.n,
            loops=args.loops,
            chunk=args.chunk
        )
    else:
        w = {"sine": Wave.SINE, "square": Wave.SQUARE, "triangle": Wave.TRIANGLE}[args.wave]
        Writer().run(
            dev=dev,
            out_path=args.out_path,
            fo=args.fo,
            wave=w,
            amp=args.amp,
            n=args.n,
            loops=args.loops,
            chunk=args.chunk
        )

