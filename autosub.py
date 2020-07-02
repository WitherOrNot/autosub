import requests
import hashlib
import os
import werkzeug
import subprocess
from pathlib import Path
from tqdm import tqdm

def get_hash(name):
    readsize = 64 * 1024
    
    with open(name, 'rb') as f:
        size = os.path.getsize(name)
        data = f.read(readsize)
        f.seek(-readsize, os.SEEK_END)
        data += f.read(readsize)
    
    return hashlib.md5(data).hexdigest()

def get_langs(vid):
    vid_hash = get_hash(vid)

    langs = requests.get(
        "http://api.thesubdb.com/",
        params={
            "action": "search",
            "hash": vid_hash
        },
        headers={
            "User-Agent": "SubDB/1.0 (Autosub/1.0; http://github.com/witherornot/autosub)"
        }
    ).text.split(",")
    
    return langs

def get_subs(vid, lang="en"):
    vid_hash = get_hash(vid)
    
    langs = get_langs(vid)

    if lang not in langs:
        raise Exception(f"Language {en} not available")
    
    sub_req = requests.get(
        "http://api.thesubdb.com/",
        params={
            "action": "download",
            "hash": vid_hash,
            "language": lang
        },
        headers={
            "User-Agent": "SubDB/1.0 (Autosub/1.0; http://github.com/witherornot/autosub)"
        }
    )
    sub_req.raise_for_status()

    filename = werkzeug.http.parse_options_header(dict(sub_req.headers)["Content-Disposition"])[1]["filename"]

    open(filename, "wb").write(sub_req.content)
    
    return filename

def ffprocess(line):
    if len(line.split()[0]) == 6:
        frame = int(line.split()[1])
    else:
        frame = int(line.split()[0].split("=")[1])

    return frame

# ffmpeg -v quiet -stats -i Good.Will.Hunting.1997.720p.@sourcemovies.mp4 -map 0:v:0 -c copy -f null -
def add_subs(vid, lang="en"):
    vid_path = Path(vid)
    print("Downloading subtitles...")
    subfile = get_subs(vid, lang=lang)
    print("Processing subtitles...")
    frames = ffprocess(subprocess.Popen(['ffmpeg', '-v', 'quiet', '-stats', '-i', vid, '-map', '0:v:0', '-c', 'copy', '-f', 'null', '-'], stderr=subprocess.PIPE).stderr.read().decode("utf-8"))
    subprocess.Popen(["ffmpeg", "-i", subfile, "temp.ass"], stderr=subprocess.DEVNULL).wait()
    print("Applying subtitles to video...")
    proc = subprocess.Popen(["ffmpeg", "-v", "quiet", "-stats", "-i", vid, "-vf", "ass=temp.ass", f"{vid_path.stem}.Subbed.{lang.upper()}{vid_path.suffix}"], stderr=subprocess.PIPE, universal_newlines=True)
    pbar = tqdm(total=frames, unit='frames')
    
    for line in proc.stderr:
        pbar.n = ffprocess(line)
        pbar.refresh()
    
    os.remove(subfile)
    os.remove("temp.ass")

