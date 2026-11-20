# Build Your Own — DEFLATE + zlib

Implementasi lengkap **DEFLATE** (RFC 1951) beserta
bungkus **zlib** (RFC 1950) dan **gzip** (RFC 1952)
dalam Python murni: dekompresor untuk ketiga jenis
blok (stored, Huffman tetap, Huffman dinamis) dan
kompresor LZ77 + Huffman dinamis sendiri.

Standarnya adalah panduannya — tidak ada tutorial.
Wasitnya adalah **zlib asli**: setiap aliran yang
dihasilkan zlib pada level 1–9 dan semua strategi
harus terdekode byte-exact di sini, dan setiap aliran
yang dihasilkan kompresor di sini harus terdekode
byte-exact oleh zlib. Total **796 pemeriksaan**
diferensial dua arah, semuanya hijau.

## Isi

| Berkas | Isi |
| --- | --- |
| `bit.py` | Pembaca/penulis bit LSB-first; kode Huffman ditulis MSB-first |
| `huffman.py` | Kode kanonik dari panjang kode (§3.2.2) + package-merge untuk panjang optimal terbatas 15 bit |
| `deflate.py` | Inflate ketiga BTYPE + kompresor (tokenisasi LZ77 rantai hash, pilihan blok stored/tetap/dinamis termurah) |
| `bungkus.py` | Format zlib & gzip; Adler-32 dan CRC-32 ditulis dari definisinya |
| `pampat.py` | Titik masuk: `kompres`, `dekompres`, varian `*_mentah` dan `*_gzip` |
| `uji_bersama.py` | Korpora uji (termasuk pola berjarak tepat 32 KiB — tepi jendela) |
| `uji_irisan1.py` … `uji_irisan5.py` | Uji per irisan melawan zlib asli |

## Memakai

```python
from pampat import kompres, dekompres

aliran = kompres(b"halo halo halo, dunia!")
assert dekompres(aliran) == b"halo halo halo, dunia!"

import zlib
assert zlib.decompress(aliran) == b"halo halo halo, dunia!"
```

## Tiga ide yang membuatnya bekerja

1. **Kode Huffman adalah daftar panjangnya.**
   Pengirim tidak pernah mengirim pohon — hanya
   panjang kode tiap simbol; kode kanonik dibangun
   ulang secara identik di kedua sisi dari daftar
   itu. Blok dinamis bahkan mengirim panjang-panjang
   itu sendiri dalam keadaan terkompresi (alfabet
   panjang-kode + simbol ulangan 16/17/18).

2. **Dua arah bit yang berlawanan.** Elemen data
   dikemas LSB-first, tetapi kode Huffman dikemas
   MSB-first. Mencampur keduanya menghasilkan aliran
   yang tampak acak dan tidak terdekode sama sekali —
   bug nomor satu di implementasi DEFLATE mana pun.

3. **Salinan boleh menimpa dirinya.** Pasangan
   length-distance dengan jarak 1 dan panjang 258
   adalah cara DEFLATE mengenkode run: penyalinan
   berjalan byte demi byte dari keluaran yang sedang
   tumbuh. Di sisi kompresor, sifat yang sama membuat
   pencocokan bisa dibandingkan langsung pada data
   asli yang sudah utuh.

## Temuan paling menarik

Alfabet jarak tetap tampak "kurang" — 30 kode
berpanjang 5 menjumlah ke 30/32, bukan kode lengkap.
RFC §3.2.6 ternyata mendefinisikan **32** kode jarak
5-bit; simbol 30–31 tidak pernah muncul dalam aliran
yang sah, tetapi panjangnya terdefinisi, dan tanpa
keduanya kode tetapnya bukan kode yang sah. Pelajaran
lamanya berulang: baca definisinya kata per kata.
Detail lain — package-merge vs penyesuaian luapan,
RLE untuk header dinamis, kapan blok stored menang —
ada di `CATATAN.md`.

## Lisensi

Kode: MIT. RFC 1950/1951/1952 © IETF, teksnya tidak
disertakan di repo ini.
