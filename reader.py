#!/usr/bin/env python3

import os, sys, zipfile
from lxml import etree
from PIL import Image

saFormats: list[str] = [".epub", ".fb2", ".modi"]
epubNamespacesMap = {
   "calibre":"http://calibre.kovidgoyal.net/2009/metadata",
   "dc":"http://purl.org/dc/elements/1.1/",
   "dcterms":"http://purl.org/dc/terms/",
   "opf":"http://www.idpf.org/2007/opf",
   "u":"urn:oasis:names:tc:opendocument:xmlns:container",
   "xsi":"http://www.w3.org/2001/XMLSchema-instance",
   "xhtml":"http://www.w3.org/1999/xhtml"
}

def save_epub_cover(sFile: str, sFileTo: str) -> int:
    '''Based on https://github.com/Alamot/code-snippets/blob/master/epub/epub-show-cover.py'''
    with zipfile.ZipFile(sFile) as epubBook:
        readedFromArchive = etree.fromstring(epubBook.read("META-INF/container.xml"))
        pathRootfile =  readedFromArchive.xpath(
            "/u:container/u:rootfiles/u:rootfile"
            , namespaces=epubNamespacesMap
        )[0].get("full-path")
        readedFromArchive = etree.fromstring(epubBook.read(pathRootfile))

        hrefCover = None
        try:
            idCover = readedFromArchive.xpath(
                "//opf:metadata/opf:meta[@name='cover']"
                , namespaces=epubNamespacesMap
            )[0].get("content")

            hrefCover = readedFromArchive.xpath(
                f"//opf:manifest/opf:item[@id='{idCover}']"
                , namespaces=epubNamespacesMap
            )[0].get("href")
        except IndexError:
            pass
        
        if not hrefCover:
            try:
                hrefCover = readedFromArchive.xpath(
                    "//opf:manifest/opf:item[@properties='cover-image']"
                    , namespaces=epubNamespacesMap
                )[0].get("href")
            except IndexError:
                pass

        if not hrefCover:
            try:
                idPadeCover = readedFromArchive.xpath(
                    "//opf:spine/opf:itemref"
                    , namespaces=epubNamespacesMap
                )[0].get("idref")

                hrefPageCover = readedFromArchive.xpath(
                    f"//opf:manifest/opf:item[@id='{idPadeCover}']"
                    , namespaces=epubNamespacesMap
                )[0].get("href")

                pathPageCover = os.path.join(os.path.dirname(pathRootfile), hrefPageCover)
                readedFromArchive = etree.fromstring(epubBook.read(pathPageCover))              
                hrefCover = readedFromArchive.xpath(
                    "//xhtml:img"
                    , namespaces=epubNamespacesMap
                )[0].get("src")
            except IndexError:
                pass

        if not hrefCover:
            print("Cover image not found.")  
            return 1
        pathCover = os.path.join(os.path.dirname(pathRootfile), hrefCover)
        Image.open(epubBook.open(pathCover)).save(sFileTo)
        return 0



def save_cover(sFile: str, sFileTo: str) -> int:
    if '.' not in sFile:
        print(f"Can't find extension of \'{sFile}\'", file=sys.stderr)
        return 1

    sFileExt: str = sFile[-(sFile[-1::-1].index('.') + 1):]
    if sFileExt not in saFormats:
        print(f"Can't recognize extension of \'{sFile}\'", file=sys.stderr)
        return 1

    match sFileExt:
        case '.epub':
            return save_epub_cover(sFile, sFileTo)
        case '.fb2' | '.mobi':
            print(f"{sFileExt} format not supported yet", file=sys.stderr)

    return 0


def main() -> int:
    saArgs: list[str] = sys.argv
    match len(saArgs):
        case 3 if saArgs[1] == 'd':
            print("Not implemented yet", file=sys.stderr)
            return 1
        case 4 if saArgs[1] == 'c':
            return save_cover(saArgs[2], saArgs[3])
        case _:
            return 1


if __name__ == "__main__":
    sys.exit(main())
