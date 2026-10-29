"""Gera e assina os custom.txt do RustDesk (versao cliente e versao agente).

O RustDesk le <pasta do exe>/custom.txt no boot: base64(assinatura(64) + JSON), verificado
contra a chave publica embutida no binario (src/common.rs -> read_custom_client).
No JSON: chaves com valor-objeto "override-settings"/"default-settings" viram opcoes travadas/
padrao; as demais chaves de texto viram HARD_SETTINGS (conn-type, disable-settings, ...).

Uso: gerar_custom.py <pasta-de-saida>   (env: JUKO_SERVER_HOST, JUKO_SERVER_KEY, JUKO_API_URL, RUNNER_TEMP)
"""
import base64
import json
import os
import pathlib
import sys

from nacl.signing import SigningKey, VerifyKey

host = os.environ["JUKO_SERVER_HOST"]
chave_servidor = os.environ["JUKO_SERVER_KEY"]
api_url = os.environ["JUKO_API_URL"].rstrip("/")  # API do JUKO que recebe o ID (juko://pair)
assert api_url.startswith("https://") or api_url.startswith("http://localhost"), "JUKO_API_URL precisa ser https://"
tmp = pathlib.Path(os.environ.get("RUNNER_TEMP", "."))
sk = SigningKey(base64.b64decode((tmp / "juko-sign-seed.b64").read_text()))

servidor = {
    "custom-rendezvous-server": host,  # trava o servidor (sem isso o rodape mostra "configure seu proprio servidor")
    "key": chave_servidor,
    "juko-api-url": api_url,  # so o app assinado fala com esta URL; o link juko://pair nunca traz endereco
    "theme": "dark",  # tema MIDNIGHT do JUKO, travado
    "enable-check-update": "N",  # nunca oferece "baixar nova versao" do site oficial
    "hide-help-cards": "Y",  # esconde os cards de instalar / UAC / atualizar
}

# Nome do app: vira o nome da janela/instalador e o esquema dos links (juko://). Uma palavra so:
# com espaco o esquema do link ficaria invalido.
APP_NAME = "JUKO"

variantes = {
    # Cliente: so mostra ID; sem configuracoes, sem senha (o agente conecta e o cliente clica Aceitar).
    # A instalacao FICA liberada (Nivel 1): o arquivo baixado se chama "...-install.exe" e abre o instalador
    # sozinho; instalado, o app vira servico e o ID passa a ser fixo.
    "cliente": {
        "app-name": APP_NAME,
        "conn-type": "incoming",
        "disable-settings": "Y",
        "disable-ab": "Y",
        "disable-account": "Y",
        "override-settings": {**servidor, "approve-mode": "click", "disable-change-id": "Y"},
    },
    # Agente: interface completa, so com o servidor travado e sem os avisos
    "agente": {
        "app-name": APP_NAME,
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
    assert lido["override-settings"]["juko-api-url"] == api_url
    assert lido["app-name"] == APP_NAME and " " not in APP_NAME
    if nome == "cliente":
        assert "disable-installation" not in lido, "cliente precisa poder instalar (Nivel 1)"
    print(f"custom-{nome}.txt OK ({len(txt)} bytes base64)")
