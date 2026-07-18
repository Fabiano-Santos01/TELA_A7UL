"""
audio.py — Gerenciador de áudio modular para Tela Azul.py
Requer pygame para funcionar. Se não instalado, opera em modo silencioso.
"""

import json
import logging
import threading
from pathlib import Path
from typing import Optional

# ─── Logger (não esconde erros, mas não quebra o jogo) ───────
_log = logging.getLogger("audio")

# ─── Caminho raiz resolvido em relação a este arquivo ────────
_RAIZ      = Path(__file__).parent.parent
_AUDIO_DIR = _RAIZ / "assets" / "audio"
_CONFIG_PATH = _RAIZ / "saves" / "audio_config.json"

# ─── Tentativa de importar pygame ────────────────────────────
_PYGAME_OK  = False
_PYGAME_ERRO = ""

try:
    import pygame
    pygame.mixer.pre_init(44100, -16, 1, 1024)
    pygame.mixer.init()
    _freq, _size, _ch = pygame.mixer.get_init()
    if _freq and _freq > 0:
        _PYGAME_OK = True
    else:
        _PYGAME_ERRO = "mixer.get_init() retornou valores inválidos"
except ImportError:
    _PYGAME_ERRO = "pygame não instalado — rode: pip install pygame"
except Exception as _e:
    _PYGAME_ERRO = str(_e)

# ─── Configuração padrão ─────────────────────────────────────
_CONFIG_PADRAO = {
    "musica_on": True,
    "sfx_on":    True,
    "volume_musica": 0.55,
    "volume_sfx":    0.80,
}

# ─── Trilhas de música (nome_lógico → arquivo .wav) ──────────
_TRILHAS: dict[str, str] = {
    "menu":       "menu.wav",
    "exploracao": "exploracao.wav",
    "cidade":     "cidade.wav",
    "loja":       "loja.wav",
    "combate":    "combate.wav",
    "boss":       "boss.wav",
    "boss_final": "boss_final.wav",
    "tela_azul":  "tela_azul.wav",
    "creditos":   "creditos.wav",
    "ng_plus":    "ng_plus.wav",
}

# ─── Efeitos sonoros (nome_lógico → arquivo .wav) ────────────
_SFX: dict[str, str] = {
    "nav":          "nav.wav",
    "confirmar":    "confirmar.wav",
    "cancelar":     "cancelar.wav",
    "inventario":   "inventario.wav",
    "compra":       "compra.wav",
    "ouro":         "ouro.wav",
    "level_up":     "level_up.wav",
    "evolucao":     "evolucao.wav",
    "ataque":       "ataque.wav",
    "magia":        "magia.wav",
    "critico":      "critico.wav",
    "cura":         "cura.wav",
    "vitoria":      "vitoria.wav",
    "derrota":      "derrota.wav",
    "save":         "save.wav",
    "load":         "load.wav",
    "cidade_entra": "cidade_entra.wav",
    "boss_entra":   "boss_entra.wav",
    "interferencia":"interferencia.wav",
    "bip":          "bip.wav",
    "erro":         "erro.wav",
    "typewriter":   "typewriter.wav",
}


class GerenciadorAudio:
    """Gerencia música de fundo e efeitos sonoros via pygame."""

    def __init__(self) -> None:
        self._config: dict = dict(_CONFIG_PADRAO)
        self._trilha_atual: Optional[str] = None
        self._sfx_cache: dict = {}
        self._lock = threading.Lock()
        self._carregar_config()

    # ── Config ────────────────────────────────────────────────
    def _carregar_config(self) -> None:
        try:
            if _CONFIG_PATH.exists():
                dados = json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
                self._config.update({k: dados[k] for k in _CONFIG_PADRAO if k in dados})
        except Exception as e:
            _log.warning("Falha ao carregar config de áudio: %s", e)

    def salvar_config(self) -> None:
        try:
            _CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            _CONFIG_PATH.write_text(
                json.dumps(self._config, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except Exception as e:
            _log.warning("Falha ao salvar config de áudio: %s", e)

    # ── Propriedades ─────────────────────────────────────────
    @property
    def musica_on(self) -> bool:
        return bool(self._config["musica_on"])

    @property
    def sfx_on(self) -> bool:
        return bool(self._config["sfx_on"])

    @property
    def volume_musica(self) -> float:
        return float(self._config["volume_musica"])

    @property
    def volume_sfx(self) -> float:
        return float(self._config["volume_sfx"])

    # ── Música ───────────────────────────────────────────────
    def tocar_musica(self, nome: str, fade_ms: int = 800) -> None:
        if not _PYGAME_OK or not self.musica_on:
            return
        if self._trilha_atual == nome:
            return
        arquivo = _AUDIO_DIR / _TRILHAS.get(nome, "")
        if not arquivo.exists():
            _log.debug("Arquivo de música não encontrado: %s", arquivo)
            return
        with self._lock:
            try:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.fadeout(min(fade_ms // 2, 400))
                pygame.mixer.music.load(str(arquivo))
                pygame.mixer.music.set_volume(self.volume_musica)
                pygame.mixer.music.play(-1, fade_ms=fade_ms)
                self._trilha_atual = nome
            except Exception as e:
                _log.warning("Erro ao tocar música '%s': %s", nome, e)

    def parar_musica(self, fade_ms: int = 800) -> None:
        if not _PYGAME_OK:
            return
        try:
            pygame.mixer.music.fadeout(fade_ms)
            self._trilha_atual = None
        except Exception as e:
            _log.warning("Erro ao parar música: %s", e)

    def pausar_musica(self) -> None:
        if not _PYGAME_OK:
            return
        try:
            pygame.mixer.music.pause()
        except Exception as e:
            _log.warning("Erro ao pausar música: %s", e)

    def retomar_musica(self) -> None:
        if not _PYGAME_OK:
            return
        try:
            pygame.mixer.music.unpause()
        except Exception as e:
            _log.warning("Erro ao retomar música: %s", e)

    def ajustar_volume_musica(self, volume: float) -> None:
        self._config["volume_musica"] = max(0.0, min(1.0, volume))
        if _PYGAME_OK:
            try:
                pygame.mixer.music.set_volume(self._config["volume_musica"])
            except Exception as e:
                _log.warning("Erro ao ajustar volume de música: %s", e)

    # ── SFX ──────────────────────────────────────────────────
    def sfx(self, nome: str) -> None:
        if not _PYGAME_OK or not self.sfx_on:
            return
        arquivo = _AUDIO_DIR / _SFX.get(nome, "")
        if not arquivo.exists():
            _log.debug("SFX não encontrado: %s", arquivo)
            return
        try:
            if nome not in self._sfx_cache:
                self._sfx_cache[nome] = pygame.mixer.Sound(str(arquivo))
            som = self._sfx_cache[nome]
            som.set_volume(self.volume_sfx)
            som.play()
        except Exception as e:
            _log.warning("Erro ao tocar SFX '%s': %s", nome, e)

    # ── Sequência BSOD ───────────────────────────────────────
    def sequencia_bsod(self) -> None:
        """Para a música e toca sequência sonora da falsa BSOD."""
        import time
        if not _PYGAME_OK:
            return
        self.parar_musica(fade_ms=300)
        time.sleep(0.35)
        self.sfx("interferencia")
        time.sleep(0.6)
        self.sfx("erro")
        time.sleep(0.3)
        self.sfx("bip")
        self.tocar_musica("tela_azul", fade_ms=0)

    # ── Volume SFX ───────────────────────────────────────────
    def ajustar_volume_sfx(self, volume: float) -> None:
        self._config["volume_sfx"] = max(0.0, min(1.0, volume))

    # ── Toggles ──────────────────────────────────────────────
    def toggle_musica(self) -> bool:
        self._config["musica_on"] = not self._config["musica_on"]
        if not self._config["musica_on"]:
            self.parar_musica(200)
        return bool(self._config["musica_on"])

    def toggle_sfx(self) -> bool:
        self._config["sfx_on"] = not self._config["sfx_on"]
        return bool(self._config["sfx_on"])

    # ── Menu de configuração ─────────────────────────────────
    def menu_audio(self) -> None:
        from src.utils import limpar_tela, banner, texto_lento, cor, continuar
        from src.utils import CYAN, YELLOW, GREEN, RED, GRAY

        while True:
            limpar_tela()
            banner("CONFIGURAÇÕES DE ÁUDIO", "Personalize sua experiência")
            print()

            estado_musica = cor("ON", GREEN) if self.musica_on else cor("OFF", RED)
            estado_sfx    = cor("ON", GREEN) if self.sfx_on    else cor("OFF", RED)
            vol_m = int(self.volume_musica * 100)
            vol_s = int(self.volume_sfx * 100)

            if not _PYGAME_OK:
                print(cor("  ⚠️  Áudio indisponível.", YELLOW))
                if _PYGAME_ERRO:
                    print(cor(f"  Detalhe: {_PYGAME_ERRO}", GRAY))
                print(cor("  Dica: pip install pygame", GRAY))
                print()

            print(f"  {cor('[1]', CYAN)} Música:        {estado_musica} (volume: {vol_m}%)")
            print(f"  {cor('[2]', CYAN)} Efeitos SFX:   {estado_sfx} (volume: {vol_s}%)")
            print(f"  {cor('[3]', CYAN)} Volume música:  [{self._barra_volume(vol_m)}] {vol_m}%")
            print(f"  {cor('[4]', CYAN)} Volume SFX:    [{self._barra_volume(vol_s)}] {vol_s}%")
            print(f"  {cor('[5]', CYAN)} Voltar")
            print()

            esc = input(cor("  Escolha: ", YELLOW)).strip()
            if esc == "1":
                on = self.toggle_musica()
                texto_lento(f"  Música: {'ON' if on else 'OFF'}", 0.02)
            elif esc == "2":
                on = self.toggle_sfx()
                texto_lento(f"  SFX: {'ON' if on else 'OFF'}", 0.02)
            elif esc == "3":
                v = self._ler_volume("Volume da música (0–100): ")
                if v is not None:
                    self.ajustar_volume_musica(v / 100)
            elif esc == "4":
                v = self._ler_volume("Volume dos SFX (0–100): ")
                if v is not None:
                    self.ajustar_volume_sfx(v / 100)
            elif esc == "5":
                self.salvar_config()
                break

    def _barra_volume(self, pct: int, larg: int = 20) -> str:
        p = max(0, min(100, pct))
        cheio = int(larg * p / 100)
        return "█" * cheio + "░" * (larg - cheio)

    def _ler_volume(self, prompt: str) -> Optional[int]:
        from src.utils import cor, YELLOW
        val = input(cor(f"  {prompt}", YELLOW)).strip()
        if val.isdigit() and 0 <= int(val) <= 100:
            return int(val)
        return None


# ─── Instância global ────────────────────────────────────────
audio = GerenciadorAudio()
