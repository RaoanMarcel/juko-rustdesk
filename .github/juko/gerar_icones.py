"""Gera os icones do JUKO (K branca sobre o fundo do tema MIDNIGHT) a partir de logo-negativa.png.

Uso (na raiz do repositorio):  python .github/juko/gerar_icones.py
Escreve: icone do app/janela (Windows), bandeja, icone interno do app e o logo do cabecalho (tema escuro).
"""
import pathlib
from PIL import Image, ImageDraw, ImageFont

RAIZ = pathlib.Path(__file__).resolve().parents[2]
LOGO = Image.open(pathlib.Path(__file__).with_name("logo-negativa.png")).convert("RGBA")
LOGO = LOGO.crop(LOGO.getchannel("A").getbbox())

FUNDO = (0x11, 0x11, 0x1C, 255)    # --bg-base do MIDNIGHT
ANEL = (0x00, 0x53, 0xE2, 255)     # --accent-main do MIDNIGHT


def marca(altura: int) -> Image.Image:
    proporcao = LOGO.width / LOGO.height
    return LOGO.resize((max(1, round(altura * proporcao)), altura), Image.LANCZOS)


def icone(lado: int = 1024) -> Image.Image:
    img = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    raio = round(lado * 0.22)
    d.rounded_rectangle((0, 0, lado - 1, lado - 1), radius=raio, fill=ANEL)
    borda = max(2, round(lado * 0.035))
    d.rounded_rectangle((borda, borda, lado - 1 - borda, lado - 1 - borda), radius=raio - borda, fill=FUNDO)
    m = marca(round(lado * 0.58))
    img.alpha_composite(m, ((lado - m.width) // 2, (lado - m.height) // 2))
    return img


def logo_cabecalho() -> Image.Image:
    """Faixa do topo da tela inicial (o app limita a 300x60; gera em 2x)."""
    img = Image.new("RGBA", (600, 120), (0, 0, 0, 0))
    m = marca(96)
    img.alpha_composite(m, (0, 12))
    fonte = None
    for nome in ("segoeuib.ttf", "arialbd.ttf", "DejaVuSans-Bold.ttf"):
        try:
            fonte = ImageFont.truetype(nome, 64)
            break
        except OSError:
            continue
    if fonte:
        ImageDraw.Draw(img).text((m.width + 24, 60), "JUKO Suporte", font=fonte, fill=(0xF8, 0xFA, 0xFC, 255), anchor="lm")
    return img


def salvar_ico(img: Image.Image, destino: pathlib.Path, tamanhos):
    destino.parent.mkdir(parents=True, exist_ok=True)
    img.save(destino, format="ICO", sizes=[(t, t) for t in tamanhos])


base = icone()
ICO_APP = [16, 20, 24, 32, 40, 48, 64, 128, 256]
salvar_ico(base, RAIZ / "flutter/windows/runner/resources/app_icon.ico", ICO_APP)
salvar_ico(base, RAIZ / "res/icon.ico", ICO_APP)
salvar_ico(base, RAIZ / "res/tray-icon.ico", [16, 24, 32, 48])
salvar_ico(base, RAIZ / "flutter/assets/icon.ico", ICO_APP)      # atalhos do instalador (data\flutter_assets\assets\icon.ico)
base.resize((256, 256), Image.LANCZOS).save(RAIZ / "flutter/assets/icon.png")  # icone interno (loadIcon)
logo_cabecalho().save(RAIZ / "flutter/assets/logo_dark.png")      # cabecalho da tela inicial no tema escuro
print("icones gerados")
