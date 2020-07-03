from autosub import add_subs, get_langs
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("video", help="Video to subtitle")
parser.add_argument("--lang", "-l", help="Languages to subtitle", action="store", nargs="+", default=["en"])
parser.add_argument("--available", "-a", action="store_true", default=False)
args = parser.parse_args()

if args.available:
    print(",".join(get_langs(args.video)))
    quit()

for l in args.lang:
    add_subs(args.video, lang=l)

