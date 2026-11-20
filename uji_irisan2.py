"""Irisan 2 — inflate Huffman tetap (BTYPE=01).

Wasit: zlib dengan strategi Z_FIXED pada semua level
kompresi, lintas korpora.
"""
import zlib

from pampat import dekompres
from uji_bersama import KORPORA

cek = 0
for nama, data in KORPORA.items():
    for level in (1, 6, 9):
        co = zlib.compressobj(level, zlib.DEFLATED, 15, 8,
                              zlib.Z_FIXED)
        aliran = co.compress(data) + co.flush()
        hasil = dekompres(aliran)
        assert hasil == data, "tetap %s level %d" % (nama, level)
        cek += 1
print("irisan 2: %d cek LULUS" % cek)
