#!/usr/bin/env python3

import sys, os, subprocess
from PIL import Image
from math import ceil

def eprint(*to_print):
    print(*to_print, file=sys.stderr)


def print_usage():
    eprint("Usage: get-ebook-cover INPUT_FILE OUTPUT_FILE MIN_SIZE")
    eprint()
    eprint("     INPUT_FILE:  ebook file")
    eprint("     OUTPUT_FILE: output image file, required when subcommand is 'c'")
    eprint("     MIN_SIZE:    min area size to fit image, required when subcommand is 'c'")


def getCover(bookFile: str, cache: str, minAreaSize: int) -> int:
    cacheTmp: str = f"{cache}.tmp"
    subprocess.run(["ebook-meta", f"--get-cover={cacheTmp}", bookFile], capture_output=True)
    imageCover = Image.open(cacheTmp)
    imageSizeTuple = imageCover.size
    maxImageSize = max(imageSizeTuple)
    if maxImageSize > minAreaSize:
        scaleRatio = ceil(maxImageSize / minAreaSize)
        imageCover = imageCover.resize(
            (imageSizeTuple[0] // scaleRatio, imageSizeTuple[1] // scaleRatio)
            , Image.LANCZOS
        )
    imageCover.save(cache, quality=20, optimize=True, format="PNG")
    os.remove(cacheTmp)


def main() -> int:
    args: list[str] = sys.argv[1:]
    if len(args) != 3:
        print_usage()
        return 1
    getCover(args[0], args[1], int(args[2]))
    return 0

if __name__ == "__main__":
    sys.exit(main())
