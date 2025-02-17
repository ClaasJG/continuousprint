import re
import sys
from continuousprint.data import PRINTER_PROFILES


def _strip_nonalpha(s: str):
    assert type(s) is str
    return re.sub("[^0-9a-zA-Z]+", " ", s)


PROFILES = list(PRINTER_PROFILES.keys())
CANDIDATES = [
    set(_strip_nonalpha(k).split()).union(
        set(PRINTER_PROFILES[k].get("extra_tags", []))
    )
    for k in PROFILES
]


class KiriMotoProcessor:
    @classmethod
    def header_match(self, hdr):
        for line in hdr:
            if line.startswith("; Generated by Kiri:Moto"):
                return True
        return False

    @classmethod
    def get_profile(self, hdr) -> str:
        for line in hdr:
            if line.startswith("; Target:"):
                return re.match("; Target: (.*)", line)[1]
        return ""


def token_string_match(profstr):
    # Remove non-alpha characters from profile string
    # Convert all into bag-of-words
    p = set(_strip_nonalpha(profstr).split())

    scores = [len(p.intersection(c)) for c in CANDIDATES]
    sys.stderr.write(f"Scoring '{profstr}':\n")
    desc = sorted(zip(PROFILES, scores), key=lambda x: x[1], reverse=True)
    for p, s in desc[:4]:
        if s == 0:
            continue
        sys.stderr.write(f"- {p}: {s}\n")
    sys.stderr.write("- ...\n")
    max_score = max(scores)
    if max_score < 2:
        return None
    max_index = scores.index(max_score)
    return PROFILES[max_index]


PROCESSORS = [
    (cls.__name__, cls.header_match, cls.get_profile) for cls in [KiriMotoProcessor]
]


def get_header(path: str):
    hdr = []
    with open(path) as f:
        for line in f:
            if re.match("^G[012] .*", line):
                return hdr
            hdr.append(line)
    return hdr


def get_profile(hdr: list):
    for name, hdr_match, getprof in PROCESSORS:
        if hdr_match(hdr):
            sys.stderr.write(f"File matched with {name}\n")
            profstr = getprof(hdr)
            return token_string_match(profstr)


if __name__ == "__main__":
    sys.stderr.write("=== Continuous Print Profile Inference ===\n")
    hdr = get_header(sys.argv[1])
    prof = get_profile(hdr)
    if prof is not None:
        sys.stdout.write(prof)
    sys.stdout.flush()
    sys.stderr.write("\n=== End Inference ===\n")
