"""Irisan 3 — inflate Huffman dinamis (BTYPE=10) + gzip.

Wasit: zlib level 1-9 strategi bawaan (blok dinamis
untuk data yang cukup besar/berpola) dan modul gzip.
"""
import gzip
import io
import zlib

from pampat import dekompres, dekompres_gzip
from uji_bersama import KORPORA

cek = 0
for nama, data in KORPORA.items():
    for level in (1, 2, 3, 4, 5, 6, 7, 8, 9):
        aliran = zlib.compress(data, level)
        assert dekompres(aliran) == data, \
            "dinamis %s level %d" % (nama, level)
        cek += 1
    # strategi lain yang juga menghasilkan blok dinamis
    for strategi in (zlib.Z_RLE, zlib.Z_FILTERED,
                     zlib.Z_HUFFMAN_ONLY):
        co = zlib.compressobj(6, zlib.DEFLATED, 15, 8, strategi)
        aliran = co.compress(data) + co.flush()
        assert dekompres(aliran) == data, \
            "strategi %s %s" % (nama, strategi)
        cek += 1
    # gzip asli dibaca bungkus kita
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as g:
        g.write(data)
    assert dekompres_gzip(buf.getvalue()) == data, \
        "gzip %s" % nama
    cek += 1
print("irisan 3: %d cek LULUS" % cek)
