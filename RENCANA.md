# RENCANA — Build 23: DEFLATE + zlib

Sumber: **RFC 1951** (DEFLATE Compressed Data Format
Specification v1.3, P. Deutsch, Mei 1996) + **RFC 1950**
(format data zlib). Standarnya sendiri adalah panduan,
seperti FIPS-197 di build 20 dan spek CommonMark di
build 22. RFC bersifat publik; teksnya tidak disertakan
di repo ini.

Wasit: **zlib asli** (modul `zlib`/`gzip` Python di atas
libz sistem) secara diferensial dua arah — aliran yang
dihasilkan zlib pada semua level & strategi harus
terdekode byte-exact oleh dekompresor build ini, dan
aliran yang dihasilkan kompresor build ini harus
terdekode byte-exact oleh zlib. Tidak ada keluaran
kompresi "yang benar" tunggal, jadi kesetaraan yang
dituntut adalah *round-trip*, bukan byte-identik.

## Lingkup

MASUK:
- Pembaca/penulis bit LSB-first; kode Huffman kanonik
  sesuai §3.2.2 RFC 1951.
- Inflate lengkap: blok stored (BTYPE=00), Huffman
  tetap (01), Huffman dinamis (10) — header
  HLIT/HDIST/HCLEN, alfabet panjang-kode dengan
  urutan transmisi RFC, simbol ulangan 16/17/18.
- Kode panjang/jarak §3.2.5 beserta bit ekstra.
- Bungkus zlib (RFC 1950): cek header FCHECK, tanpa
  kamus, Adler-32 diverifikasi. Bungkus gzip:
  header, CRC-32, ISIZE.
- Kompresor: tokenisasi LZ77 (rantai hash, pencocokan
  greedy + lazy satu langkah, jendela 32 KiB, panjang
  3–258), pohon Huffman terbatas-panjang 15 bit
  (package-merge), pilihan blok stored/tetap/dinamis
  berdasarkan ukuran terkecil, RLE panjang kode
  untuk header dinamis.

DILUAR (tercatat):
- Kompresi streaming/chunked API (seluruh data di
  memori; blok dipecah per potongan masukan).
- Kamus preset (FDICT) — ditolak saat membaca,
  tidak pernah ditulis.
- Optimasi kecepatan: dekode bit-per-bit yang jernih
  lebih diutamakan daripada tabel akselerasi.

## Irisan

- [x] Irisan 1 — Bit I/O + blok stored + bungkus zlib
  (Adler-32). Wasit: aliran level-0 zlib.
- [x] Irisan 2 — Inflate Huffman tetap (BTYPE=01).
  Wasit: strategi Z_FIXED zlib lintas korpora.
- [x] Irisan 3 — Inflate Huffman dinamis (BTYPE=10) +
  bungkus gzip baca. Wasit: level 1–9 zlib.
- [x] Irisan 4 — Kompresor: tokenisasi LZ77 + blok
  tetap/stored. Wasit: zlib mendekode keluaran kita;
  rasio waras pada teks.
- [x] Irisan 5 — Kompresor dinamis + tulis gzip +
  final: matriks diferensial penuh dua arah +
  kasus galat (Adler rusak, aliran terpotong,
  BTYPE=11, jarak terlalu jauh).

## Pagar selesai

- [x] `uji_irisan1.py` … `uji_irisan5.py` hijau.
- [x] `CATATAN.md` satu halaman per irisan.
- [x] Repo GitHub publik
  `build-your-own-deflate-python` terbit dan
  terverifikasi (SHA blob lokal == remote, halaman
  publik terbaca).
