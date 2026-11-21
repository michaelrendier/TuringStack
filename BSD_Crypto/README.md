# BSD Crypto — every encryption algorithm in the most recent BSD

Collected 2026-11-21 for the TuringStack. **Target: FreeBSD 15.1** (`releng/15.1`, tip `bb03631fe3b7`, 2026-11-13; latest release tag `release/15.1.0-p7`). FreeBSD is the BSD with the largest shipped cryptographic surface: OpenBSD ships LibreSSL and its own `libc` crypto; NetBSD and DragonFly carry subsets or older forks. This collection is the FreeBSD base system plus its `security/` ports category.

All of it is read from source by `collect_bsd_crypto.py` (re-runnable; inputs are a sparse FreeBSD checkout and the ports `INDEX-15`). Nothing here is hand-typed except the per-component notes.

## What is in this directory
| file | content |
|---|---|
| `algorithms.csv` | 610 rows (component, kind, algorithm, source path); 522 distinct names |
| `security_ports_15.csv` | all 1713 ports in `security/` (FreeBSD 15 INDEX); 912 flagged `crypto_related` by keyword |
| `summary.json` | counts by component and kind |
| `collect_bsd_crypto.py` | the collector |

## The base system, by component (rows)
- **OpenSSL 3 default provider**: 296
- **OpenSSH**: 79
- **OpenSSL 3 legacy provider**: 43
- **opencrypto(9)**: 43
- **libecc**: 32
- **MIT krb5**: 24
- **sys/crypto**: 20
- **Heimdal krb5**: 18
- **opencrypto(9) xforms**: 13
- **geli(8)**: 9
- **kernel-driver**: 7
- **libcrypt**: 6
- **IPsec/PF_KEY**: 5
- **OpenZFS ICP**: 5
- **base contrib**: 5
- **libmd**: 4
- **libsecureboot**: 1

## Where the algorithms live
- **Kernel, `opencrypto(9)`** (`sys/opencrypto/cryptodev.h`): DES, 3DES, Blowfish, CAST, Skipjack, AES-CBC/ICM(CTR)/XTS/GCM/CCM/GMAC, Camellia-CBC, ChaCha20, ChaCha20-Poly1305, XChaCha20-Poly1305, ARC4, null, MD5/SHA-1/SHA-2/RIPEMD-160/BLAKE2 and their HMACs, Poly1305, deflate. Software in `sys/crypto/{aesni,armv8,blake2,camellia,chacha20,des,rc4,rijndael,sha2,siphash,skein,openssl}`; hardware drivers: AES-NI, VIA PadLock, AMD Geode, CCP, Intel QAT, SafeXcel, CESA, ARMv8.
- **geli(8)** disk encryption: AES-CBC, AES-XTS, CAMELLIA-CBC, NULL-CBC, RIPEMD160-HMAC, SHA1-HMAC, SHA2-256-HMAC, SHA2-384-HMAC, SHA2-512-HMAC.
- **IPsec** (`sys/netipsec`, PF_KEY): SADB_AALG_MD5HMAC, SADB_AALG_SHA1HMAC, SADB_EALG_3DESCBC, SADB_EALG_DESCBC, SADB_EALG_NULL plus everything opencrypto(9) offers through the ESP/AH transforms.
- **WireGuard** (`sys/dev/wg`): X25519, ChaCha20-Poly1305, BLAKE2s, HMAC-BLAKE2s.
- **Random** (`sys/dev/random`): Fortuna (AES-256 counter mode + SHA-256), ChaCha20 (Fenestras X), RDRAND/RDSEED/DARN hardware sources.
- **OpenZFS ICP**: AES-CCM/GCM, SHA-2, Skein, BLAKE3, Edon-R.
- **OpenSSL 3.x** (`crypto/openssl`): default provider — 141 ciphers, 52 digests, 26 MACs, 16 KDFs, 69 signature names, key exchange DH, ECDH, HKDF, SCRYPT, TLS1-PRF, X25519, X448, KEMs EC, ML-KEM-1024, ML-KEM-512, ML-KEM-768, RSA, X25519, X448. Legacy provider: BF-CBC, BF-CFB, BF-ECB, BF-OFB, CAST5-CBC, CAST5-CFB, CAST5-ECB, CAST5-OFB, DES-CBC, DES-CFB, DES-CFB1, DES-CFB8, DES-ECB, DES-OFB, DESX-CBC, IDEA-CBC, IDEA-CFB, IDEA-ECB, IDEA-OFB, MD2, MD4, MDC2, PBKDF1, PVKKDF, RC2-40-CBC, RC2-64-CBC, RC2-CBC, RC2-CFB, RC2-ECB, RC2-OFB, RC4, RC4-40, RC4-HMAC-MD5, RC5-CBC, RC5-CFB, RC5-ECB, RC5-OFB, RIPEMD-160, SEED-CBC, SEED-CFB, SEED-ECB, SEED-OFB, WHIRLPOOL.
- **OpenSSH**: ciphers 3des-cbc, aes128-cbc, aes128-ctr, aes128-gcm@openssh.com, aes192-cbc, aes192-ctr, aes256-cbc, aes256-ctr, aes256-gcm@openssh.com, chacha20-poly1305@openssh.com, none; key exchange 15 names (DH groups, ECDH, curve25519, sntrup761x25519, mlkem768x25519); MACs 16; host/user key types 22 incl. certificates, FIDO `sk-` and XMSS.
- **Kerberos 5** (MIT krb5 + Heimdal): AES-CTS-HMAC-SHA1/SHA2, Camellia-CMAC, 3DES, RC4-HMAC (and export variants).
- **libecc** (`secure/lib/libpkgecc`): signature schemes bign, bip0340, dbign, decdsa, ecdsa, ecfsdsa, ecgdsa, eckcdsa, ecosdsa, ecrdsa, ecsdsa, eddsa, sm2; hashes incl. SHA-3, SHAKE, SM3, Streebog, BelT, BASH, RIPEMD-160; named curves under `crypto/libecc/include/libecc/curves/known/`.
- **libcrypt / libmd**: crypt `$1$` MD5, `$2$` bcrypt (Blowfish), `$3$` NT hash (MD4), `$5$` SHA-256, `$6$` SHA-512, traditional DES; MD4/MD5/SHA-0/SHA-1/RIPEMD-160 (+ SHA-2, Skein wrappers via `mdXhl.c`).
- **Base contrib**: wpa_supplicant (CCMP, GCMP, TKIP, SAE, AES-WRAP, CMAC), unbound/ldns (DNSSEC RSA/DSA/ECDSA/Ed25519/Ed448/GOST), ntp (MD5, SHA-1, CMAC, NTS), libfido2, libsecureboot (BearSSL signature verify).

## Ports (security/ category)
1713 ports in FreeBSD 15 `security/`, 912 matching crypto keywords: see `security_ports_15.csv`. Libraries with their own algorithm sets worth reading in addition to the base: `security/openssl*`, `security/libressl*`, `security/gnupg`, `security/libgcrypt`, `security/botan3`, `security/nettle`, `security/libsodium`, `security/mbedtls*`, `security/wolfssl`, `security/liboqs`, `security/argon2`, `security/wireguard-tools`, `security/strongswan`, `security/openvpn`.

## Honest limits
- Names are read from tables in the source (OpenSSL provider tables, OpenSSH cipher/kex/mac tables, opencrypto ids, Kerberos enctype table). Algorithms implemented only inside a large port (for example the full `security/libgcrypt` or `security/botan3` sets) are listed as ports, not enumerated.
- `crypto_related` on the ports is a keyword flag, not a classification.
- Re-run the collector after each release; the target is one release branch, not a history.
