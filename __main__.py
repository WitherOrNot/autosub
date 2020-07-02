from autosub import add_subs
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("video", help="Video to subtitle")
parser.add_argument("--lang", "-l", help="Languages to subtitle", action="store", nargs="+", default=["en"])
args = parser.parse_args()

for l in args.lang:
    add_subs(args.video, lang=l)

