# JUKO Suporte — build do RustDesk

Base: RustDesk 1.4.9 (AGPL-3.0). Este repositório é o código-fonte completo do app distribuído.

## Gerar os instaladores

Actions → **JUKO - RustDesk Windows x64** → Run workflow, preenchendo:

| Entrada | O que é |
| --- | --- |
| `server-host` | Endereço público do servidor RustDesk (hbbs/hbbr), sem `http://`. Não pode ser `localhost`. |
| `server-key` | Chave pública do hbbs (`id_ed25519.pub`, 44 caracteres). |
| `api-url` | URL pública da API do JUKO (`https://...`), a mesma do `PUBLIC_API_URL` do Frontend. |
| `release-tag` | Tag da release que recebe os arquivos. |

Sai na release: `juko-suporte-install.exe` (cliente), `juko-agente-install.exe` (agente) e `SHA256SUMS.txt`.
Demora cerca de 46 minutos. Depois, no sistema JUKO, preencher `RUSTDESK_INSTALADOR_*` (Backend) e
`PUBLIC_RUSTDESK_INSTALADOR_*` (Frontend) com as URLs e os SHA-256 da release.

## O que é do JUKO neste fork

- `flutter/lib/common.dart`: tema MIDNIGHT (cores do `global.css` do sistema) e `jukoPair` (`juko://pair?token=...`).
- `.github/juko/gerar_custom.py`: `custom.txt` assinado (nome `JUKO`, servidor travado, tema escuro, URL da API).
- `.github/juko/gerar_icones.py`: ícones e logo do cabeçalho a partir de `logo-negativa.png`.
- `src/lang/ptbr.rs` e `en.rs`: "RustDesk" trocado por "JUKO" só nos textos traduzidos (a chave em inglês não muda;
  o crédito "Desenvolvido por RustDesk" foi mantido de propósito).
