import os
import sys
import time
from typing import Iterable, Optional

# Ensure Unicode box characters render properly on Windows consoles.
# If the terminal does not support UTF-8, we still avoid crashes by
# replacing unsupported characters instead of raising UnicodeEncodeError.
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
ITALIC  = "\033[3m"
CYAN    = "\033[36m"
BLUE    = "\033[34m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
RED     = "\033[31m"
MAGENTA = "\033[35m"
WHITE   = "\033[97m"
GRAY    = "\033[90m"
ORANGE  = "\033[38;5;208m"
PURPLE  = "\033[38;5;141m"


def cor(texto: str, codigo: str) -> str:
    return f"{codigo}{texto}{RESET}"


def limpar_tela() -> None:
    os.system("cls" if os.name == "nt" else "clear")


def pausar(segundos: float = 0.8) -> None:
    time.sleep(max(0.0, segundos))


def _limpar_buffer_teclas() -> None:
    try:
        import msvcrt  # type: ignore
        while msvcrt.kbhit():
            msvcrt.getwch()
        return
    except Exception:
        pass
    try:
        if sys.stdin.isatty():
            import select
            while True:
                pronto, _, _ = select.select([sys.stdin], [], [], 0)
                if not pronto:
                    break
                sys.stdin.read(1)
    except Exception:
        pass


def _enter_pressionado_nao_bloqueante() -> bool:
    try:
        import msvcrt  # type: ignore
        if msvcrt.kbhit():
            tecla = msvcrt.getwch()
            return tecla in {"\r", "\n"}
    except Exception:
        pass
    try:
        if sys.stdin.isatty():
            import select
            pronto, _, _ = select.select([sys.stdin], [], [], 0)
            if pronto:
                tecla = sys.stdin.read(1)
                return tecla in {"\r", "\n"}
    except Exception:
        pass
    return False


def texto_lento(texto: str, delay: float = 0.03, fim: str = "\n") -> None:
    delay = max(0.0, min(delay, 0.08))
    if delay <= 0:
        print(texto, end=fim, flush=True)
        return
    _tw_counter = 0
    for indice, caractere in enumerate(texto):
        if _enter_pressionado_nao_bloqueante():
            sys.stdout.write(texto[indice:])
            sys.stdout.write(fim)
            sys.stdout.flush()
            _limpar_buffer_teclas()
            return
        sys.stdout.write(caractere)
        sys.stdout.flush()
        # Som discreto de máquina de escrever — a cada 3 caracteres visíveis
        if caractere not in (" ", "\n", "\r"):
            _tw_counter += 1
            if _tw_counter % 3 == 1:
                try:
                    from src.audio import audio as _aud
                    _aud.sfx("typewriter")
                except Exception:
                    pass
        time.sleep(delay)
    sys.stdout.write(fim)
    sys.stdout.flush()


def linha(largura: int = 78, char: str = "═") -> str:
    return char * largura


def banner(titulo: str, subtitulo: Optional[str] = None, cor_borda: str = CYAN) -> None:
    largura = max(58, len(titulo) + 10)
    if subtitulo:
        largura = max(largura, len(subtitulo) + 6)
    print(cor("╔" + "═" * largura + "╗", cor_borda))
    meio = f" {titulo} "
    print(cor("║" + meio.center(largura) + "║", cor_borda))
    if subtitulo:
        print(cor("║" + subtitulo.center(largura) + "║", cor_borda))
    print(cor("╚" + "═" * largura + "╝", cor_borda))


def banner_decorado(titulo: str, subtitulo: Optional[str] = None) -> None:
    """Banner com estilo alternativo para momentos especiais."""
    largura = max(60, len(titulo) + 12)
    if subtitulo:
        largura = max(largura, len(subtitulo) + 8)
    print(cor("╔" + "═" * largura + "╗", MAGENTA))
    print(cor("║" + " " * largura + "║", MAGENTA))
    print(cor("║" + f" ★  {titulo}  ★ ".center(largura) + "║", YELLOW))
    if subtitulo:
        print(cor("║" + subtitulo.center(largura) + "║", ORANGE))
    print(cor("║" + " " * largura + "║", MAGENTA))
    print(cor("╚" + "═" * largura + "╝", MAGENTA))


def caixa(texto: str, largura: int = 78, cor_borda: str = CYAN) -> None:
    print(cor("╭" + "─" * largura + "╮", cor_borda))
    for linha_texto in texto.splitlines():
        print(cor("│ " + linha_texto.ljust(largura - 2)[:largura - 2] + " │", cor_borda))
    print(cor("╰" + "─" * largura + "╯", cor_borda))


def caixa_narrativa(texto: str) -> None:
    """Caixa especial para narração de história."""
    linhas = []
    palavras = texto.split()
    linha_atual = ""
    for palavra in palavras:
        if len(linha_atual) + len(palavra) + 1 <= 72:
            linha_atual = (linha_atual + " " + palavra).strip()
        else:
            linhas.append(linha_atual)
            linha_atual = palavra
    if linha_atual:
        linhas.append(linha_atual)

    print(cor("  ┌" + "─" * 74 + "┐", DIM))
    for l in linhas:
        print(cor("  │ ", DIM) + cor(l.ljust(73), ITALIC + WHITE) + cor("│", DIM))
    print(cor("  └" + "─" * 74 + "┘", DIM))


def continuar(mensagem: str = "\n  [ ENTER para continuar... ]") -> None:
    sys.stdout.flush()
    time.sleep(0.08)
    _limpar_buffer_teclas()
    input(cor(mensagem, DIM))


def menu_escolha(pergunta: str, opcoes: Iterable[str]) -> int:
    opcoes = list(opcoes)
    while True:
        print()
        texto_lento(pergunta, 0.03)
        for i, opcao in enumerate(opcoes, start=1):
            texto_lento(f"  {cor(f'[{i}]', CYAN)} {opcao}", 0.02)
        valor = input(cor("  Escolha: ", YELLOW)).strip()
        if valor.isdigit():
            indice = int(valor)
            if 1 <= indice <= len(opcoes):
                return indice
        print(cor("  Entrada inválida. Digite um número da lista.", RED))


def ler_texto(pergunta: str, padrao: str = "Herói") -> str:
    valor = input(pergunta).strip()
    return valor if valor else padrao


def progress_bar(valor: int, maximo: int, largura: int = 20) -> str:
    if maximo <= 0:
        maximo = 1
    proporcao = max(0.0, min(1.0, valor / maximo))
    preenchido = int(round(largura * proporcao))

    if proporcao > 0.6:
        cor_bar = GREEN
    elif proporcao > 0.3:
        cor_bar = YELLOW
    else:
        cor_bar = RED

    barra = "█" * preenchido + "░" * (largura - preenchido)
    return f"{cor_bar}[{barra}]{RESET}"


def exibir_estado(
    nome: str,
    hp: int,
    hp_max: int,
    mp: int = 0,
    mp_max: int = 0,
    level: int = 1,
    xp: int = 0,
    next_xp: int = 1,
) -> None:
    hp_bar = progress_bar(hp, hp_max)
    if mp_max > 0:
        mp_bar = progress_bar(mp, mp_max, largura=14)
        print(
            f"  {BOLD}{cor(nome, CYAN)}{RESET} {cor(f'Lv.{level}', YELLOW)} | "
            f"HP {hp_bar} {cor(f'{hp}/{hp_max}', WHITE)} | "
            f"MP {mp_bar} {cor(f'{mp}/{mp_max}', BLUE)} | "
            f"XP {cor(f'{xp}/{next_xp}', GRAY)}"
        )
    else:
        print(
            f"  {BOLD}{cor(nome, CYAN)}{RESET} {cor(f'Lv.{level}', YELLOW)} | "
            f"HP {hp_bar} {cor(f'{hp}/{hp_max}', WHITE)} | "
            f"XP {cor(f'{xp}/{next_xp}', GRAY)}"
        )


def confirmar(mensagem: str = "Confirmar? [s/n]: ") -> bool:
    while True:
        valor = input(cor(mensagem, YELLOW)).strip().lower()
        if valor in {"s", "sim", "y", "yes"}:
            return True
        if valor in {"n", "nao", "não", "no"}:
            return False
        print(cor("  Responda com s ou n.", RED))


def digitar_nome(prompt: str = "  Nome do personagem: ", padrao: str = "Jogador") -> str:
    valor = input(cor(prompt, CYAN)).strip()
    return valor if valor else padrao


def efeito_digitando(texto: str, delay: float = 0.05) -> None:
    """Efeito de terminal digitando — para momentos de narrativa intensos."""
    for ch in texto:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def separador(char: str = "─", largura: int = 78, color: str = DIM) -> None:
    print(cor(char * largura, color))
