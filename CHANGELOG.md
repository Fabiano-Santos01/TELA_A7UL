# CHANGELOG — Tela A7UL Release 1.0

## Versões entregues

- `Tela_A7UL_Full_v1.0/` — Versão completa com áudio, NG+, BSOD, campanha integral
- `Tela_A7UL_Lite_v1.0/` — Versão de demonstração sem áudio, campanha reduzida

---

## Arquivos modificados

### `audio.py` (Full e Lite)
**Motivo:** Causa raiz do silêncio no áudio identificada.
- Os arquivos em `assets/audio/` tinham extensão `.ogg` mas eram WAV internamente. O pygame carrega por extensão e rejeitava silenciosamente. Todos renomeados para `.wav` e os dicionários `_TRILHAS` e `_SFX` atualizados.
- `_AUDIO_DIR` e `_CONFIG_PATH` corrigidos de `Path("assets/audio")` para `Path(__file__).parent / "assets" / "audio"` — resolve em qualquer CWD no Windows.
- Substituídos todos os `except Exception: pass` por `_log.warning(...)` via `logging.getLogger("audio")`.
- **Lite:** substituído por stub silencioso sem nenhuma dependência externa.

### `player.py` (Full e Lite)
**Motivo:** Todos os 6 blocos `try: from audio import audio as _a; _a.sfx(...) except Exception: pass` dentro de funções suprimiam erros de áudio silenciosamente e impediam o som de funcionar.
- Adicionado `from audio import audio as _audio` no topo do arquivo.
- Substituídos todos os blocos inline por `_audio.sfx("nome")` direto.
- Bugs corrigidos: `sfx("level_up")`, `sfx("evolucao")`, `sfx("critico")`, `sfx("ataque")`, `sfx("magia")`, `sfx("cura")`.

### `world.py` (Full e Lite)
**Motivo:** Mesmo padrão de blocos inline de áudio com `try/except: pass`.
- Adicionado `from audio import audio as _audio` no topo.
- Corrigidos: `sfx("compra")`, `sfx("cidade_entra")`.

### `combate.py` (Full e Lite)
**Motivo:** Dois problemas técnicos de save e um inline de áudio.
- `SAVE_DIR = Path("saves")` → `Path(__file__).parent / "saves"` — caminhos absolutos.
- `autosave()`: `except Exception: pass` → `except Exception as e: _log.warning(...)` — falha de save agora é registrada.
- `carregar_de_slot()`: mesmo tratamento — erro logado em vez de engolido.
- Adicionado `import logging` e `_log = logging.getLogger("combate")`.

### `main.py` (Full e Lite)
**Motivo:** Caminho relativo em `tela_selecionar_save` falhava fora do diretório do projeto.
- `Path(f"saves/slot_{i}.json")` → `_SAVE_DIR / f"slot_{i}.json"` usando `_SAVE_DIR = Path(__file__).parent / "saves"` definido no topo.
- **Lite:** adicionada função `montar_encontros_lite()` com campanha reduzida (10 encontros vs 17), mantendo narrativa, textos, bosses e cidades integralmente. A função `_jogar()` da Lite aponta para esta versão reduzida.

### `tela_azul.py` (Full e Lite)
**Motivo:** Flags de BSOD usavam `Path("saves")` relativo.
- `_FLAG_FILE`, `_FLAG_NG`, flag de retorno: todos corrigidos para `_SAVES_DIR = Path(__file__).parent / "saves"`.
- Removido `import string` (não utilizado).
- `try: _audio.sequencia_bsod() except Exception: pass` → chamada direta (o método já trata internamente).

### `gerar_sons.py` (Full e Lite)
**Motivo:** `OUTPUT_DIR = Path("assets") / "audio"` falhava fora do diretório do projeto.
- Corrigido para `Path(__file__).parent / "assets" / "audio"`.

### `utils.py` (apenas Full)
**Motivo:** Adicionar efeito de máquina de escrever discreto durante `texto_lento()`.
- A cada 3 caracteres visíveis digitados, dispara `_audio.sfx("typewriter")` sem bloquear o timing existente.
- Não altera velocidade, conteúdo ou comportamento dos textos.

### `assets/audio/*.wav` (apenas Full)
**Motivo:** Arquivos renomeados de `.ogg` para `.wav` (correção do bug raiz de áudio).
- Adicionado `typewriter.wav` — som de tecla mecânica 8ms, gerado por síntese pura.

---

## Bugs corrigidos

| # | Bug | Causa raiz | Arquivo(s) |
|---|-----|------------|------------|
| 1 | Áudio completamente silencioso | Arquivos `.ogg` eram WAV internamente; pygame rejeita por extensão | `audio.py`, `assets/audio/` |
| 2 | Áudio não inicializava | Blocos `try/except: pass` em `player.py` e `world.py` suprimiam toda chamada de sfx | `player.py`, `world.py` |
| 3 | Saves falham fora do diretório do projeto | `Path("saves")` relativo ao CWD | `combate.py`, `main.py`, `tela_azul.py` |
| 4 | NG+ não aparecia no menu após reabrir | Flag `.ng_plus_unlocked` não encontrada por caminho relativo | `tela_azul.py` |
| 5 | Falha de autosave silenciosa | `except Exception: pass` sem log | `combate.py` |
| 6 | `gerar_sons.py` falhava fora do diretório | `Path("assets")` relativo | `gerar_sons.py` |
| 7 | `import string` desnecessário | Resíduo de versão anterior | `tela_azul.py` |

---

## O que NÃO foi alterado

- História, narrativa, diálogos, humor, piadas, referências +18
- Arte ASCII e banner do menu
- Subtítulo do menu inicial
- Menus, cores, velocidade de textos, identidade visual
- Estrutura da campanha (Full)
- Balanceamento de combate
- Sistema de classes e subclasses
- NPCs, cidades, eventos de caminho
- Modo recrutador
- Evento da falsa tela azul (lógica e narrativa)
- Arquitetura geral do projeto

---

## Como executar

```bash
# Full (com áudio)
cd Tela_A7UL_Full_v1.0
python gerar_sons.py     # apenas na primeira vez
python main.py

# Lite (sem áudio, demonstração rápida)
cd Tela_A7UL_Lite_v1.0
python main.py
```

**Requisitos Full:** Python 3.10+, `pip install pygame`
**Requisitos Lite:** Python 3.10+ apenas
