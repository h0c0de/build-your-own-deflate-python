# CATATAN — Build 23: DEFLATE + zlib

Satu halaman per irisan: konsep inti + temuan.
Wasit seluruh build: zlib asli secara diferensial
dua arah (796 pemeriksaan + 120 aliran acak ekstra).

## Irisan 1 — Bit I/O, blok stored, bungkus zlib (544)

**Konsep.** DEFLATE adalah format *bit*, bukan byte:
header blok 3 bit, kode Huffman berpanjang variabel,
dan hanya blok stored yang peduli batas byte (ia
menyelaraskan diri, lalu LEN/NLEN 16-bit little-endian
yang saling berkomplemen). Bungkus zlib membungkus
aliran mentah dengan CMF/FLG — pasangan byte yang
jumlah tertimbang mod-31-nya nol (FCHECK) — dan ekor
Adler-32 big-endian dari data asli.

**Temuan.** Adler-32 dan CRC-32 ditulis dari
definisinya dan dicocokkan ke `zlib.adler32` /
`binascii.crc32` pada semua korpora sebelum dipercaya
— checksum yang salah akan menutupi bug dekompresi
sebagai "data rusak". Blok stored di atas 65535 byte
wajib dipecah; korpora 70–100 KiB memastikan batas
itu terlewati dalam uji, bukan dalam produksi.

## Irisan 2 — Inflate Huffman tetap (33)

**Konsep.** Blok BTYPE=01 memakai tabel panjang yang
sudah ditetapkan standar: literal 0–143 berpanjang 8,
144–255 berpanjang 9, 256–279 berpanjang 7, 280–287
berpanjang 8; jarak semuanya 5. Dekode berjalan
simbol demi simbol: literal disalin, 256 mengakhiri
blok, 257–285 adalah kode length yang diikuti kode
jarak — pasangan itu menyalin dari keluaran yang
sudah ada, dan boleh tumpang tindih (jarak 1 =
pengulangan byte terakhir).

**Temuan.** Percobaan pertama gagal sebelum satu
simbol pun terdekode: validasi kelengkapan kodeku
menolak alfabet jarak tetap. Sebabnya hal yang
terdengar sepele — §3.2.6 mendefinisikan **32** kode
jarak 5-bit, bukan 30. Kode 30–31 memang tidak pernah
dipakai aliran sah (dan dekoder tetap menolaknya
bila muncul sebagai *simbol jarak terpakai*), tetapi
panjang mereka ikut menghitung kelengkapan kode.
Validasi Kraft-ku sendiri yang menangkapnya —
gerbang yang baik memang harus bisa menolak kode
buatan pembuatnya.

## Irisan 3 — Inflate Huffman dinamis (143)

**Konsep.** Blok BTYPE=10 mengirim tabelnya sendiri:
HLIT/HDIST/HCLEN, lalu panjang untuk alfabet
panjang-kode dalam urutan transmisi khusus RFC
(16,17,18,0,8,…), lalu daftar panjang literal+jarak
yang di-RLE dengan simbol 16 (salin sebelumnya 3–6),
17 (nol 3–10), dan 18 (nol 11–138). Dua tingkat
kompresi meta ini yang membuat header dinamis murah.

**Temuan.** zlib punya kekhasan yang didokumentasikan
di perilaku, bukan di RFC: blok yang tidak memakai
rujukan sama sekali dapat membawa alfabet jarak
"tak lengkap" berisi tepat satu kode — dekoder yang
menolak semua kode tak lengkap akan gagal pada
aliran zlib yang sah. Aturan yang benar: tak lengkap
hanya boleh bila tepat satu simbol terpakai. Uji
strategi Z_RLE/Z_FILTERED/Z_HUFFMAN_ONLY ditambahkan
karena tiap strategi membentuk header dinamis dengan
profil berbeda.

## Irisan 4 — Kompresor: LZ77 + blok tetap (36)

**Konsep.** Tokenisasi memakai rantai hash 3-byte:
tiap posisi mengingat posisi sebelumnya dengan hash
yang sama, dan pencarian berjalan mundur menyusuri
rantai (maks 128 probe, berhenti di tepi jendela
32768). Evaluasi lazy satu langkah — bandingkan
kecocokan di posisi ini dengan posisi berikutnya,
ambil yang lebih panjang — menaikkan rasio terasa
dengan biaya kecil. Karena data asli utuh di memori,
panjang kecocokan dibandingkan langsung pada data
asli; semantik timpa-diri hanya urusan dekoder.

**Temuan.** Bukti LZ77 bekerja bukanlah "round-trip
lulus" — stored yang menyamar juga lulus. Pagarnya
adalah rasio: teks 16 KiB harus menyusut di bawah
sepertiganya dan 100 KiB nol di bawah 2 KiB. Data
acak 70 KiB dipagari dari sisi lain: keluaran tidak
boleh meledak melebihi stored + 64 byte.

## Irisan 5 — Kompresor dinamis + gzip + final (40)

**Konsep.** Panjang kode optimal terbatas 15 bit
dibangun dengan **package-merge**: daftar paket
berbobot digabung berpasangan sebanyak batas kali,
dan 2n−2 entri pertama menentukan kedalaman tiap
simbol — optimal terbukti, tanpa penyesuaian luapan
ala pohon yang sulit dibuktikan. Header dinamis
menulis HLIT/HDIST yang sudah dipangkas nol-ekornya
dan RLE panjang gabungan. Ketiga bentuk blok
(stored/tetap/dinamis) dibangun utuh dan yang
terkecil yang dikirim — keputusan berdasarkan ukuran
nyata, bukan heuristik.

**Temuan.** gzip menambah dua jebakan kecil: CRC-32
dan ISIZE disimpan little-endian (kebalikan Adler
zlib yang big-endian), dan header gzip Python menulis
FLG=0 hanya bila tanpa nama berkas — pembaca di sini
menolak flag lain secara eksplisit daripada menebak.
Kasus galat final membuktikan sisi negatifnya juga:
Adler rusak, FCHECK rusak, aliran terpotong,
BTYPE=11, dan jarak yang menunjuk sebelum awal
keluaran semuanya ditolak dengan pengecualian, tidak
ada yang bocor sebagai data setengah jadi.
