import argparse
from .reader import Reader
from .writer import Writer
# from .file_device import FileDevice
from .ftdi_device import FtdiDevice
from .wavegen import Wave


def main():
    p = argparse.ArgumentParser(
        prog="oscifgen", description="Oscilloscope & Function Generator (Python)")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser(
        "acquire", help="Read N bytes at Fs from input and write to output file")
    a.add_argument("--in", required=True, dest="in_path")
    a.add_argument("--out", required=True, dest="out_path")
    a.add_argument("--n", required=True, type=int, dest="n")
    a.add_argument("--fs", required=True, type=float, dest="fs")

    g = sub.add_parser(
        "generate", help="Generate N waveform bytes at Fo and write to output file")
    g.add_argument("--out", required=True, dest="out_path")
    g.add_argument("--n", required=True, type=int, dest="n")
    g.add_argument("--fo", required=True, type=float, dest="fo")
    g.add_argument("--wave", choices=["sine",
                   "square", "triangle"], default="sine")
    g.add_argument("--amp", type=float, default=1.0)

    args = p.parse_args()

    # dev = FileDevice()  # swap to FTDI backend later
    # if args.cmd == "acquire":
    #     Reader().run(dev, args.in_path, args.n, args.fs, args.out_path)
    # else:
    #     w = {"sine":Wave.SINE, "square":Wave.SQUARE, "triangle":Wave.TRIANGLE}[args.wave]
    #     Writer().run(dev, args.out_path, args.n, args.fo, w, args.amp)

    # dev = FileDevice()
    dev = FtdiDevice()
    dev.open('ftdi://::/1')  # or your specific FTDI URL# dev = FileDevice()
