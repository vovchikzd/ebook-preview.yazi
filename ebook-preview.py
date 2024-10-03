#!/usr/bin/env python3

import os, sys, zipfile, io, base64, chardet
from lxml import etree
from PIL import Image
from math import ceil

def eprint(sToPrint: str = ""):
    print(sToPrint, file=sys.stderr)

saFormats: list[str] = [".epub", ".fb2", ".modi"]

def save_epub_cover(sFile: str, sFileTo: str, npImageHeight: int) -> int:
    '''Based on https://github.com/Alamot/code-snippets/blob/master/epub/epub-show-cover.py'''

    epubNamespacesMap = {
       "calibre":"http://calibre.kovidgoyal.net/2009/metadata",
       "dc":"http://purl.org/dc/elements/1.1/",
       "dcterms":"http://purl.org/dc/terms/",
       "opf":"http://www.idpf.org/2007/opf",
       "u":"urn:oasis:names:tc:opendocument:xmlns:container",
       "xsi":"http://www.w3.org/2001/XMLSchema-instance",
       "xhtml":"http://www.w3.org/1999/xhtml"
    }

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
            eprint("Cover image not found.")  
            return 1

        pathCover = os.path.join(os.path.dirname(pathRootfile), hrefCover)
        imageCover = Image.open(epubBook.open(pathCover))
        if npImageHeight:
            nImageSizeTuple = imageCover.size
            nMaxImageSize = max(nImageSizeTuple)
            if nMaxImageSize > npImageHeight:
                nScaleRatio = ceil(nMaxImageSize / npImageHeight)
                imageCover = imageCover.resize(
                    (nImageSizeTuple[0] // nScaleRatio, nImageSizeTuple[1] // nScaleRatio)
                    , Image.LANCZOS)
        imageCover.save(sFileTo, quality=20, optimize=True, format="PNG")
        return 0


def save_fb2_cover(sFile: str, sFileTo: str, npImageHeight: int) -> int:

    fb2NamespacesMap = {
        "xs":"http://www.gribuser.ru/xml/fictionbook/2.0"
        ,"l":"http://www.w3.org/1999/xlink"
    }

    with open(sFile, "rb") as fb2File:
        readedFile = etree.fromstring(fb2File.read())
        try:
            imageIndex = readedFile.xpath(
                "/xs:FictionBook/xs:description/xs:title-info/xs:coverpage/xs:image"
                , namespaces=fb2NamespacesMap
            )[0].get(f"{{{fb2NamespacesMap['l']}}}href")[1:]
        except IndexError:
            pass

        if imageIndex is None:
            eprint("Cover image not found")
            return 1

        try:
            imageBytes = readedFile.xpath(
                f"/xs:FictionBook/xs:binary[@id='{imageIndex}']"
                ,namespaces=fb2NamespacesMap
            )[0].text
        except IndexError:
            pass

        if imageBytes is None:
            eprint("Cover image not found")
            return 1

        imageCover = Image.open(io.BytesIO(base64.b64decode(imageBytes)))
        if npImageHeight:
            nImageSizeTuple = imageCover.size
            nMaxImageSize = max(nImageSizeTuple)
            if nMaxImageSize > npImageHeight:
                nScaleRatio = ceil(nMaxImageSize / npImageHeight)
                imageCover = imageCover.resize(
                    (nImageSizeTuple[0] // nScaleRatio, nImageSizeTuple[1] // nScaleRatio)
                    , Image.LANCZOS)
        imageCover.save(sFileTo, quality=20, optimize=True, format="PNG")
        return 0


def save_cover(sFile: str, sFileTo: str, npImageHeight: int) -> int:
    if '.' not in sFile:
        eprint(f"File '{sFile}' doesn't have format. Abort")
        return 1

    sFileExt: str = sFile[-(sFile[-1::-1].index('.') + 1):]
    if sFileExt not in saFormats:
        eprint(f"Can't recognize '{sFileExt}' format. Abort")
        return 1

    match sFileExt:
        case '.epub':
            return save_epub_cover(
                sFile = sFile
                ,sFileTo = sFileTo
                ,npImageHeight = npImageHeight)
        case '.fb2':
            return save_fb2_cover(
                sFile = sFile
                , sFileTo = sFileTo
                , npImageHeight = npImageHeight
            )
        case '.mobi':
            eprint(f"{sFileExt} format is not supported yet")
            return 1

    return 0


def extract_data(sFile: str) -> int:
    pass


def main() -> int:
    saArgs: list[str] = sys.argv
    match len(saArgs):
        case 3 if saArgs[1] == 'd':
            eprint("Data extraction is not implemented yet")
            return 1
        case 4 | 5 if saArgs[1] == 'c':
            return save_cover(
                sFile = saArgs[2]
                ,sFileTo = saArgs[3]
                ,npImageHeight = int(0 if len(saArgs) == 4 else saArgs[4]))
        case _:
            eprint("I don't know what you want")
            return 1


if __name__ == "__main__":
    sys.exit(main())
