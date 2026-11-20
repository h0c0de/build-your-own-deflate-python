"""Irisan 4 — kompresor: tokenisasi LZ77 + blok
tetap/stored. Wasit: zlib asli mendekode keluaran
kita byte-exact; rasio waras pada data berpola.
"""
import zlib

from pampat import kompres, kompres_mentah, dekompres_mentah
from uji_bersama import KORPORA

cek = 0
for nama, data in KORPORA.items():
    mentah = kompres_mentah(data)
    assert zlib.decompress(mentah, -15) == data, \
        "mentah kita -> zlib: %s" % nama
    cek += 1
    assert dekompres_mentah(mentah) == data, \
        "mentah kita -> kita: %s" % nama
    cek += 1
    assert zlib.decompress(kompres(data)) == data, \
        "zlib kita -> zlib: %s" % nama
    cek += 1

# data berpola harus benar-benar menyusut (bukti
# rujukan LZ77 bekerja, bukan stored menyamar)
teks = KORPORA["teks-panjang"]
assert len(kompres_mentah(teks)) < len(teks) // 3, "rasio teks"
cek += 1
nol = KORPORA["nol-100k"]
assert len(kompres_mentah(nol)) < 2000, "rasio nol"
cek += 1
# data acak tidak meledak lebih dari stored + header
acak = KORPORA["acak-70k"]
assert len(kompres_mentah(acak)) <= len(acak) + 64, "acak waras"
cek += 1
print("irisan 4: %d cek LULUS" % cek)
