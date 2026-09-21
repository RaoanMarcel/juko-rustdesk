"""Gera o par de chaves efemero que assina o custom.txt deste build.

A chave PUBLICA e impressa (o workflow a embute em src/common.rs, no lugar da chave
oficial do RustDesk). A SEMENTE fica so no RUNNER_TEMP do job e some com ele; sem ela
ninguem consegue assinar um custom.txt que este binario aceite.
"""
import base64
import os
import pathlib

from nacl.signing import SigningKey

sk = SigningKey.generate()
tmp = pathlib.Path(os.environ.get("RUNNER_TEMP", "."))
(tmp / "juko-sign-seed.b64").write_text(base64.b64encode(bytes(sk)).decode())
print(base64.b64encode(bytes(sk.verify_key)).decode())
