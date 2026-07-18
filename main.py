import sys
import time
import random
from pathlib import Path
from typing import Optional, Tuple

from src.utils import (
    limpar_tela, banner, banner_decorado, texto_lento, continuar,
    menu_escolha, cor, caixa_narrativa, separador, pausar, digitar_nome,
    CYAN, YELLOW, GREEN, RED, MAGENTA, GRAY, BOLD, RESET, DIM, WHITE, ORANGE,
)

from src.player import Personagem
from src.enemy import (
    criar_inimigos, criar_bosses,
    criar_inimigos_ng, criar_bosses_ng,
    criar_inimigos_recrutador, criar_bosses_recrutador,
)
from src.combate import (
    Combate, tela_gerenciar_saves, carregar_de_slot,
    resumo_slot, salvar_em_slot,
)
from src.world import (
    cidade_porto_zero, cidade_nexo_profundo,
    cidade_forja_binaria, cidade_santuario_suspenso,
    cidade_setor_esquecido, cidade_camara_void, cidade_arquivo_proibido,
    evento_caminho, evento_caminho_ng,
    abrir_loja,
)
from src.audio import audio as _audio

# ── Caminho absoluto de saves (compatível com qualquer CWD) ──
_SAVE_DIR = Path(__file__).parent / "saves"

# ─────────────────────────────────────────────────────────────
#  DETECÇÃO DE GÊNERO — mantida para compatibilidade com saves antigos
# ─────────────────────────────────────────────────────────────
_NOMES_FEMININOS = {
    "ana","maria","julia","juliana","gabriela","fernanda","camila","larissa",
    "leticia","letícia","beatriz","bianca","bruna","carol","carolina","carla",
    "clara","alice","amanda","andressa","aline","debora","débora","elisa",
    "erica","érica","giovana","heloisa","heloise","isis","jade","jessica",
    "jéssica","joana","laura","lara","luana","lucia","luciana","luisa","luísa",
    "luna","lydia","manuela","mariana","marina","milena","monica","mônica",
    "natalia","natália","nathalia","nathalie","nicole","olivia","patricia",
    "patrícia","paula","priscila","rafaela","raquel","rebeca","renata",
    "sabrina","sara","sarah","sofia","stephanie","stéphanie","talita","talia",
    "tatiana","thais","thaís","valentina","vanessa","veronica","vitoria",
    "vitória","viviane","yasmin",
}


def detectar_genero(nome: str) -> str:
    primeiro = nome.strip().lower().split()[0] if nome.strip() else ""
    if primeiro in _NOMES_FEMININOS:
        return "f"
    if primeiro.endswith("a") and primeiro not in {"lua", "era", "para"}:
        return "f"
    return "m"


# ─────────────────────────────────────────────────────────────
#  SITES SUGESTIVOS (nomes paródia)
# ─────────────────────────────────────────────────────────────
_SITES_MASC = {
    "1": "Cornhub",
    "2": "Xvrideos",
    "3": "Beeg.tv",
    "4": "Sambanoito",
    "5": "Youtubr",
}

_SITES_FEM = {
    "1": "Cornhub",
    "2": "Xvrideos",
    "3": "Privaacy",
    "4": "CasadasSafadas",
}

_ATRIZES = ["Vivi Fernandes", "Gretchen", "Rita Cadillac", "Regininha Poltergeist"]


def _intro_site_masc(nome: str, key: str) -> None:
    site = _SITES_MASC.get(key, "Cornhub")
    texto_lento(f"\n  Você abre o {cor(site, MAGENTA)} quase no automático.", 0.03)
    pausar(0.3)
    if key == "5":
        texto_lento(
            "  Você procura algo pra ver enquanto espera. Dez minutos viram cinquenta.", 0.03)
        texto_lento(
            "  GPU unboxing, framerate de jogo que você não tem placa pra rodar, "
            "compilação de fails de parkour que ninguém pediu.", 0.03)
        texto_lento(
            f"  Ao final do décimo segundo vídeo recomendado, {nome} para e pensa: "
            "\"Como cheguei aqui?\". Não tem resposta. Nunca tem.", 0.03)
        pausar(0.3)
        texto_lento(
            "  Vinte minutos assistindo tutorial de como dobrar camiseta. "
            "As camisetas continuam uma bagunça.", 0.03)
    elif key == "4":
        texto_lento("  Você quer algo mais nacional. Raiz. Com sotaque.", 0.03)
        print()
        for i, a in enumerate(_ATRIZES, 1):
            print(f"    {cor(f'[{i}]', CYAN)} {a}")
        esc = input(cor("\n  Qual você vai procurar? ", YELLOW)).strip()
        atriz = _ATRIZES[int(esc)-1] if esc.isdigit() and 1 <= int(esc) <= 4 else "Vivi Fernandes"
        texto_lento(f"\n  Você busca por {cor(atriz, YELLOW)} e encontra o que precisava.", 0.03)
        texto_lento(
            "  O material é antigo mas o clássico não envelhece. "
            "A cadeira reclina, a temperatura do quarto sobe alguns graus.", 0.03)
        texto_lento(
            "  Alguns minutos depois você está satisfeito, levemente exausto "
            "e com adrenalina no ponto certo.", 0.03)
    else:
        texto_lento(
            "  Você abre quatro abas sem pensar duas vezes. "
            "Direto ao ponto, sem enrolação. Eficiência.", 0.03)
        texto_lento(
            "  Minutos depois está satisfeito, com adrenalina no ponto certo "
            "e pronto pra encarar qualquer boss.", 0.03)


def _intro_site_fem(nome: str, key: str) -> None:
    site = _SITES_FEM.get(key, "Cornhub")
    texto_lento(
        f"\n  Você abre o {cor(site, MAGENTA)} com aquela curiosidade específica de quem sabe o que quer.",
        0.03)
    pausar(0.3)
    if key == "3":
        texto_lento("  Você entra na sua conta, liga a câmera, e em segundos as notificações começam.", 0.03)
        texto_lento(
            "  Você controla o show do seu jeito — um sorriso aqui, um olhar ali. "
            "Tem arte nisso, mesmo que ninguém queira admitir.", 0.03)
        texto_lento(
            "  Uma hora depois você desliga tudo, fecha o notebook, "
            "e se sente completamente no controle.", 0.03)
    elif key == "4":
        nomes_vizinho = ["Rafael", "Bruno", "Cauã", "Diego", "Thiago"]
        vizinho = random.choice(nomes_vizinho)
        texto_lento(
            f"  Você entra no bate-papo por proximidade e lá está: {cor(vizinho, YELLOW)}. "
            "Seu vizinho. Casado. Musculoso. Inconvenientemente atraente.", 0.03)
        texto_lento(
            f"  Você e {vizinho} trocam mensagens que começam inocentes e terminam menos inocentes. "
            "A tensão acumulada de meses de corredores estreitos finalmente encontra um lugar pra ir.",
            0.03)
        texto_lento(
            "  A conversa termina. Você fecha o chat. Respira fundo. "
            "Está satisfeita com o nível de entretenimento disponível.", 0.03)
    else:
        texto_lento(
            "  O conteúdo aparece e você vai afundando na cadeira gamer aos poucos, "
            "o olhar fixo na tela.", 0.03)
        texto_lento(
            "  Alguns minutos depois você está levemente corada, "
            "completamente satisfeita e com energia pra jogar até de madrugada.", 0.03)


def introducao(nome: str, sexo: str) -> None:
    limpar_tela()
    banner_decorado("UM QUARTO. UM PC. UM ERRO.", "A história começa antes de você perceber.")
    pausar(0.5)

    sua = "sua" if sexo == "f" else "seu"
    entediad = "entediada" if sexo == "f" else "entediado"
    satisfeit = "satisfeita" if sexo == "f" else "satisfeito"
    sufixo_o_a = "a" if sexo == "f" else "o"

    texto_lento(f"\n  {nome}. Terça-feira. 23h47.", 0.03)
    pausar(0.3)
    texto_lento(
        f"  O teto do {sua} quarto não tem nada de interessante, "
        "mas você ficou olhando pra ele por quase dez minutos assim mesmo.", 0.03)
    texto_lento(
        f"  {entediad.capitalize()}. Não é o tipo de tédio que passa com Netflix. "
        "É o tédio profundo, existencial, que só um bom jogo resolve.", 0.03)
    continuar()

    texto_lento(
        f"  Você liga o PC. A ventoinha faz aquele barulho de sempre — "
        "um aviso antigo de que a máquina ainda está viva.", 0.03)
    texto_lento("  Você abre o Discord no automático. O servidor de tecnologia está agitado.", 0.03)
    pausar(0.3)
    caixa_narrativa(
        "Mateus_Dev: 'cara BAIXA O TELA AZUL.py agora'\n"
        "Kenji_404: 'sério isso tá insano'\n"
        "Mateus_Dev: 'tem boss que travou minha cabeça por 2 dias'\n"
        "xX_null_ptr_Xx: 'MEU DEUS esse jogo mexe com a cabeça'\n"
        "Kenji_404: 'já zerei 3x e ainda acho coisa nova'\n"
        "Mateus_Dev: 'baixa. simplesmente baixa.'"
    )
    pausar(0.4)
    text_curioso = "curiosa" if sexo == "f" else "curioso"
    texto_lento(
        f"  Você fica {text_curioso}. Esse tipo de hype no servidor é raro — "
        "geralmente é gente brigando por tabs vs espaços.", 0.03)
    continuar()

    texto_lento("  Você procura o jogo. Google. DuckDuckGo. Reddit.", 0.03)
    texto_lento(
        "  Encontra um site. Botão de download. "
        "O arquivo é menor do que deveria ser pra um jogo assim.", 0.03)
    texto_lento("  Você baixa mesmo assim. Claro que baixa.", 0.03)

    texto_lento(f"\n  {cor('Download: 0%', GRAY)} ........", 0.02)
    for p in range(0, 101, 10):
        time.sleep(0.12)
        barra = "█" * (p // 5) + "░" * (20 - p // 5)
        sys.stdout.write(f"\r  {cor(f'Download: {p}%', GREEN)} [{barra}]   ")
        sys.stdout.flush()
    print()
    pausar(0.3)
    texto_lento("  Download concluído. Instalação: automática. Estimativa: 4 minutos.", 0.03)
    continuar()

    texto_lento(f"\n  Quatro minutos. Você precisa matar o tempo de alguma forma.", 0.03)
    pausar(0.3)

    print()
    texto_lento("  Você abre uma nova aba.", 0.03)
    if sexo == "m":
        for k, s in _SITES_MASC.items():
            print(f"    {cor(f'[{k}]', CYAN)} {s}")
        key = input(cor("\n  Qual você abre? ", YELLOW)).strip()
        if key not in _SITES_MASC:
            key = "1"
        _intro_site_masc(nome, key)
    else:
        for k, s in _SITES_FEM.items():
            print(f"    {cor(f'[{k}]', CYAN)} {s}")
        key = input(cor("\n  Qual você abre? ", YELLOW)).strip()
        if key not in _SITES_FEM:
            key = "1"
        _intro_site_fem(nome, key)

    pausar(0.5)
    print()
    texto_lento(
        "  " + cor("[ SISTEMA ] ", CYAN) + cor("TELA AZUL.py — Pronto para iniciar.", YELLOW), 0.02)
    pausar(0.4)
    texto_lento(
        f"  Você fecha a aba. Respira. Se sente {satisfeit} e um pouco mais "
        f"acord{sufixo_o_a}.", 0.03)
    texto_lento("  O jogo está esperando. Você clica em iniciar sem hesitar.", 0.03)
    pausar(0.3)
    texto_lento("  A tela escurece.", 0.03)
    pausar(0.5)
    texto_lento("  E aí começa a parte estranha.", 0.03)
    continuar(f"\n  {cor('[ ENTER para jogar... ]', YELLOW)}")


# ─────────────────────────────────────────────────────────────
#  CRIAÇÃO DE PERSONAGEM
# ─────────────────────────────────────────────────────────────
def _escolher_sexo() -> str:
    limpar_tela()
    banner("IDENTIDADE DO PERSONAGEM", "Essa escolha adapta pronomes e diálogos.")
    print()
    texto_lento("  Com qual gênero seu personagem se identifica?", 0.03)
    print()
    print(f"  {cor('[1]', CYAN)} Masculino")
    print(f"  {cor('[2]', CYAN)} Feminino")
    print()
    while True:
        esc = input(cor("  Escolha: ", YELLOW)).strip()
        if esc == "1":
            return "m"
        if esc == "2":
            return "f"
        print(cor("  Digite 1 ou 2.", RED))


def criar_jogador() -> Personagem:
    limpar_tela()
    banner("CRIAR PERSONAGEM", "Quem você vai ser nesse caos?")
    texto_lento(
        "\n  Antes de tudo: um nome. Pensa bem. "
        "Esse nome vai aparecer bastante nas próximas horas.", 0.03)
    print()
    nome = digitar_nome("  Nome do personagem: ")

    sexo = _escolher_sexo()

    limpar_tela()
    banner("ESCOLHER CLASSE", f"{'Bem-vinda' if sexo == 'f' else 'Bem-vindo'}, {nome}.")
    texto_lento(
        "\n  Cada classe tem um estilo diferente de sobreviver. "
        "Não existe errado — existe o que combina com você.", 0.03)
    print()
    classe = Personagem.escolher_classe_interativa()
    jogador = Personagem(nome, classe, sexo)

    limpar_tela()
    banner("PERSONAGEM CRIADO", f"{nome} — {classe}")
    print()
    texto_lento(f"  Nome:   {cor(nome, CYAN)}", 0.03)
    texto_lento(f"  Sexo:   {'Feminino' if sexo == 'f' else 'Masculino'}", 0.03)
    texto_lento(f"  Classe: {cor(classe, YELLOW)}", 0.03)
    texto_lento(f"  Skill:  {cor(jogador.skill, MAGENTA)}", 0.03)
    texto_lento(
        f"  HP: {jogador.hp_max} | MP: {jogador.mp_max} | "
        f"ATK: {jogador.dano} | DEF: {jogador.defesa}", 0.03)
    print()
    texto_lento("  Itens iniciais: 2x Poção HP, 1x Poção MP, 1x Bomba, 1x Antídoto.", 0.03)
    continuar("\n  [ ENTER para continuar... ]")

    introducao(nome, sexo)
    return jogador


# ─────────────────────────────────────────────────────────────
#  SELEÇÃO DE SAVE
# ─────────────────────────────────────────────────────────────
def tela_selecionar_save() -> Tuple[Optional[Personagem], int]:
    limpar_tela()
    banner("CARREGAR PARTIDA", "Escolha um slot")
    print()
    slots_com_save = []
    for i in range(1, 4):
        tem = (_SAVE_DIR / f"slot_{i}.json").exists()
        if tem:
            slots_com_save.append(i)
        print(f"  {cor(f'Slot {i}', CYAN)}: {resumo_slot(i)}")
    print()
    if not slots_com_save:
        texto_lento("  Nenhuma partida salva encontrada.", 0.03)
        continuar()
        return None, 1
    opcoes = [f"Carregar Slot {i}" for i in slots_com_save] + ["Voltar"]
    escolha = menu_escolha("Qual slot carregar?", opcoes)
    if escolha > len(slots_com_save):
        return None, 1
    slot = slots_com_save[escolha - 1]
    jog = carregar_de_slot(slot)
    if jog is None:
        texto_lento(f"  Erro ao carregar Slot {slot}.", 0.03)
        continuar()
        return None, 1
    suf = "a" if jog.sexo == "f" else "o"
    limpar_tela()
    banner("PARTIDA CARREGADA", f"Bem-vind{suf} de volta, {jog.nome}.")
    texto_lento(f"  Classe: {jog.classe_atual} | Nível: {jog.level}", 0.03)
    texto_lento(f"  HP: {jog.hp}/{jog.hp_max} | MP: {jog.mp}/{jog.mp_max}", 0.03)
    if jog.mundo_alterado:
        texto_lento(f"  {cor('[O mundo foi alterado]', MAGENTA)}", 0.03)
    if jog.ng_plus:
        texto_lento(f"  {cor('[NG+ — Beyond the Kernel]', YELLOW)}", 0.03)
    continuar()
    return jog, slot


# ─────────────────────────────────────────────────────────────
#  MONTAGEM DOS ENCONTROS — CAMPANHA PRINCIPAL
# ─────────────────────────────────────────────────────────────
def montar_encontros(jogador: Personagem):
    mobs   = criar_inimigos()
    bosses = criar_bosses()
    ma = jogador.mundo_alterado

    def ev(cap):
        return lambda j: evento_caminho(j, cap)

    return [
        # ── Capítulo 1
        {
            "titulo": "Capítulo 1 — Ruas Corrompidas",
            "narrativa": (
                "O jogo carrega. A tela fica preta por um segundo a mais que deveria. "
                "Quando abre, você não está num menu. Está numa rua. "
                "Uma rua de código, com lixo digital nas calçadas e sinais que piscam sem parar."
            ) if not ma else (
                "As ruas estão iguais. Os inimigos estão iguais. "
                "Mas você não está igua. Você passou pela tela azul. Voltou. "
                "Cada criatura aqui sente isso — e nenhuma sabe o que fazer com isso."
            ),
            "inimigo": mobs[0], "evento": ev(1),
        },
        {
            "titulo": "Capítulo 1 — Ruas Corrompidas",
            "narrativa": "Você derrubou o primeiro. Mas o sistema não gosta de visitantes.",
            "inimigo": mobs[1],
        },
        {
            "titulo": "Capítulo 1 — Ruas Corrompidas",
            "narrativa": "As ruas ficam mais densas. Algo maior se forma no final da avenida.",
            "inimigo": mobs[2], "evento": ev(1),
        },
        {
            "titulo": "Capítulo 1 — Ruas Corrompidas",
            "narrativa": "Você quase pode ver o guardião do bairro daqui. Mas antes, mais um.",
            "inimigo": mobs[3],
        },
        {
            "titulo": "Capítulo 1 — Boss: Capetão do Stack",
            "narrativa": (
                "Ele está no final da rua, bloqueando a única saída."
            ) if not ma else (
                "O Capetão do Stack está no mesmo lugar. Mas hesita um momento antes de atacar. "
                "Ele nunca fez isso antes."
            ),
            "inimigo": bosses[0],
        },
        # ── Capítulo 2
        {
            "titulo": "Capítulo 2 — Túnel de Latência",
            "narrativa": "Você entrou no túnel. A rede gagueja. Seus movimentos chegam com atraso.",
            "inimigo": mobs[4], "cidade": cidade_porto_zero, "evento": ev(2),
        },
        {
            "titulo": "Capítulo 2 — Túnel de Latência",
            "narrativa": "O túnel não tem fim visível. Só tem próximo inimigo.",
            "inimigo": mobs[5], "evento": ev(2),
        },
        {
            "titulo": "Capítulo 2 — Boss: Rainha da Latência",
            "narrativa": "Ela existe no espaço entre um frame e outro.",
            "inimigo": bosses[1],
        },
        # ── Capítulo 3
        {
            "titulo": "Capítulo 3 — Arsenal de Dados",
            "narrativa": "As estruturas antigas desmoronam. Cada bloco que cai libera criatura.",
            "inimigo": mobs[6], "cidade": cidade_nexo_profundo, "evento": ev(3),
        },
        {
            "titulo": "Capítulo 3 — Arsenal de Dados",
            "narrativa": "O arsenal é vasto. Você não consegue ver o outro lado.",
            "inimigo": mobs[7], "evento": ev(3),
        },
        {
            "titulo": "Capítulo 3 — Boss: Arquiteto de Ruínas",
            "narrativa": "Ele construiu esse lugar. Ele também o está destruindo, de propósito.",
            "inimigo": bosses[2],
        },
        # ── Capítulo 4
        {
            "titulo": "Capítulo 4 — Núcleo Sombrio",
            "narrativa": "O núcleo pulsa. Você sente a vibração antes de ouvir o som.",
            "inimigo": mobs[8], "cidade": cidade_forja_binaria, "evento": ev(4),
        },
        {
            "titulo": "Capítulo 4 — Núcleo Sombrio",
            "narrativa": "Mais fundo. Mais quente. A lógica aqui é diferente.",
            "inimigo": mobs[9], "evento": ev(4),
        },
        {
            "titulo": "Capítulo 4 — Boss: Guardião do Kernel",
            "narrativa": "Ele não guarda o núcleo porque foi colocado aqui. Ele escolheu.",
            "inimigo": bosses[3],
        },
        # ── Capítulo 5
        {
            "titulo": "Capítulo 5 — Trono do Caos",
            "narrativa": "Você chegou. O trono não é um lugar físico. É um estado do sistema.",
            "inimigo": mobs[10], "cidade": cidade_santuario_suspenso, "evento": ev(5),
        },
        {
            "titulo": "Capítulo 5 — Trono do Caos",
            "narrativa": "Última linha antes do fim. Ainda está de pé.",
            "inimigo": mobs[11], "evento": ev(5),
        },
        {
            "titulo": "Boss Final: Imperador do Caos",
            "narrativa": (
                "\"Eu sabia que alguém chegaria até aqui.\", ele diz. "
                "\"Só não sabia se você seria suficiente.\""
            ) if not ma else (
                "O Imperador olha pra você diferente desta vez. "
                "\"Você foi além.\", ele diz. \"Mas isso muda o que você vai encontrar depois.\""
            ),
            "inimigo": bosses[4],
        },
    ]


# ─────────────────────────────────────────────────────────────
#  MONTAGEM — NEW GAME+
# ─────────────────────────────────────────────────────────────
def montar_encontros_ng(jogador: Personagem):
    mobs_ng   = criar_inimigos_ng()
    bosses_ng = criar_bosses_ng()

    def ev_ng(j):
        evento_caminho_ng(j, 1)

    return [
        # ── Setor Esquecido
        {
            "titulo": "NG+ — Setor Esquecido",
            "narrativa": (
                "Além do Imperador do Caos, há um setor que não aparece em nenhum mapa. "
                "Você chegou aqui por causa da tela azul. Ou a tela azul aconteceu para te trazer até aqui."
            ),
            "inimigo": mobs_ng[0], "evento": ev_ng,
        },
        {
            "titulo": "NG+ — Setor Esquecido",
            "narrativa": "Os ecos do sistema resistem. Mas sabem que você já foi além.",
            "inimigo": mobs_ng[1], "evento": ev_ng,
        },
        {
            "titulo": "NG+ — Boss 1: Overseer do Setor",
            "narrativa": (
                "O Overseer administra o que foi esquecido. "
                "Ele não esperava visita — especialmente não sua."
            ),
            "inimigo": bosses_ng[0],
        },
        # ── Câmara Void
        {
            "titulo": "NG+ — Câmara Void",
            "narrativa": "Além do Setor, a realidade fica mais fina. Mais honesta.",
            "inimigo": mobs_ng[2], "cidade": cidade_setor_esquecido, "evento": ev_ng,
        },
        {
            "titulo": "NG+ — Câmara Void",
            "narrativa": "A Câmara Void não tem paredes visíveis. Tem bordas que mudam.",
            "inimigo": mobs_ng[3], "evento": ev_ng,
        },
        {
            "titulo": "NG+ — Câmara Void",
            "narrativa": "Você está mais fundo do que qualquer pessoa deveria estar.",
            "inimigo": mobs_ng[4], "evento": ev_ng,
        },
        {
            "titulo": "NG+ — Câmara Void",
            "narrativa": "O Void começa a te reconhecer. Isso é bom e péssimo ao mesmo tempo.",
            "inimigo": mobs_ng[5],
        },
        {
            "titulo": "NG+ — Boss 2: Núcleo Corrompido",
            "narrativa": (
                "O Núcleo Corrompido não foi criado. Foi o que sobrou depois que tudo mais falhou."
            ),
            "inimigo": bosses_ng[1],
        },
        # ── Arquivo Proibido / Boss Final NG+
        {
            "titulo": "NG+ — Arquivo Proibido",
            "narrativa": "O Arquivo Proibido guarda o que o sistema não quer que ninguém saiba.",
            "inimigo": mobs_ng[6], "cidade": cidade_camara_void, "evento": ev_ng,
        },
        {
            "titulo": "NG+ — Arquivo Proibido",
            "narrativa": "Você está perto. O Vazio sente isso.",
            "inimigo": mobs_ng[7], "evento": ev_ng,
        },
        {
            "titulo": "NG+ — Antecâmara do Vazio",
            "narrativa": "Não tem mais inimigos aleatórios aqui. Só propósito.",
            "inimigo": mobs_ng[8], "cidade": cidade_arquivo_proibido,
        },
        {
            "titulo": "NG+ — Antecâmara do Vazio",
            "narrativa": "A última linha antes do VAZIO.",
            "inimigo": mobs_ng[9],
        },
        {
            "titulo": "NG+ — BOSS FINAL: O VAZIO",
            "narrativa": (
                "O VAZIO não fala. Não precisa. "
                "Você sabe o que ele quer — encerrar tudo. "
                "Você sabe o que você quer — que ele não consiga."
            ),
            "inimigo": bosses_ng[2],
        },
    ]


# ─────────────────────────────────────────────────────────────
#  MONTAGEM — MODO RECRUTADOR
# ─────────────────────────────────────────────────────────────
def montar_encontros_recrutador(jogador: Personagem):
    mobs   = criar_inimigos_recrutador()
    bosses = criar_bosses_recrutador()

    def loja_rapida(j):
        abrir_loja(j, "Mercado do Demo")

    return [
        {
            "titulo": "Demo — Primeiro Contato",
            "narrativa": (
                "Você entrou num sistema desconhecido. Não sabe como chegou aqui. "
                "Só sabe que tem algo no caminho e precisa passar."
            ),
            "inimigo": mobs[0],
        },
        {
            "titulo": "Demo — Escalando",
            "narrativa": "O sistema resiste. Os inimigos ficam mais espertos conforme avança.",
            "inimigo": mobs[1], "cidade": loja_rapida,
        },
        {
            "titulo": "Demo — Boss 1: Gerente de Projeto",
            "narrativa": (
                "O Gerente de Projeto não é um inimigo físico. "
                "É uma ideia — a ideia de que cada progresso gera mais trabalho. "
                "No sistema, ela ganhou forma."
            ),
            "inimigo": bosses[0],
        },
        {
            "titulo": "Demo — Profundidade",
            "narrativa": "Além do Gerente há código mais velho. Mais resistente. Mais teimoso.",
            "inimigo": mobs[2], "cidade": loja_rapida,
        },
        {
            "titulo": "Demo — Último Obstáculo",
            "narrativa": "Você está quase fora. Mas o sistema tem uma última coisa a dizer.",
            "inimigo": mobs[3],
        },
        {
            "titulo": "Demo — Boss Final: O Sistema Legado",
            "narrativa": (
                "Ninguém entende o Sistema Legado. "
                "Ele mesmo não se entende mais. "
                "Mas continua rodando — e continuará, a menos que alguém o pare."
            ),
            "inimigo": bosses[1],
        },
    ]


# ─────────────────────────────────────────────────────────────
#  MODO RECRUTADOR
# ─────────────────────────────────────────────────────────────
def modo_recrutador() -> None:
    limpar_tela()
    banner_decorado("MODO RECRUTADOR", "Demo independente — 20 a 35 minutos")
    print()
    texto_lento(
        "  Uma versão compacta e independente de Tela Azul.py. "
        "História própria, final próprio.", 0.03)
    texto_lento(
        "  Se você terminar querendo mais — a campanha completa está no menu principal.",
        0.03)
    print()
    continuar()

    nome = digitar_nome("  Nome do personagem (demo): ")
    sexo = _escolher_sexo()

    limpar_tela()
    banner("DEMO — CLASSE", f"{'Bem-vinda' if sexo == 'f' else 'Bem-vindo'}, {nome}.")
    print()
    texto_lento("  Escolha uma classe para o demo:", 0.03)
    print()
    classe = Personagem.escolher_classe_interativa()
    jogador = Personagem(nome, classe, sexo)

    # Boost inicial para o demo ser completável em 20-35min
    jogador.dano   += 5
    jogador.defesa += 3
    jogador.hp_max += 30
    jogador.mp_max += 20
    jogador.hp = jogador.hp_max
    jogador.mp = jogador.mp_max
    jogador.ouro = 60
    jogador.adicionar_item("pocao_hp", 2)
    jogador.adicionar_item("bomba", 1)

    limpar_tela()
    banner("DEMO — INÍCIO", "O sistema te recebeu. Mal.")
    texto_lento(
        "\n  Você abriu o terminal. O terminal te puxou pra dentro. "
        "Não é a primeira vez que isso acontece com alguém. "
        "É a primeira vez que alguém volta pra contar.", 0.03)
    texto_lento(
        "  O objetivo é simples: atravesse o sistema. "
        "Derrube o que precisar ser derrubado. Saia pelo outro lado.", 0.03)
    continuar()

    _audio.tocar_musica("exploracao")

    encontros = montar_encontros_recrutador(jogador)
    combate = Combate(jogador, encontros, slot_ativo=0)

    resultado = combate.iniciar()

    limpar_tela()
    if resultado in ("vitoria", "vitoria_ng"):
        banner_decorado("FIM DO DEMO", "Você chegou onde poucos chegam.")
        print()
        texto_lento(
            "  Você saiu do sistema. O terminal fechou. "
            "O quarto está igual. Mas você está diferente.", 0.03)
        texto_lento(
            f"\n  {cor(nome, CYAN)} | {cor(jogador.classe_atual, YELLOW)} | "
            f"Nível {jogador.level} | {jogador.ouro}g", 0.03)
        print()
        texto_lento(
            f"  {cor('→', GREEN)} A campanha completa tem 5 capítulos, 12 mobs, 5 bosses,", 0.03)
        texto_lento(
            "     sistema de evolução de classe, 4 cidades, eventos de caminho,", 0.03)
        texto_lento(
            "     e um segredo que você só descobre jogando até o fim.", 0.03)
        texto_lento(
            f"  {cor('→', GREEN)} Disponível no menu principal: Nova Partida.", 0.03)
    else:
        banner("FIM DO DEMO", "Não foi desta vez.", RED)
        print()
        texto_lento(
            "  O sistema venceu. Mas você chegou mais longe do que a maioria.", 0.03)
        texto_lento(
            "  A campanha completa tem mais recursos, mais itens, mais espaço pra crescer.", 0.03)
    print()
    continuar("\n  [ ENTER para voltar ao menu... ]")

    _audio.tocar_musica("menu")


# ─────────────────────────────────────────────────────────────
#  LOOP DE JOGO
# ─────────────────────────────────────────────────────────────
def _escolher_slot_e_jogar(jogador: Personagem) -> None:
    limpar_tela()
    banner("SALVAR NOVA PARTIDA", "Escolha onde salvar")
    print()
    for i in range(1, 4):
        print(f"  {cor(f'Slot {i}', CYAN)}: {resumo_slot(i)}")
    print()
    opcoes = ["Salvar no Slot 1", "Salvar no Slot 2", "Salvar no Slot 3"]
    escolha = menu_escolha("Em qual slot quer salvar?", opcoes)
    slot = escolha
    salvar_em_slot(jogador, slot)
    texto_lento(f"  ✅ Partida salva no Slot {slot}.", 0.03)
    continuar()
    _jogar(jogador, slot)


def _jogar(jogador: Personagem, slot: int) -> None:
    while True:
        # Verificar se voltou de BSOD
        from src.tela_azul import verificar_e_exibir_retorno
        verificar_e_exibir_retorno()

        # NG+ ou campanha normal?
        if jogador.ng_plus:
            encontros = montar_encontros_ng(jogador)
            combate   = Combate(jogador, encontros, slot_ativo=slot, ng_plus=True)
        else:
            encontros = montar_encontros(jogador)
            combate   = Combate(jogador, encontros, slot_ativo=slot, ng_plus=False)

        resultado = combate.iniciar()

        if resultado == "bsod":
            # Jogo "fechou" — loop principal detecta ao reabrir
            # O save já foi feito antes da BSOD. Sair do processo é intencional.
            sys.exit(0)

        elif resultado == "vitoria":
            _tela_vitoria(jogador, ng=False)
            # Verificar se NG+ está disponível
            from src.tela_azul import ng_plus_desbloqueado
            if ng_plus_desbloqueado() and not jogador.ng_plus:
                r = input(cor(
                    "\n  O conteúdo NG+ foi desbloqueado. Iniciar Beyond the Kernel? [s/n]: ",
                    YELLOW)).strip().lower()
                if r in {"s", "sim"}:
                    jogador.ng_plus = True
                    jogador.mundo_alterado = True
                    salvar_em_slot(jogador, slot, silencioso=True)
                    continue
            break

        elif resultado == "vitoria_ng":
            _tela_vitoria(jogador, ng=True)
            break

        elif resultado == "derrota":
            decisao = _tela_derrota(jogador)
            if decisao == "reiniciar":
                jog_reload = carregar_de_slot(slot)
                if jog_reload:
                    jogador = jog_reload
                    continue
            break


def _tela_vitoria(jogador: Personagem, ng: bool = False) -> None:
    limpar_tela()
    if ng:
        banner_decorado("ALÉM DO VAZIO", "Você foi além do que o sistema permite.")
        print()
        texto_lento(
            "  O VAZIO foi confrontado. Não destruído — isso não é possível. "
            "Mas foi encontrado, enfrentado, e contido.", 0.03)
        texto_lento(
            "  O sistema registra a anomalia. Cria um arquivo com seu nome. "
            "Marca como: não resolvido.", 0.03)
        texto_lento(
            "  Isso é o máximo que o sistema consegue fazer com você.", 0.03)
    else:
        banner_decorado("VITÓRIA", "Você foi além do que o sistema esperava.")
        print()
        texto_lento(
            "  O Imperador do Caos caiu. O terminal ficou quieto pela primeira vez.", 0.03)
        texto_lento(
            f"  {jogador.nome}. Nível {jogador.level}. {jogador.classe_atual}.", 0.03)
        texto_lento(
            "  Você começou num quarto entediado, baixou um jogo questionável "
            "e acabou derrubando um imperador digital.", 0.03)
    print()
    texto_lento(f"  📊 {jogador.resumo_completo()}", 0.03)
    continuar("\n  [ ENTER para voltar ao menu... ]")


def _tela_derrota(jogador: Personagem) -> str:
    limpar_tela()
    banner("GAME OVER", "O sistema venceu desta vez.", RED)
    print()
    texto_lento(f"  {jogador.nome} caiu. Não é o fim — é uma pausa.", 0.03)
    texto_lento("  O sistema anotou o erro. Você também deveria.", 0.03)
    print()
    opcoes = [
        "🔄  Tentar novamente (recarregar último save)",
        "🏠  Voltar ao menu principal",
    ]
    escolha = menu_escolha("O que você faz?", opcoes)
    return "reiniciar" if escolha == 1 else "menu"


# ─────────────────────────────────────────────────────────────
#  MENU PRINCIPAL
# ─────────────────────────────────────────────────────────────
def menu_principal() -> None:
    # Verificar retorno pós-BSOD ao abrir o jogo
    _verificar_retorno_inicial()

    _audio.tocar_musica("menu")

    while True:
        limpar_tela()
        _desenhar_titulo()
        print()

        from src.tela_azul import ng_plus_desbloqueado
        ng_disponivel = ng_plus_desbloqueado()

        opcoes = [
            "🎮  Nova Partida",
            "📂  Continuar Partida",
            "💾  Gerenciar Saves",
            "🎯  Modo Recrutador (Demo)",
        ]
        if ng_disponivel:
            opcoes.append("🌑  Beyond the Kernel (NG+)")
        opcoes += ["🔊  Configurações de Áudio", "📖  Como Jogar", "🚪  Sair"]

        escolha = menu_escolha("", opcoes)
        base = 4  # opções antes do NG+ condicional
        offset = 1 if ng_disponivel else 0

        if escolha == 1:
            _iniciar_nova_partida()
        elif escolha == 2:
            _continuar_partida()
        elif escolha == 3:
            tela_gerenciar_saves()
        elif escolha == 4:
            modo_recrutador()
        elif ng_disponivel and escolha == 5:
            _continuar_ng_plus()
        elif escolha == 5 + offset:
            _audio.menu_audio()
            _audio.tocar_musica("menu")
        elif escolha == 6 + offset:
            _tela_como_jogar()
        elif escolha == 7 + offset:
            limpar_tela()
            texto_lento("  Até a próxima. O sistema continua rodando sem você.", 0.03)
            pausar(1.0)
            _audio.parar_musica()
            sys.exit(0)


def _verificar_retorno_inicial() -> None:
    """Detecta se o jogo foi reaberto após a BSOD."""
    from src.tela_azul import verificar_e_exibir_retorno
    if verificar_e_exibir_retorno():
        # Mostrou cutscene de retorno — agora pedir para carregar save
        limpar_tela()
        banner("SISTEMA RESTAURADO", "Retomando de onde parou.")
        texto_lento(
            "  Seu progresso foi preservado antes da... interrupção.", 0.03)
        texto_lento(
            "  Selecione sua partida para continuar.", 0.03)
        continuar()


def _iniciar_nova_partida() -> None:
    jogador = criar_jogador()
    _escolher_slot_e_jogar(jogador)
    _audio.tocar_musica("menu")


def _continuar_partida() -> None:
    jogador, slot = tela_selecionar_save()
    if jogador is None:
        return
    _jogar(jogador, slot)
    _audio.tocar_musica("menu")


def _continuar_ng_plus() -> None:
    """Carregar save existente e forçar modo NG+."""
    jogador, slot = tela_selecionar_save()
    if jogador is None:
        return
    if not jogador.ng_plus:
        jogador.ng_plus = True
        jogador.mundo_alterado = True
        salvar_em_slot(jogador, slot, silencioso=True)
    _jogar(jogador, slot)
    _audio.tocar_musica("menu")


def _desenhar_titulo() -> None:
    print()
    # TELA em ciano
    linhas_tela = [
        "  ████████╗███████╗██╗      █████╗  ",
        "     ██╔══╝██╔════╝██║     ██╔══██╗ ",
        "     ██║   █████╗  ██║     ███████║ ",
        "     ██║   ██╔══╝  ██║     ██╔══██║ ",
        "     ██║   ███████╗███████╗██║  ██║ ",
        "     ╚═╝   ╚══════╝╚══════╝╚═╝  ╚═╝ ",
    ]
    for t in linhas_tela:
        print(cor(t, CYAN))
    print()

    # A7UL em amarelo + .py em laranja na mesma linha
    linhas_a7ul = [
        "              █████╗ ███████╗██╗   ██╗██╗     ",
        "             ██╔══██╗╚════██║██║   ██║██║     ",
        "             ███████║    ██╔╝██║   ██║██║     ",
        "             ██╔══██║   ██╔╝ ██║   ██║██║     ",
        "             ██║  ██║   ██║  ╚██████╔╝███████╗",
        "             ╚═╝  ╚═╝   ╚═╝   ╚═════╝ ╚══════╝",
    ]
    linhas_py = [
        "██████╗ ██╗   ██╗",
        "██╔══██╗╚██╗ ██╔╝",
        "██████╔╝ ╚████╔╝ ",
        "██╔═══╝   ╚██╔╝  ",
        "██║        ██║   ",
        "╚═╝        ╚═╝   ",
    ]
    for a, p in zip(linhas_a7ul, linhas_py):
        sys.stdout.write(cor(a, YELLOW) + cor(p, ORANGE) + "\n")
        sys.stdout.flush()

    print()
    # Frase de impacto por extenso — humor +18, tema tech
    frase1 = "  ⚠  AVISO: Este programa contém bugs propositais, chefões sem dó e uma"
    frase2 = "     Tela Azul que vai te fazer achar que seu PC morreu de verdade."
    frase3 = "     Se você tem coração fraco, pressão alta ou código em produção aberto,"
    frase4 = "     feche agora.  —  Caso contrário: bem-vind@ ao sistema."
    print(cor(frase1, YELLOW))
    print(cor(frase2, YELLOW))
    print(cor(frase3, ORANGE))
    print(cor(frase4, ORANGE))
    print()
    separador()


def _tela_como_jogar() -> None:
    limpar_tela()
    banner("COMO JOGAR", "Tela Azul.py — Guia rápido")
    print()
    guia = [
        ("COMBATE",        "Turnos alternados. Você age, o inimigo age."),
        ("AÇÕES",          "[1] Atacar  [2] Skill  [3] Skill Extra  [4] Defender  [5] Meditar  [6] Item"),
        ("SALVAR [S]",     "Pressione S durante o combate para salvar a qualquer momento."),
        ("CIDADES",        "Aparecem entre capítulos. Loja, NPC de evolução e eventos."),
        ("EVOLUÇÃO",       "Encontre o Mestre de Classe na cidade. Requer nível mínimo."),
        ("EVENTOS",        "Aparecem entre lutas. Suas escolhas importam."),
        ("SAVES",          "3 slots. Gerencie no menu ou com S em combate."),
        ("SEXO",           "Escolhido na criação do personagem. Adapta pronomes e diálogos."),
        ("NG+",            "Desbloqueado após um evento especial. Conteúdo novo além do fim."),
        ("MODO DEMO",      "20-35 min. História independente. Ideal pra apresentar o projeto."),
        ("DICA",           "Mobs fracos dão menos XP. Use skills com inteligência nos bosses."),
        ("SEGREDO",        "Jogue até o fim. Algo vai acontecer que você não vai esquecer."),
    ]
    for titulo, desc in guia:
        print(f"  {cor(f'{titulo:16s}', YELLOW)} {desc}")
    print()
    continuar()


# ─────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────

def _escolher_edicao() -> str:
    """Seleciona a edição do jogo (lite/full).

    Primeiro verifica a variável de ambiente TELA_A7UL_EDITION (lite|full) para
    permitir execuções automatizadas. Caso não exista, apresenta um pequeno
    menu interativo para o usuário escolher. Retorna 'lite' ou 'full'.
    """
    import os

    env = os.environ.get("TELA_A7UL_EDITION", "").strip().lower()
    if env in {"lite", "full", "completa", "completo", "complete", "complete"}:
        return "lite" if env.startswith("l") else "full"

    # Interativo — mantém aparência e textos originais
    limpar_tela()
    banner("TELA A7UL", "Escolha a edição")
    print()
    print(f"  {cor('[1]', CYAN)} Lite")
    print(f"  {cor('[2]', CYAN)} Completa")
    print()
    while True:
        esc = input(cor("  Escolha: ", YELLOW)).strip()
        if esc == "1":
            return "lite"
        if esc == "2":
            return "full"
        print(cor("  Digite 1 ou 2.", RED))


if __name__ == "__main__":
    try:
        # Pequeno menu inicial para seleção de edição (lite / completa).
        # A variável global EDITION fica disponível no módulo main para futuras
        # integrações. Não altera o fluxo do jogo.
        EDITION = _escolher_edicao()
        texto_lento(f"\n  Edição selecionada: {cor(EDITION.upper(), CYAN)}", 0.02)
        pausar(0.6)

        menu_principal()
    except KeyboardInterrupt:
        limpar_tela()
        texto_lento("\n  Interrompido. O sistema continua.", 0.03)
        pausar(0.8)
        sys.exit(0)
    except Exception as e:
        limpar_tela()
        print(cor(f"\n  Erro inesperado: {e}", RED))
        import traceback
        traceback.print_exc()
        print(cor("  O jogo vai tentar voltar ao menu.", YELLOW))
        pausar(2.5)
        try:
            menu_principal()
        except Exception:
            sys.exit(1)
