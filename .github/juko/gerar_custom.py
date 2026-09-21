"""Gera e assina os custom.txt do RustDesk (versao cliente e versao agente).

O RustDesk le <pasta do exe>/custom.txt no boot: base64(assinatura(64) + JSON), verificado
contra a chave publica embutida no binario (src/common.rs -> read_custom_client).
No JSON: chaves com valor-objeto "override-settings"/"default-settings" viram opcoes travadas/
padrao; as demais chaves de texto viram HARD_SETTINGS (conn-type, disable-settings, ...).

Uso: gerar_custom.py <pasta-de-saida>   (env: JUKO_SERVER_HOST, JUKO_SERVER_KEY, RUNNER_TEMP)
"""
import base64
import json
import os
import pathlib
import sys

from nacl.signing import SigningKey, VerifyKey

host = os.environ["JUKO_SERVER_HOST"]
chave_servidor = os.environ["JUKO_SERVER_KEY"]
tmp = pathlib.Path(os.environ.get("RUNNER_TEMP", "."))
sk = SigningKey(base64.b64decode((tmp / "juko-sign-seed.b64").read_text()))

servidor = {
    "custom-rendezvous-server": host,  # trava o servidor (sem isso o rodape mostra "configure seu proprio servidor")
    "key": chave_servidor,
    "enable-check-update": "N",  # nunca oferece "baixar nova versao" do site oficial
    "hide-help-cards": "Y",  # esconde os cards de instalar / UAC / atualizar
}

variantes = {
    # Cliente: so mostra ID; sem configuracoes, sem instalar, sem senha (o agente conecta e o cliente clica Aceitar)
    "cliente": {
        "conn-type": "incoming",
        "disable-settings": "Y",
        "disable-installation": "Y",
        "disable-ab": "Y",
        "disable-account": "Y",
        "override-settings": {**servidor, "approve-mode": "click", "disable-change-id": "Y"},
    },
    # Agente: interface completa, so com o servidor travado e sem os avisos
    "agente": {
        "override-settings": servidor,
    },
}

saida = pathlib.Path(sys.argv[1])
saida.mkdir(parents=True, exist_ok=True)
vk = VerifyKey(bytes(sk.verify_key))

for nome, cfg in variantes.items():
    for k, v in cfg.items():
        if k not in ("override-settings", "default-settings", "app-name"):
            assert isinstance(v, str), f"{nome}.{k}: valor de HARD_SETTINGS precisa ser texto"
    assinado = bytes(sk.sign(json.dumps(cfg, separators=(",", ":")).encode()))
    txt = base64.b64encode(assinado).decode()
    (saida / f"custom-{nome}.txt").write_text(txt)
    # releitura como o RustDesk faz: decode64 -> verify(chave publica) -> JSON
    lido = json.loads(vk.verify(base64.b64decode(txt)))
    assert lido == cfg, f"{nome}: JSON lido difere do gerado"
    assert lido["override-settings"]["custom-rendezvous-server"] == host
    print(f"custom-{nome}.txt OK ({len(txt)} bytes base64)")
