"""Irisan 1 — bit I/O, blok stored, bungkus zlib.

Wasit: zlib asli pada level 0 (blok stored murni),
termasuk batas 65535/65536 byte LEN, dan checksum
Adler-32/CRC-32 dibandingkan dengan binascii.
"""
import binascii
import zlib

import bungkus
from bit import PembacaBit, PenulisBit
from pampat import dekompres
from uji_bersama import KORPORA

cek = 0


def periksa(kondisi, pesan):
    global cek
    cek += 1
    assert kondisi, pesan


# bit I/O bolak-balik pada lebar acak
import random
acak = random.Random(1)
tulis = PenulisBit()
nilai = []
for _ in range(500):
    lebar = acak.randrange(1, 17)
    v = acak.randrange(1 << lebar)
    nilai.append((v, lebar))
    tulis.tulis(v, lebar)
baca = PembacaBit(tulis.hasil())
for v, lebar in nilai:
    periksa(baca.baca(lebar) == v, "bit io lebar %d" % lebar)

# checksum melawan binascii
for nama, data in KORPORA.items():
    periksa(bungkus.adler32(data) == zlib.adler32(data),
            "adler %s" % nama)
    periksa(bungkus.crc32(data) == binascii.crc32(data),
            "crc %s" % nama)

# aliran stored zlib (level 0) terdekode byte-exact,
# termasuk korpora di atas 65535 byte
for nama, data in KORPORA.items():
    aliran = zlib.compress(data, 0)
    periksa(dekompres(aliran) == data, "stored %s" % nama)
    # dan bungkus kita sendiri terbaca zlib
    mentah = zlib.compressobj(0, zlib.DEFLATED, -15)
    mentah = mentah.compress(data) + mentah.flush()
    periksa(zlib.decompress(bungkus.bungkus_zlib(mentah, data)) == data,
            "bungkus kita %s" % nama)

print("irisan 1: %d cek LULUS" % cek)
