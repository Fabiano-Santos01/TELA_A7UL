"""
gerar_sons.py — Gerador de sons pixel art / 8-bit para Tela Azul.py
Execute uma vez: python gerar_sons.py
Gera todos os arquivos .ogg/.wav em assets/audio/
Requer apenas Python 3 padrão (wave, array, math, struct, os).
"""

import os
import math
import wave
import array
import struct
from pathlib import Path

SAMPLE_RATE = 44100
OUTPUT_DIR  = Path(__file__).resolve().parent.parent / "assets" / "audio"


def _salvar_wav(nome: str, amostras: list[float], volume: float = 0.7) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    caminho = OUTPUT_DIR / nome
    # Normaliza e converte para int16
    dados = array.array("h", [
        max(-32767, min(32767, int(s * volume * 32767)))
        for s in amostras
    ])
    with wave.open(str(caminho), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(dados.tobytes())
    print(f"  ✅ {caminho}")


def _senoide(freq: float, duracao: float, sr: int = SAMPLE_RATE) -> list[float]:
    n = int(sr * duracao)
    return [math.sin(2 * math.pi * freq * i / sr) for i in range(n)]


def _quadrada(freq: float, duracao: float, duty: float = 0.5,
               sr: int = SAMPLE_RATE) -> list[float]:
    n = int(sr * duracao)
    period = sr / freq
    return [1.0 if (i % period) / period < duty else -1.0 for i in range(n)]


def _triangular(freq: float, duracao: float, sr: int = SAMPLE_RATE) -> list[float]:
    n = int(sr * duracao)
    period = sr / freq
    return [2 * abs(2 * ((i / period) - math.floor(i / period + 0.5))) - 1
            for i in range(n)]


def _ruido(duracao: float, sr: int = SAMPLE_RATE) -> list[float]:
    import random
    n = int(sr * duracao)
    return [random.uniform(-1, 1) for _ in range(n)]


def _envelope(amostras: list[float], attack: float, decay: float,
               sustain: float, release: float, sustain_level: float = 0.7,
               sr: int = SAMPLE_RATE) -> list[float]:
    n = len(amostras)
    a = int(attack * sr)
    d = int(decay * sr)
    r = int(release * sr)
    s = max(0, n - a - d - r)
    env = []
    for i in range(min(a, n)):
        env.append(i / a if a > 0 else 1.0)
    for i in range(min(d, n - len(env))):
        env.append(1.0 - (1.0 - sustain_level) * i / d if d > 0 else sustain_level)
    for i in range(min(s, n - len(env))):
        env.append(sustain_level)
    for i in range(min(r, n - len(env))):
        env.append(sustain_level * (1.0 - i / r) if r > 0 else 0.0)
    while len(env) < n:
        env.append(0.0)
    return [a * e for a, e in zip(amostras, env)]


def _mix(*listas: list[float]) -> list[float]:
    n = max(len(l) for l in listas)
    resultado = [0.0] * n
    for l in listas:
        for i, v in enumerate(l):
            resultado[i] += v
    fator = 1.0 / len(listas)
    return [v * fator for v in resultado]


def _concatenar(*listas: list[float]) -> list[float]:
    resultado = []
    for l in listas:
        resultado.extend(l)
    return resultado


def _silencio(duracao: float, sr: int = SAMPLE_RATE) -> list[float]:
    return [0.0] * int(sr * duracao)


def _sweep(freq_ini: float, freq_fim: float, duracao: float,
           forma: str = "quad", sr: int = SAMPLE_RATE) -> list[float]:
    n = int(sr * duracao)
    result = []
    phase = 0.0
    for i in range(n):
        t = i / n
        freq = freq_ini + (freq_fim - freq_ini) * t
        phase += 2 * math.pi * freq / sr
        if forma == "quad":
            v = 1.0 if math.sin(phase) >= 0 else -1.0
        elif forma == "tri":
            v = 2 * abs(2 * (phase / (2 * math.pi) - math.floor(phase / (2 * math.pi) + 0.5))) - 1
        else:
            v = math.sin(phase)
        result.append(v)
    return result


# ─── Sons individuais ─────────────────────────────────────────

def gen_nav():
    """Bip curto de navegação — tick pixel."""
    s = _quadrada(880, 0.04)
    s = _envelope(s, 0.002, 0.02, 0.01, 0.01)
    _salvar_wav("nav.ogg", s, 0.4)


def gen_confirmar():
    """Dois tons ascendentes — confirmação."""
    a = _quadrada(440, 0.06)
    b = _quadrada(660, 0.08)
    a = _envelope(a, 0.002, 0.03, 0.02, 0.01)
    b = _envelope(b, 0.002, 0.04, 0.02, 0.015)
    s = _concatenar(a, _silencio(0.02), b)
    _salvar_wav("confirmar.ogg", s, 0.5)


def gen_cancelar():
    """Tom descendente — cancelamento."""
    a = _quadrada(440, 0.07)
    b = _quadrada(280, 0.09)
    a = _envelope(a, 0.002, 0.03, 0.02, 0.02)
    b = _envelope(b, 0.002, 0.04, 0.02, 0.03)
    s = _concatenar(a, _silencio(0.02), b)
    _salvar_wav("cancelar.ogg", s, 0.45)


def gen_inventario():
    """Som de tela de inventário — clic digital."""
    s = _quadrada(330, 0.05)
    s2 = _quadrada(495, 0.05)
    s = _envelope(s, 0.001, 0.02, 0.02, 0.01)
    s2 = _envelope(s2, 0.001, 0.02, 0.02, 0.01)
    r = _concatenar(s, _silencio(0.01), s2)
    _salvar_wav("inventario.ogg", r, 0.4)


def gen_compra():
    """Som de compra — moeda digital."""
    notas = [(523, 0.06), (659, 0.06), (784, 0.10)]
    partes = []
    for freq, dur in notas:
        n = _quadrada(freq, dur)
        n = _envelope(n, 0.002, dur * 0.3, dur * 0.4, dur * 0.3)
        partes.append(n)
        partes.append(_silencio(0.01))
    _salvar_wav("compra.ogg", _concatenar(*partes), 0.5)


def gen_ouro():
    """Moeda coletada — 3 bips rápidos."""
    partes = []
    for freq in [660, 784, 1047]:
        n = _quadrada(freq, 0.05)
        n = _envelope(n, 0.001, 0.02, 0.01, 0.02)
        partes.append(n)
        partes.append(_silencio(0.008))
    _salvar_wav("ouro.ogg", _concatenar(*partes), 0.5)


def gen_level_up():
    """Level up — fanfarra pixel ascendente."""
    notas = [262, 330, 392, 523, 659, 784, 1047]
    partes = []
    for freq in notas:
        n = _quadrada(freq, 0.08)
        n = _envelope(n, 0.002, 0.03, 0.03, 0.02)
        partes.append(n)
        partes.append(_silencio(0.005))
    # Acorde final
    chord = _mix(
        _envelope(_quadrada(523, 0.25), 0.01, 0.05, 0.1, 0.09),
        _envelope(_quadrada(659, 0.25), 0.01, 0.05, 0.1, 0.09),
        _envelope(_quadrada(784, 0.25), 0.01, 0.05, 0.1, 0.09),
    )
    partes.append(chord)
    _salvar_wav("level_up.ogg", _concatenar(*partes), 0.55)


def gen_evolucao():
    """Evolução de classe — épico pixel."""
    sweep1 = _sweep(200, 800, 0.3, "quad")
    sweep1 = _envelope(sweep1, 0.05, 0.1, 0.1, 0.05)
    notas = [523, 659, 784, 1047, 1319]
    partes = [sweep1, _silencio(0.05)]
    for freq in notas:
        n = _quadrada(freq, 0.07)
        n = _envelope(n, 0.002, 0.03, 0.02, 0.02)
        partes.append(n)
        partes.append(_silencio(0.005))
    chord = _mix(
        _envelope(_quadrada(784, 0.4), 0.01, 0.08, 0.2, 0.11),
        _envelope(_quadrada(988, 0.4), 0.01, 0.08, 0.2, 0.11),
        _envelope(_quadrada(1175, 0.4), 0.01, 0.08, 0.2, 0.11),
    )
    partes.append(chord)
    _salvar_wav("evolucao.ogg", _concatenar(*partes), 0.5)


def gen_ataque():
    """Ataque básico — impacto pixelado."""
    s = _sweep(300, 80, 0.08, "quad")
    s = _envelope(s, 0.001, 0.04, 0.02, 0.03)
    noise = _ruido(0.04)
    noise = _envelope(noise, 0.001, 0.01, 0.01, 0.02)
    r = _mix(s[:len(noise)] + [0.0] * max(0, len(s) - len(noise)),
             noise + [0.0] * max(0, len(s) - len(noise)))
    _salvar_wav("ataque.ogg", r[:len(s)], 0.5)


def gen_magia():
    """Magia / skill — varredura mágica."""
    s = _sweep(200, 1200, 0.15, "sine")
    s = _envelope(s, 0.01, 0.05, 0.06, 0.04)
    shimmer = [math.sin(2 * math.pi * 3000 * i / SAMPLE_RATE) * 0.3
               for i in range(len(s))]
    r = [a + b for a, b in zip(s, shimmer)]
    _salvar_wav("magia.ogg", r, 0.45)


def gen_critico():
    """Crítico — impacto + eco pixel."""
    s1 = _sweep(600, 100, 0.1, "quad")
    s1 = _envelope(s1, 0.001, 0.05, 0.03, 0.04)
    eco = [v * 0.4 for v in s1]
    silencio_eco = _silencio(0.08)
    r = _concatenar(s1, _silencio(0.08), eco)
    _salvar_wav("critico.ogg", r, 0.55)


def gen_cura():
    """Cura — arpejo suave ascendente."""
    notas = [523, 659, 784, 1047]
    partes = []
    for freq in notas:
        n = _triangular(freq, 0.10)
        n = _envelope(n, 0.01, 0.04, 0.04, 0.02, sustain_level=0.6)
        partes.append(n)
        partes.append(_silencio(0.01))
    _salvar_wav("cura.ogg", _concatenar(*partes), 0.45)


def gen_vitoria():
    """Vitória — jingle pixel completo."""
    melodia = [
        (523, 0.1), (523, 0.1), (523, 0.1), (415, 0.07),
        (523, 0.1), (659, 0.1), (784, 0.2),
    ]
    partes = []
    for freq, dur in melodia:
        n = _quadrada(freq, dur)
        n = _envelope(n, 0.005, dur * 0.3, dur * 0.3, dur * 0.4)
        partes.append(n)
        partes.append(_silencio(0.01))
    _salvar_wav("vitoria.ogg", _concatenar(*partes), 0.5)


def gen_derrota():
    """Derrota — descida sombria."""
    notas = [(392, 0.12), (349, 0.12), (330, 0.12), (294, 0.12), (262, 0.25)]
    partes = []
    for freq, dur in notas:
        n = _quadrada(freq, dur)
        n = _envelope(n, 0.005, dur * 0.2, dur * 0.4, dur * 0.4, sustain_level=0.5)
        partes.append(n)
        partes.append(_silencio(0.01))
    _salvar_wav("derrota.ogg", _concatenar(*partes), 0.5)


def gen_save():
    """Save — dois bips de confirmação."""
    a = _quadrada(660, 0.06)
    b = _quadrada(880, 0.08)
    a = _envelope(a, 0.002, 0.02, 0.02, 0.016)
    b = _envelope(b, 0.002, 0.03, 0.03, 0.02)
    _salvar_wav("save.ogg", _concatenar(a, _silencio(0.02), b), 0.4)


def gen_load():
    """Load — varredura ascendente."""
    s = _sweep(220, 880, 0.15, "quad")
    s = _envelope(s, 0.01, 0.05, 0.06, 0.04)
    _salvar_wav("load.ogg", s, 0.45)


def gen_cidade_entra():
    """Entrada em cidade — fanfarra pixelada."""
    notas = [(392, 0.08), (523, 0.08), (659, 0.12)]
    partes = []
    for freq, dur in notas:
        n = _quadrada(freq, dur)
        n = _envelope(n, 0.003, dur * 0.3, dur * 0.3, dur * 0.4)
        partes.append(n)
        partes.append(_silencio(0.008))
    _salvar_wav("cidade_entra.ogg", _concatenar(*partes), 0.45)


def gen_boss_entra():
    """Entrada de boss — tremor grave + alarme."""
    grave = _quadrada(55, 0.4)
    grave = _envelope(grave, 0.05, 0.1, 0.15, 0.1, sustain_level=0.6)
    alarme = _sweep(880, 220, 0.3, "quad")
    alarme = _envelope(alarme, 0.01, 0.1, 0.1, 0.1)
    n = max(len(grave), len(alarme))
    grave  += [0.0] * (n - len(grave))
    alarme += [0.0] * (n - len(alarme))
    r = [g * 0.6 + a * 0.4 for g, a in zip(grave, alarme)]
    _salvar_wav("boss_entra.ogg", r, 0.55)


def gen_interferencia():
    """Interferência — ruído com modulação (BSOD)."""
    ruido = _ruido(1.5)
    mod = [math.sin(2 * math.pi * 8 * i / SAMPLE_RATE) for i in range(len(ruido))]
    r = [a * (0.5 + 0.5 * m) for a, m in zip(ruido, mod)]
    _salvar_wav("interferencia.ogg", r, 0.6)


def gen_bip():
    """Bip eletrônico (BSOD)."""
    s = _senoide(1000, 0.5)
    s = _envelope(s, 0.01, 0.1, 0.25, 0.15)
    _salvar_wav("bip.ogg", s, 0.5)


def gen_erro():
    """Erro crítico — som de falha de sistema."""
    partes = []
    for freq in [200, 180, 160]:
        n = _quadrada(freq, 0.12)
        n = _envelope(n, 0.001, 0.05, 0.04, 0.03, sustain_level=0.4)
        partes.append(n)
        partes.append(_silencio(0.02))
    _salvar_wav("erro.ogg", _concatenar(*partes), 0.55)


# ─── Trilhas de música (loops curtos 8-bit) ───────────────────

def _arpejo_loop(notas: list, dur_nota: float, repeticoes: int,
                 forma: str = "quad", vol: float = 0.4) -> list[float]:
    partes = []
    for _ in range(repeticoes):
        for freq in notas:
            n = globals()[f"_{forma}da"](freq, dur_nota) if f"_{forma}da" in globals() else _quadrada(freq, dur_nota)
            n = _envelope(n, 0.005, dur_nota * 0.2, dur_nota * 0.5, dur_nota * 0.3, sustain_level=0.7)
            partes.append(n)
    return _concatenar(*partes)


def gen_musica_menu():
    """Menu — tema tranquilo com arpejo pixel."""
    notas_base = [262, 330, 392, 523, 392, 330]
    notas_harm = [196, 247, 294, 392, 294, 247]
    dur = 0.12
    rep = 6
    base = []
    harm = []
    for _ in range(rep):
        for freq in notas_base:
            n = _quadrada(freq, dur)
            n = _envelope(n, 0.005, dur * 0.2, dur * 0.5, dur * 0.3, sustain_level=0.65)
            base.append(n)
        for freq in notas_harm:
            n = _triangular(freq, dur)
            n = _envelope(n, 0.005, dur * 0.2, dur * 0.5, dur * 0.3, sustain_level=0.5)
            harm.append(n)
    b = _concatenar(*base)
    h = _concatenar(*harm)
    n = min(len(b), len(h))
    r = [b[i] * 0.6 + h[i] * 0.4 for i in range(n)]
    _salvar_wav("menu.ogg", r, 0.35)


def gen_musica_exploracao():
    """Exploração — aventura pixel dinâmica."""
    # Melodia principal
    melodia = [392, 440, 494, 523, 494, 440, 392, 349,
               392, 440, 494, 523, 659, 587, 523, 494]
    # Baixo
    baixo   = [196, 196, 247, 262, 247, 196, 196, 175,
               196, 196, 247, 262, 330, 294, 262, 247]
    dur = 0.10
    rep = 4
    partes_m = []
    partes_b = []
    for _ in range(rep):
        for freq in melodia:
            n = _quadrada(freq, dur)
            n = _envelope(n, 0.003, dur * 0.2, dur * 0.5, dur * 0.3)
            partes_m.append(n)
        for freq in baixo:
            n = _quadrada(freq, dur)
            n = _envelope(n, 0.003, dur * 0.3, dur * 0.4, dur * 0.3, sustain_level=0.5)
            partes_b.append(n)
    m = _concatenar(*partes_m)
    b = _concatenar(*partes_b)
    n = min(len(m), len(b))
    r = [m[i] * 0.55 + b[i] * 0.45 for i in range(n)]
    _salvar_wav("exploracao.ogg", r, 0.38)


def gen_musica_combate():
    """Combate — urgência pixel."""
    melodia = [523, 494, 523, 587, 523, 494, 440, 494,
               523, 659, 523, 494, 440, 494, 523, 392]
    baixo   = [131, 131, 131, 147, 131, 131, 110, 131,
               131, 165, 131, 131, 110, 131, 131, 98]
    dur = 0.08
    rep = 5
    pm, pb = [], []
    for _ in range(rep):
        for freq in melodia:
            n = _quadrada(freq, dur)
            n = _envelope(n, 0.002, dur * 0.15, dur * 0.6, dur * 0.25)
            pm.append(n)
        for freq in baixo:
            n = _quadrada(freq, dur)
            n = _envelope(n, 0.002, dur * 0.2, dur * 0.5, dur * 0.3, sustain_level=0.6)
            pb.append(n)
    m = _concatenar(*pm)
    b = _concatenar(*pb)
    n = min(len(m), len(b))
    r = [m[i] * 0.55 + b[i] * 0.45 for i in range(n)]
    _salvar_wav("combate.ogg", r, 0.4)


def gen_musica_boss():
    """Boss — tenso e pesado."""
    melodia = [262, 294, 262, 247, 220, 247, 262, 196,
               220, 247, 262, 294, 330, 294, 262, 247]
    baixo   = [65, 73, 65, 62, 55, 62, 65, 49,
               55, 62, 65, 73, 82, 73, 65, 62]
    dur = 0.10
    rep = 4
    pm, pb = [], []
    for _ in range(rep):
        for freq in melodia:
            n = _quadrada(freq, dur)
            n = _envelope(n, 0.003, dur * 0.2, dur * 0.5, dur * 0.3)
            pm.append(n)
        for freq in baixo:
            n = _quadrada(freq * 2, dur)
            n = _envelope(n, 0.003, dur * 0.3, dur * 0.4, dur * 0.3, sustain_level=0.55)
            pb.append(n)
    m = _concatenar(*pm)
    b = _concatenar(*pb)
    n = min(len(m), len(b))
    r = [m[i] * 0.5 + b[i] * 0.5 for i in range(n)]
    _salvar_wav("boss.ogg", r, 0.42)


def gen_musica_boss_final():
    """Boss final — épico e ameaçador."""
    melodia = [196, 220, 196, 175, 165, 175, 196, 147,
               165, 175, 196, 220, 247, 220, 196, 175,
               196, 247, 220, 196, 175, 196, 220, 165,
               175, 196, 220, 247, 294, 247, 220, 196]
    dur = 0.09
    rep = 3
    pm = []
    for _ in range(rep):
        for freq in melodia:
            n = _mix(
                _envelope(_quadrada(freq, dur), 0.002, dur * 0.2, dur * 0.5, dur * 0.3),
                _envelope(_quadrada(freq * 2, dur), 0.002, dur * 0.2, dur * 0.5, dur * 0.3),
            )
            pm.append(n)
    r = _concatenar(*pm)
    _salvar_wav("boss_final.ogg", r, 0.4)


def gen_musica_cidade():
    """Cidade — tranquilo e aconchegante."""
    melodia = [523, 587, 659, 698, 659, 587, 523, 494,
               523, 587, 659, 784, 698, 659, 587, 523]
    dur = 0.13
    rep = 4
    pm = []
    for _ in range(rep):
        for freq in melodia:
            n = _triangular(freq, dur)
            n = _envelope(n, 0.01, dur * 0.3, dur * 0.4, dur * 0.3, sustain_level=0.6)
            pm.append(n)
    r = _concatenar(*pm)
    _salvar_wav("cidade.ogg", r, 0.32)


def gen_musica_loja():
    """Loja — alegre e comercial pixel."""
    melodia = [659, 784, 880, 784, 659, 784, 1047, 784,
               659, 587, 523, 587, 659, 523, 494, 523]
    dur = 0.09
    rep = 5
    pm = []
    for _ in range(rep):
        for freq in melodia:
            n = _quadrada(freq, dur)
            n = _envelope(n, 0.003, dur * 0.2, dur * 0.5, dur * 0.3)
            pm.append(n)
    r = _concatenar(*pm)
    _salvar_wav("loja.ogg", r, 0.3)


def gen_musica_tela_azul():
    """Tela azul — glitch e suspense."""
    # Ruído modulado com varredura grave
    ruido = _ruido(3.0)
    sweep = _sweep(80, 40, 3.0, "quad")
    mod = [math.sin(2 * math.pi * 0.5 * i / SAMPLE_RATE) for i in range(len(ruido))]
    r = [ruido[i] * 0.3 + sweep[i] * 0.7 * (0.5 + 0.5 * mod[i])
         for i in range(min(len(ruido), len(sweep)))]
    _salvar_wav("tela_azul.ogg", r, 0.5)


def gen_musica_creditos():
    """Créditos — nostálgico e reconfortante."""
    melodia = [523, 587, 659, 523, 523, 587, 659, 523,
               659, 698, 784, 659, 698, 784, 392, 440,
               494, 523, 392, 440, 494, 523, 784, 698,
               659, 587, 523, 494, 523, 0, 0, 0]
    dur = 0.15
    rep = 2
    pm = []
    for _ in range(rep):
        for freq in melodia:
            if freq == 0:
                pm.append(_silencio(dur))
            else:
                n = _triangular(freq, dur)
                n = _envelope(n, 0.01, dur * 0.3, dur * 0.35, dur * 0.35, sustain_level=0.65)
                pm.append(n)
    r = _concatenar(*pm)
    _salvar_wav("creditos.ogg", r, 0.35)


def gen_musica_ng_plus():
    """NG+ — misterioso, intenso, além do normal."""
    melodia = [349, 392, 415, 349, 330, 349, 392, 311,
               330, 349, 392, 440, 415, 392, 349, 330]
    baixo   = [87, 98, 103, 87, 82, 87, 98, 77,
               82, 87, 98, 110, 103, 98, 87, 82]
    dur = 0.10
    rep = 5
    pm, pb = [], []
    for _ in range(rep):
        for freq in melodia:
            n = _mix(
                _envelope(_quadrada(freq, dur), 0.003, dur * 0.2, dur * 0.5, dur * 0.3),
                _envelope(_triangular(freq * 1.5, dur), 0.003, dur * 0.2, dur * 0.5, dur * 0.3),
            )
            pm.append(n)
        for freq in baixo:
            n = _quadrada(freq * 2, dur)
            n = _envelope(n, 0.003, dur * 0.3, dur * 0.4, dur * 0.3, sustain_level=0.5)
            pb.append(n)
    m = _concatenar(*pm)
    b = _concatenar(*pb)
    n = min(len(m), len(b))
    r = [m[i] * 0.55 + b[i] * 0.45 for i in range(n)]
    _salvar_wav("ng_plus.ogg", r, 0.4)


if __name__ == "__main__":
    print("\n  🎵 Gerando sons pixel art para Tela Azul.py...\n")

    # SFX
    gen_nav()
    gen_confirmar()
    gen_cancelar()
    gen_inventario()
    gen_compra()
    gen_ouro()
    gen_level_up()
    gen_evolucao()
    gen_ataque()
    gen_magia()
    gen_critico()
    gen_cura()
    gen_vitoria()
    gen_derrota()
    gen_save()
    gen_load()
    gen_cidade_entra()
    gen_boss_entra()
    gen_interferencia()
    gen_bip()
    gen_erro()

    # Músicas
    gen_musica_menu()
    gen_musica_exploracao()
    gen_musica_combate()
    gen_musica_boss()
    gen_musica_boss_final()
    gen_musica_cidade()
    gen_musica_loja()
    gen_musica_tela_azul()
    gen_musica_creditos()
    gen_musica_ng_plus()

    print(f"\n  ✅ {21 + 10} arquivos gerados em assets/audio/")
    print("  Execute o jogo normalmente. Os sons serão carregados automaticamente.\n")
