"""Irisan 5 — kompresor dinamis + gzip + final.

Matriks diferensial penuh dua arah dan kasus galat:
Adler rusak, FCHECK gagal, aliran terpotong,
BTYPE=11, jarak terlalu jauh.
"""
import gzip
import io
import zlib

import bungkus
from bit import GalatDeflate
from pampat import (dekompres, dekompres_gzip, kompres,
                    kompres_gzip)
from uji_bersama import KORPORA

cek = 0
for nama, data in KORPORA.items():
    # kita -> zlib & gzip asli, dua arah penuh
    assert zlib.decompress(kompres(data)) == data, nama
    cek += 1
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode="wb", mtime=0) as g:
        g.write(data)
    assert dekompres_gzip(buf.getvalue()) == data, nama
    cek += 1
    aliran_gz = kompres_gzip(data)
    assert gzip.decompress(aliran_gz) == data, \
        "gzip kita -> gzip asli: %s" % nama
    cek += 1
    # blok dinamis kita harus terpakai & menang pada
    # korpora besar berpola (bukan stored/tetap)
    if nama in ("teks-panjang", "campur"):
        mentah = kompres(data)[2:-4]
        btype = (mentah[0] >> 1) & 0b11
        assert btype == 2, "dinamis terpilih untuk %s" % nama
        cek += 1

# --- kasus galat: semua harus GalatDeflate ---
data = KORPORA["teks-pendek"]
baik = kompres(data)


def harus_galat(aliran, pesan):
    global cek
    cek += 1
    try:
        dekompres(aliran)
    except GalatDeflate:
        return
    raise AssertionError("tidak galat: %s" % pesan)


rusak = bytearray(baik)
rusak[-1] ^= 0xFF  # Adler-32 rusak
harus_galat(bytes(rusak), "adler")
rusak = bytearray(baik)
rusak[1] ^= 0x01   # FCHECK rusak
harus_galat(bytes(rusak), "fcheck")
harus_galat(baik[:len(baik) // 2], "terpotong")

# BTYPE=11 terlarang: byte pertama 0b111 = final + 11
harus_galat(bungkus.bungkus_zlib(b"\x07", b""), "btype11")

# jarak terlalu jauh: blok tetap berisi satu rujukan
# length 3 / jarak 100 tanpa pendahulu
from bit import PenulisBit
import huffman
import deflate as _d
penulis = PenulisBit()
penulis.tulis(1, 1)
penulis.tulis(1, 2)
kode = huffman.kode_kanonik(_d._panjang_tetap()[0])
kode_j = huffman.kode_kanonik(_d._panjang_tetap()[1])
simbol, ekstra, nbit = _d._kode_panjang(3)
k, p = kode[simbol]
penulis.tulis_kode(k, p)
simbol_j, ekstra_j, nbit_j = _d._kode_jarak(100)
k, p = kode_j[simbol_j]
penulis.tulis_kode(k, p)
k, p = kode[256]
penulis.tulis_kode(k, p)
harus_galat(bungkus.bungkus_zlib(penulis.hasil(), b""),
            "jarak jauh")
print("irisan 5: %d cek LULUS" % cek)
