"""
tela_azul.py — Evento da Falsa Tela Azul
Completamente simulado em terminal. Nenhuma API do sistema é tocada.
Nenhum reinício real. Nenhum BSOD real. Só teatro de terminal.
"""

import os
import sys
import time
import random
from pathlib import Path
from typing import Optional


# ─── Caminho raiz resolvido em relação a este arquivo ────────
_RAIZ      = Path(__file__).parent.parent
_SAVES_DIR = _RAIZ / "saves"

# ─── Flag de controle ────────────────────────────────────────
_FLAG_FILE = _SAVES_DIR / ".bsod_triggered"
_FLAG_NG   = _SAVES_DIR / ".ng_plus_unlocked"

# ─── Códigos de erro falsos ──────────────────────────────────
_STOP_CODES = [
    "KERNEL_DATA_INPAGE_ERROR",
    "CRITICAL_PROCESS_DIED",
    "SYSTEM_SERVICE_EXCEPTION",
    "MEMORY_MANAGEMENT",
    "PAGE_FAULT_IN_NONPAGED_AREA",
    "IRQL_NOT_LESS_OR_EQUAL",
    "UNEXPECTED_KERNEL_MODE_TRAP",
    "DRIVER_IRQL_NOT_LESS_OR_EQUAL",
    "CORRUPTED_KERNEL_STACK",
    "TERMINAL_RPG_EXCEPTION",
]

_ERROS_FALSOS = [
    "Collecting error information...",
    "Preparing automatic repair...",
    "Diagnosing your PC...",
    "Attempting repairs...",
    "Gathering system diagnostics...",
    "Writing memory dump to disk...",
    "Compressing crash data...",
]

_HEX_ADDR = [
    "0x000000000000007E",
    "0xC000021A",
    "0xC0000034",
    "0x00000050",
    "0xDEADC0DE",
    "0xBADC0FFE",
    "0xFF7F3A1B009E2C40",
    "0x00000000000000B8",
]


def _ja_foi_disparado() -> bool:
    return _FLAG_FILE.exists()


def _marcar_disparado() -> None:
    _SAVES_DIR.mkdir(parents=True, exist_ok=True)
    _FLAG_FILE.touch()
    _FLAG_NG.touch()


def ng_plus_desbloqueado() -> bool:
    return _FLAG_NG.exists()


def _limpar() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def _escrever(texto: str, delay: float = 0.0, fim: str = "\n") -> None:
    if delay <= 0:
        sys.stdout.write(texto + fim)
        sys.stdout.flush()
        return
    for ch in texto:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write(fim)
    sys.stdout.flush()


def _ruido(linhas: int = 3) -> None:
    """Imprime linhas de ruído hexadecimal estilo dump de memória."""
    for _ in range(linhas):
        addr = "".join(random.choices("0123456789ABCDEF", k=16))
        dados = " ".join(
            "".join(random.choices("0123456789ABCDEF", k=2)) for _ in range(16)
        )
        sys.stdout.write(f"  {addr}  {dados}\n")
        sys.stdout.flush()
        time.sleep(0.04)


def _barra_progresso_bsod(label: str, total_seg: float = 4.0, largura: int = 42) -> None:
    """Barra de progresso estilo Windows BSOD."""
    passos = 40
    delay = total_seg / passos
    for i in range(passos + 1):
        cheio = int(largura * i / passos)
        barra = "█" * cheio + " " * (largura - cheio)
        pct = int(100 * i / passos)
        sys.stdout.write(f"\r  {label} [{barra}] {pct}%   ")
        sys.stdout.flush()
        time.sleep(delay)
    print()


def _tela_bsod_windows(stop_code: str) -> None:
    """
    Simula visualmente a BSOD do Windows 10/11 em terminal.
    Fundo azul via ANSI. Apenas texto — nenhuma API do SO.
    """
    AZUL   = "\033[44m\033[97m"   # fundo azul, texto branco
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    DIMW   = "\033[2m"

    largura = 80

    def linha_azul(texto: str = "", centralizar: bool = False) -> None:
        if centralizar:
            texto = texto.center(largura)
        else:
            texto = texto.ljust(largura)
        sys.stdout.write(f"{AZUL}{texto}{RESET}\n")
        sys.stdout.flush()

    _limpar()

    # Preenche tudo de azul
    for _ in range(3):
        linha_azul()

    # Emoji de triste (QR code simulado)
    linha_azul()
    linha_azul("    :(", False)
    linha_azul()
    linha_azul(
        "    Your PC ran into a problem and needs to restart.",
        False
    )
    linha_azul(
        "    We're just collecting some error info, and then we'll",
        False
    )
    linha_azul("    restart for you.", False)
    linha_azul()
    linha_azul()

    # Barra de progresso — estilo nativo
    for pct in range(0, 101, 2):
        cheio = int(34 * pct / 100)
        barra = "█" * cheio + " " * (34 - cheio)
        linha_barra = f"    {pct}% complete  [{barra}]".ljust(largura)
        sys.stdout.write(f"\r{AZUL}{linha_barra}{RESET}")
        sys.stdout.flush()
        time.sleep(0.06 if pct < 85 else 0.14)
    print()

    linha_azul()
    linha_azul(
        f"    For more information about this issue and possible fixes, visit",
        False
    )
    linha_azul("    https://www.windows.com/stopcode", False)
    linha_azul()
    linha_azul(
        f"    If you call a support person, give them this info:",
        False
    )
    linha_azul(
        f"    Stop code: {BOLD}{stop_code}{RESET}{AZUL}".ljust(largura),
        False
    )
    linha_azul()
    linha_azul()
    linha_azul()

    # QR code fake (ASCII)
    qr_linhas = [
        "    ┌─────────────────┐  ",
        "    │ ▄▄▄ ▄  ▄▄ ▄▄▄ │  ",
        "    │ █▄█ ▄▄▄▄  █▄█ │  ",
        "    │ ▀▀▀ █▄▀▄  ▀▀▀ │  ",
        "    │ ▄▄▄▄█▀▄█▄▄▄▄  │  ",
        "    │ ▀ ▄▄ ▀▀ █▀▄ ▀ │  ",
        "    └─────────────────┘  ",
    ]
    for ql in qr_linhas:
        linha_azul(ql)

    for _ in range(5):
        linha_azul()

    time.sleep(1.2)


def _dump_de_memoria() -> None:
    """Simula output de dump de memória no terminal."""
    print()
    cores = ["\033[90m", "\033[33m", "\033[31m"]
    msgs = [
        "*** STOP: 0x0000007E (0xC0000005, 0xFFFFF880, 0xFFFFF880, 0xFFFFF880)",
        f"*** {random.choice(_STOP_CODES)}",
        "",
        "Collecting data for crash dump ...",
        "Initializing disk for crash dump ...",
        "Beginning dump of physical memory.",
        f"Dumping physical memory to disk: {random.choice(_HEX_ADDR)}",
        "",
    ]
    for m in msgs:
        cor = random.choice(cores)
        sys.stdout.write(f"{cor}  {m}\033[0m\n")
        sys.stdout.flush()
        time.sleep(0.08)
    _ruido(4)


def _sequencia_reinicializacao() -> None:
    """Simula mensagens de reinicialização após o BSOD."""
    msgs = [
        ("Reiniciando o sistema...", 0.05, 1.2),
        ("", 0.0, 0.5),
        ("BIOS v3.14.15-TERMINAL  2024", 0.03, 0.8),
        ("Detectando hardware...", 0.04, 1.0),
        ("", 0.0, 0.3),
        ("RAM: 16384 MB OK", 0.03, 0.4),
        ("CPU: Terminal RPG Engine @ 3.14 GHz", 0.03, 0.4),
        ("HDD: /dev/sda  [OK]", 0.03, 0.4),
        ("", 0.0, 0.5),
        ("Carregando sistema operacional...", 0.04, 1.5),
        ("", 0.0, 0.4),
        ("kernel: [    0.000000] Initializing cgroup subsys cpuset", 0.02, 0.2),
        ("kernel: [    0.000000] Linux version 6.1.0-terminal", 0.02, 0.2),
        ("kernel: [    0.181234] Memory: 16384K/16384K available", 0.02, 0.2),
        ("kernel: [    0.321456] ACPI: IRQ0 used by override.", 0.02, 0.2),
        ("kernel: [    0.512345] PCI: Using configuration type 1", 0.02, 0.2),
        ("", 0.0, 0.4),
        ("[  OK  ] Started Session Manager...", 0.03, 0.3),
        ("[  OK  ] Reached target Multi-User System.", 0.03, 0.3),
        ("[  OK  ] Started Terminal RPG Daemon...", 0.03, 0.4),
        ("", 0.0, 0.5),
    ]
    print()
    for texto, delay, pausa in msgs:
        _escrever(f"  {texto}" if texto else "", delay)
        time.sleep(pausa)


def _cutscene_pos_bsod() -> None:
    """Narrativa que roda quando o jogo reabre após a BSOD."""
    from src.utils import texto_lento, continuar, cor, limpar_tela, banner_decorado
    from src.utils import CYAN, YELLOW, MAGENTA, DIM, GRAY

    limpar_tela()
    time.sleep(0.5)

    # Terminal pisca
    for _ in range(3):
        sys.stdout.write("\033[5m_\033[0m")
        sys.stdout.flush()
        time.sleep(0.3)
        sys.stdout.write("\r ")
        sys.stdout.flush()
        time.sleep(0.2)
    print()

    banner_decorado("SISTEMA REINICIADO", "algo mudou")
    print()

    texto_lento("  ...", 0.08)
    time.sleep(0.8)
    texto_lento("  O terminal abre.", 0.04)
    time.sleep(0.4)
    texto_lento("  Você está de volta.", 0.04)
    time.sleep(0.5)
    texto_lento("  Mas algo está diferente.", 0.04)
    time.sleep(0.6)
    print()
    texto_lento(
        f"  {cor('As ruas estão iguais.', DIM)} "
        f"{cor('Os inimigos estão iguais.', DIM)}",
        0.03,
    )
    texto_lento(
        "  O mapa é o mesmo. Os nomes são os mesmos.",
        0.03,
    )
    texto_lento(
        f"  Mas você sente — na pele, nos ossos, no código — que {cor('algo foi reescrito.', YELLOW)}",
        0.03,
    )
    print()
    texto_lento(
        "  Ninguém vai falar sobre a Tela Azul. Ninguém vai confirmar o que aconteceu.",
        0.03,
    )
    texto_lento(
        "  Mas as pessoas falam diferente. Os lugares parecem levemente fora de lugar.",
        0.03,
    )
    texto_lento(
        f"  E no canto do terminal, uma nova porta apareceu. {cor('Nunca esteve lá antes.', MAGENTA)}",
        0.03,
    )
    print()
    texto_lento(
        f"  {cor('[SISTEMA]', CYAN)} Novo conteúdo desbloqueado: {cor('BEYOND THE KERNEL', YELLOW)}",
        0.03,
    )
    texto_lento(
        f"  {cor('[SISTEMA]', CYAN)} Modo NG+ disponível no menu principal.",
        0.03,
    )
    print()
    continuar("\n  [ ENTER para continuar... ]")


def disparar_tela_azul(jogador_nome: str = "") -> None:
    """
    Ponto de entrada principal do evento.
    Salvar deve ter sido feito antes de chamar esta função.
    """
    # Import tardio para evitar circular (audio <- utils <- tela_azul <- combate <- audio)
    from src.audio import audio as _audio

    stop_code = random.choice(_STOP_CODES)

    # Sequência sonora (não crítica — áudio pode não estar disponível)
    _audio.sequencia_bsod()

    # Pequena pausa dramática antes do blackout
    time.sleep(0.8)

    # Blackout
    _limpar()
    time.sleep(0.4)

    # Ruído de fundo
    _dump_de_memoria()
    time.sleep(0.6)

    # BSOD principal
    _tela_bsod_windows(stop_code)
    time.sleep(0.8)

    # "Reiniciando..."
    _limpar()
    _sequencia_reinicializacao()

    # Fecha o processo de forma abrupta — experiência de que o jogo fechou
    _limpar()
    print()
    print("  Pressione qualquer tecla para iniciar...")
    print()
    try:
        input()
    except Exception:
        pass

    # Marca flag e abre cutscene de retorno
    _marcar_disparado()


def verificar_e_exibir_retorno() -> bool:
    """
    Chamado no início do main() após carregar o save.
    Retorna True se acabou de voltar de uma BSOD (mostra cutscene).
    """
    flag_retorno = _SAVES_DIR / ".bsod_retorno"
    if flag_retorno.exists():
        flag_retorno.unlink()
        _cutscene_pos_bsod()
        return True
    return False


def deve_disparar_bsod(indice_encontro: int, total_encontros: int, boss_final_morreu: bool) -> bool:
    """
    Lógica de quando disparar: metade da campanha OU após boss final.
    Só dispara uma vez por save.
    """
    if _ja_foi_disparado():
        return False
    if boss_final_morreu:
        return True
    # metade da campanha (após o encontro central)
    meio = total_encontros // 2
    return indice_encontro == meio


def preparar_retorno_pos_bsod() -> None:
    """
    Cria flag que indica que o jogo deve mostrar cutscene de retorno.
    Chamar ANTES de disparar_tela_azul().
    """
    flag_retorno = _SAVES_DIR / ".bsod_retorno"
    flag_retorno.parent.mkdir(parents=True, exist_ok=True)
    flag_retorno.touch()
