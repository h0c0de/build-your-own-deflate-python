"""Korpora & pembantu uji bersama untuk build 23.

Wasitnya zlib asli: `zlib`/`gzip` dari pustaka standar.
Korpora dipilih untuk menyentuh tepi-tepi format:
kosong, satu byte, semua nilai byte, acak murni (tak
termampatkan), nol panjang, dan pola berjarak tepat
32 KiB — tepi jendela geser.
"""

import os
import random

_teks = (
    "Kompresi data tanpa kehilangan memakai dua ide: "
    "pengulangan dirujuk, bukan disalin, dan simbol "
    "yang sering muncul diberi kode yang pendek. "
    "DEFLATE menggabungkan LZ77 dengan kode Huffman, "
    "dan dunia memakainya di dalam zlib, gzip, ZIP, "
    "PNG, dan HTTP setiap hari. ").encode("utf-8")


def _pola_jendela():
    # segmen 4 KiB yang muncul lagi tepat 32768 byte
    # sesudah awal kemunculan pertamanya
    segmen = bytes(random.Random(7).randrange(256)
                   for _ in range(4096))
    pengisi = bytes(random.Random(8).randrange(256)
                    for _ in range(32768 - 4096))
    return segmen + pengisi + segmen


KORPORA = {
    "kosong": b"",
    "satu-byte": b"a",
    "teks-pendek": b"halo halo halo, dunia!",
    "teks-panjang": _teks * 60,
    "semua-byte": bytes(range(256)) * 40,
    "acak-1k": random.Random(42).randbytes(1000),
    "acak-70k": random.Random(43).randbytes(70000),
    "nol-100k": bytes(100000),
    "run-aa": b"a" * 50000,
    "pola-jendela": _pola_jendela(),
    "campur": (_teks * 20) + random.Random(9).randbytes(3000)
              + bytes(20000) + (_teks * 20),
}
