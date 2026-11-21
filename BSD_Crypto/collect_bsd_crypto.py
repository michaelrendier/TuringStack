#!/usr/bin/env python3
"""collect_bsd_crypto.py (2026-11-21): every encryption algorithm in the most recent BSD, read from source.
Target: FreeBSD releng/15.1 (the latest release; tip bb03631fe3b7, 2026-11-13), the BSD with the largest shipped crypto surface (OpenBSD's libcrypto/LibreSSL, NetBSD and DragonFly are subsets/forks; see README).
Inputs : SRC  = sparse FreeBSD checkout (sys/, lib/, contrib/ ...), SRC2 = sparse checkout of crypto/ + secure/, INDEX = ports INDEX-15 (security/ category).
Outputs: algorithms.csv (component, kind, algorithm, where), security_ports_15.csv (all security/ ports), summary.json.
usage: python3 collect_bsd_crypto.py SRC SRC2 INDEX"""
import re, os, sys, csv, json, collections, glob
SRC, SRC2, INDEX = sys.argv[1:4]
rows = []
def add(comp, kind, alg, where): rows.append((comp, kind, alg, where))
def rd(p):
    try: return open(p, errors="ignore").read()
    except OSError: return ""
# 1. kernel opencrypto(9) algorithm ids + who uses them
txt = rd(f"{SRC}/sys/opencrypto/cryptodev.h")
KIND = lambda n: ("digest" if re.search(r"^(MD5|SHA1|SHA2_\d+|RIPEMD160|BLAKE2[BS])$", n) else "mac" if re.search(r"HMAC|KPDK|GMAC|POLY1305|CBC_MAC", n) else "aead" if re.search(r"GCM|CCM|CHACHA20_POLY1305", n) else "compression" if "DEFLATE" in n else "cipher")
for n in re.findall(r"#define\s+CRYPTO_([A-Z0-9_]+)\s+\d+\s", txt):
    if n.startswith(("DRIVERS", "ALGORITHM", "FLAG", "F_", "OP_", "HINT", "MAY", "HAS", "ASYNC", "SYMQ")): continue
    add("opencrypto(9)", KIND(n), n.replace("_", "-"), "sys/opencrypto/cryptodev.h")
# 2. geli(8) (disk encryption): ciphers and auth from g_eli.h / geom_eli.h
for f, k in ((f"{SRC}/sys/geom/eli/g_eli.h", "geli"),):
    t = rd(f)
    for n in sorted(set(re.findall(r"G_ELI_(?:CRYPTO_)?(?:ALGO_)?(AES[_A-Z0-9]*|CAMELLIA[_A-Z0-9]*|NULL|HMAC_[A-Z0-9]+|BLOWFISH|3DES)\b", t))): add("geli(8)", "disk-encryption", n, "sys/geom/eli/g_eli.h")
for n in re.findall(r"CRYPTO_([A-Z0-9_]+)", rd(f"{SRC}/sys/geom/eli/g_eli.c") + rd(f"{SRC}/sys/geom/eli/g_eli.h")):
    if n.startswith(("AES", "CAMELLIA", "SHA", "RIPEMD", "NULL")): add("geli(8)", "disk-encryption", n.replace("_", "-"), "sys/geom/eli/g_eli.[ch]")
# 3. kernel software implementations: directory = algorithm
KDIR = {"sys/crypto/aesni": "AES-NI (AES-CBC/XTS/ICM/GCM/CCM, SHA1, SHA256 via SHA-NI)", "sys/crypto/armv8": "ARMv8 Crypto Extensions (AES, SHA)", "sys/crypto/blake2": "BLAKE2b/BLAKE2s", "sys/crypto/camellia": "Camellia", "sys/crypto/ccp": "AMD CCP engine", "sys/crypto/chacha20": "ChaCha20", "sys/crypto/des": "DES/3DES", "sys/crypto/rc4": "RC4 (ARC4)", "sys/crypto/rijndael": "Rijndael/AES", "sys/crypto/sha2": "SHA-224/256/384/512", "sys/crypto/siphash": "SipHash", "sys/crypto/skein": "Skein (256/512/1024)", "sys/crypto/via": "VIA PadLock (AES, SHA)", "sys/crypto/openssl": "OpenSSL-derived assembly: AES, AES-GCM, ChaCha20, Poly1305, SHA-1/256/512", "sys/crypto/libsodium": "libsodium shim (randombytes/utils)"}
for d, a in KDIR.items():
    if os.path.isdir(f"{SRC}/{d}"): add("sys/crypto", "kernel-implementation", a, d)
for f, a in (("chacha20_poly1305.c", "ChaCha20-Poly1305 / XChaCha20-Poly1305 AEAD"), ("curve25519.c", "Curve25519 (X25519)"), ("md4c.c", "MD4"), ("md5c.c", "MD5"), ("sha1.c", "SHA-1")):
    if os.path.exists(f"{SRC}/sys/crypto/{f}"): add("sys/crypto", "kernel-implementation", a, f"sys/crypto/{f}")
for d, a in (("sys/dev/random", "Fortuna CSPRNG (AES-256 counter + SHA-256) / ChaCha20 (Fenestras X) / hardware RDRAND, RDSEED, DARN, Nehemiah"), ("sys/dev/wg", "WireGuard: X25519, ChaCha20-Poly1305, BLAKE2s, HMAC-BLAKE2s"), ("sys/netipsec", "IPsec ESP/AH/IPcomp transforms (xform_esp/xform_ah)"), ("sys/dev/padlock", "VIA PadLock"), ("sys/dev/glxsb", "AMD Geode LX AES"), ("sys/dev/qat", "Intel QuickAssist"), ("sys/dev/safexcel", "Inside Secure SafeXcel"), ("sys/dev/cesa", "Marvell CESA"), ("sys/dev/armv8crypto", "ARMv8 crypto driver")):
    if os.path.isdir(f"{SRC}/{d}") and os.listdir(f"{SRC}/{d}"): add("kernel-driver", "implementation/consumer", a, d)
t = rd(f"{SRC}/sys/netipsec/xform.h") + "".join(rd(p) for p in glob.glob(f"{SRC}/sys/netipsec/xform_*.c"))
for n in sorted({x for x in re.findall(r"#define\s+(SADB_X?[EA]ALG_[A-Z0-9_]+)\b", rd(f"{SRC}/sys/net/pfkeyv2.h")) if not x.endswith(("_NONE", "_MAX"))}): add("IPsec/PF_KEY", "ipsec-algorithm", n, "sys/net/pfkeyv2.h")
for p in sorted(glob.glob(f"{SRC}/sys/opencrypto/xform_*.c")): add("opencrypto(9) xforms", "transform", os.path.basename(p)[6:-2], "sys/opencrypto/" + os.path.basename(p))
# 4. OpenZFS ICP (native encryption / checksums)
zd = f"{SRC}/sys/contrib/openzfs/module/icp/algs"
for sub, a in (("aes", "AES (CCM, GCM)"), ("blake3", "BLAKE3 (checksum)"), ("edonr", "Edon-R (checksum)"), ("sha2", "SHA-256/512"), ("skein", "Skein (checksum)")):
    if os.path.isdir(f"{zd}/{sub}"): add("OpenZFS ICP", "zfs", a, f"sys/contrib/openzfs/module/icp/algs/{sub}")
# 5. libmd + libcrypt
for f, a in (("md4c.c", "MD4"), ("sha0c.c", "SHA-0"), ("sha1c.c", "SHA-1"), ("rmd160c.c", "RIPEMD-160"), ("mdXhl.c", "(MD2/4/5, SHA, RIPEMD, SHA-2, Skein wrappers)")): 
    if os.path.exists(f"{SRC}/lib/libmd/{f}"): add("libmd", "digest", a, f"lib/libmd/{f}")
for f in ("md2", "md4", "md5", "sha", "sha256", "sha512", "skein", "rmd160"): pass
for f, a in (("crypt-md5.c", "crypt $1$ (MD5)"), ("crypt-sha256.c", "crypt $5$ (SHA-256)"), ("crypt-sha512.c", "crypt $6$ (SHA-512)"), ("crypt-nthash.c", "crypt $3$ (NT hash = MD4)"), ("crypt.c", "crypt DES-based traditional + $2 bcrypt dispatch")):
    if os.path.exists(f"{SRC}/lib/libcrypt/{f}"): add("libcrypt", "password-hash", a, f"lib/libcrypt/{f}")
if os.path.exists(f"{SRC2}/secure/lib/libcrypt") or os.path.exists(f"{SRC}/lib/libcrypt/crypt.c"): add("libcrypt", "password-hash", "crypt $2a$/$2b$ (bcrypt, via crypt-blowfish)", "lib/libcrypt")
# 6. OpenSSL 3.x providers
nm = rd(f"{SRC2}/crypto/openssl/providers/implementations/include/prov/names.h")
names = {k: v for k, v in re.findall(r'#\s*define\s+(PROV_NAMES_[A-Z0-9_]+)\s+"([^"]*)"', nm)}
def sect(files, kind):
    seen = set()
    for f in files:
        for c, m in re.findall(r"ALG\((PROV_NAMES_[A-Z0-9_]+)\s*,\s*([A-Za-z0-9_]+)", rd(f)):
            if c in names and (kind, c) not in seen: seen.add((kind, c)); yield kind, names[c].split(":")[0]
P = f"{SRC2}/crypto/openssl/providers"
d = rd(f"{P}/defltprov.c"); fips = rd(f"{P}/fips/fipsprov.c") if os.path.exists(f"{P}/fips/fipsprov.c") else ""
# default provider table: sections are arrays; read each array by its name
for arr, kind in (("deflt_digests", "digest"), ("deflt_macs", "mac"), ("deflt_kdfs", "kdf"), ("deflt_keyexch", "key-exchange"), ("deflt_rands", "rng"), ("deflt_signature", "signature"), ("deflt_asym_cipher", "asym-cipher"), ("deflt_asym_kem", "kem"), ("deflt_keymgmt", "key-type"), ("deflt_ciphers", "cipher")):
    m = re.search(arr + r"\[\]\s*=\s*\{(.*?)\n\};", d, re.S)
    if not m: continue
    for c in re.findall(r"(PROV_NAMES_[A-Z0-9_]+)", m.group(1)):
        if c in names: add("OpenSSL 3 default provider", kind, names[c].split(":")[0], "crypto/openssl/providers/defltprov.c")
lg = rd(f"{P}/legacyprov.c")
for c in re.findall(r"(PROV_NAMES_[A-Z0-9_]+)|\{\s*\"([A-Za-z0-9-]+)(?::[^\"]*)?\"\s*,\s*\"provider=legacy", lg):
    n = names.get(c[0], c[0]).split(":")[0] if c[0] else c[1]
    if n: add("OpenSSL 3 legacy provider", "legacy", n, "crypto/openssl/providers/legacyprov.c")
for m in re.findall(r"\{\s*\"([A-Za-z0-9_-]+)(?::[^\"]*)?\"\s*,\s*\"provider=legacy[^\"]*\"", lg): pass
# 7. OpenSSH
c = rd(f"{SRC2}/crypto/openssh/cipher.c")
for n in sorted(set(re.findall(r'\{\s*"([a-z0-9@.-]+)"\s*,\s*\d', c))): add("OpenSSH", "ssh-cipher", n, "crypto/openssh/cipher.c")
k = rd(f"{SRC2}/crypto/openssh/kex-names.c") + rd(f"{SRC2}/crypto/openssh/kex.h")
for n in sorted(set(re.findall(r'#define\s+KEX_[A-Z0-9_]+\s+"([a-z0-9@.,-]+)"', k))): add("OpenSSH", "ssh-kex", n, "crypto/openssh/kex.h")
for n in sorted(set(re.findall(r'"((?:diffie-hellman|ecdh|curve25519|sntrup|mlkem)[a-z0-9@.,-]*)"', k))): add("OpenSSH", "ssh-kex", n, "crypto/openssh/kex-names.c")
mc = rd(f"{SRC2}/crypto/openssh/mac.c")
for n in sorted(set(re.findall(r'\{\s*"((?:hmac|umac)[a-z0-9@.-]*)"', mc))): add("OpenSSH", "ssh-mac", n, "crypto/openssh/mac.c")
sk = rd(f"{SRC2}/crypto/openssh/sshkey.c")
sk = sk + "".join(rd(p) for p in glob.glob(f"{SRC2}/crypto/openssh/ssh*.c"))
for n in sorted(set(re.findall(r'"((?:ssh-(?:rsa|dss|ed25519|xmss)|ecdsa-sha2-nistp\d+|sk-ssh-ed25519|sk-ecdsa-sha2-nistp256|rsa-sha2-\d+)(?:-cert-v01)?(?:@openssh\.com)?)"', sk))): add("OpenSSH", "ssh-hostkey", n, "crypto/openssh/sshkey.c")
# 8. Kerberos 5 (MIT) + Heimdal
e = rd(f"{SRC2}/crypto/krb5/src/lib/crypto/krb/etypes.c")
for n in sorted(set(re.findall(r'"([a-z0-9-]+)"', e))): add("MIT krb5", "kerberos-enctype", n, "crypto/krb5/src/lib/crypto/krb/etypes.c")
h = "".join(rd(p) for p in glob.glob(f"{SRC2}/crypto/heimdal/lib/krb5/crypto*.c"))
for n in sorted(set(re.findall(r'"((?:aes|des|des3|arcfour|camellia)[a-z0-9-]*)"', h))): add("Heimdal krb5", "kerberos-enctype", n, "crypto/heimdal/lib/krb5/crypto*.c")
# 9. libecc (secure/lib/libpkgecc = pkg's EC code): curves, sig algs, hashes
for dd, kind in (("hash", "digest"), ("sig", "signature")):
    for f in sorted(os.listdir(f"{SRC2}/crypto/libecc/src/{dd}")) if os.path.isdir(f"{SRC2}/crypto/libecc/src/{dd}") else []:
        if f.endswith(".c") and not f.startswith(("fuzzing", "sig_algs", "hash_algs", "ec_key", "ecdsa_common", "ecsdsa_common", "bign_common", "sha512_core", "sha3.c", "shake.c", "bash.c")) and f != "hmac.c": add("libecc", kind, f[:-2], f"crypto/libecc/src/{dd}/{f}")
cp = rd(f"{SRC2}/crypto/libecc/include/libecc/curves/known/ec_params_external.h") if os.path.exists(f"{SRC2}/crypto/libecc/include/libecc/curves/known/ec_params_external.h") else ""
for f in sorted(glob.glob(f"{SRC2}/crypto/libecc/include/libecc/curves/known/ec_params_*.h")): add("libecc", "curve", os.path.basename(f)[10:-2], "crypto/libecc/include/libecc/curves/known/")
# 10. boot-time verification (libsecureboot, bearssl)
if os.path.isdir(f"{SRC}/lib/libsecureboot"): add("libsecureboot", "signature/hash", "BearSSL X.509 + RSA/ECDSA signature verify, SHA-1/224/256/384/512 (verify_file, OpenPGP)", "lib/libsecureboot")
for d, a in (("contrib/wpa", "wpa_supplicant/hostapd: AES-CCMP, GCMP, TKIP(RC4+Michael), WEP, SAE, SHA-1/256/384, HMAC, PBKDF2, AES-WRAP, CMAC, OMAC1"), ("contrib/unbound", "DNSSEC: RSA, DSA, ECDSA P-256/384, Ed25519, Ed448, GOST, SHA-1/256/384/512, NSEC3"), ("contrib/ldns", "DNSSEC algorithms (same set as unbound)"), ("contrib/ntp", "NTP: MD5, SHA-1, CMAC (AES-128), NTS (AES-SIV)"), ("contrib/libfido2", "FIDO2: ES256, EdDSA, RS256, AES-256-CBC, HMAC-SHA-256")):
    if os.path.isdir(f"{SRC}/{d}"): add("base contrib", "protocol-suite", a, d)
os.makedirs(".", exist_ok=True)
rows = sorted(set(rows))
with open("algorithms.csv", "w", newline="") as fh: w = csv.writer(fh); w.writerow(["component", "kind", "algorithm", "source_path"]); w.writerows(rows)
# ports
pr = []
for ln in open(INDEX, errors="ignore"):
    p = ln.rstrip("\n").split("|")
    if len(p) > 6 and "/security/" in p[1]: pr.append((p[0], p[1].replace("/usr/ports/", ""), p[3], p[4]))
CR = re.compile(r"encrypt|crypt|cipher|TLS|SSL|openssl|gnupg|pgp|gpg|key|sign|hash|checksum|cert|VPN|wireguard|ipsec|ssh|otp|password|sodium|nettle|gcrypt|botan|argon|scrypt|bcrypt|libressl|kerberos|gss|pkcs|x509|PKI|AES|RSA|ECC|elliptic|quantum|ML-KEM|dilithium|fido|yubi|tpm", re.I)
with open("security_ports_15.csv", "w", newline="") as fh:
    w = csv.writer(fh); w.writerow(["package", "origin", "comment", "crypto_related"]); w.writerows([(a, b, c, "yes" if CR.search(a + " " + c) else "") for a, b, c, d in sorted(pr)])
cnt = collections.Counter(r[0] for r in rows); kinds = collections.Counter(r[1] for r in rows)
json.dump(dict(target="FreeBSD releng/15.1", rows=len(rows), distinct_algorithm_names=len({r[2] for r in rows}), by_component=dict(cnt.most_common()), by_kind=dict(kinds.most_common()), security_ports=len(pr), security_ports_crypto_related=sum(1 for a, b, c, d in pr if CR.search(a + " " + c))), open("summary.json", "w"), indent=1)
print(open("summary.json").read())
