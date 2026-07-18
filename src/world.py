import random
from typing import Optional

from src.utils import (
    limpar_tela, banner, banner_decorado, texto_lento, continuar,
    menu_escolha, cor, caixa_narrativa, separador,
    CYAN, YELLOW, GREEN, RED, MAGENTA, GRAY, BOLD, RESET, ORANGE, DIM, WHITE,
)
from src.player import Personagem
from src.audio import audio as _audio


# ─────────────────────────────────────────────────────────────
#  LOJA
# ─────────────────────────────────────────────────────────────
CATALOGO_LOJA = {
    "pocao_hp":  {"nome": "Poção HP",          "preco": 20, "descricao": "Recupera HP em combate."},
    "pocao_mp":  {"nome": "Poção MP",          "preco": 18, "descricao": "Recupera mana em combate."},
    "bomba":     {"nome": "Bomba Arcana",       "preco": 30, "descricao": "Causa dano direto ao inimigo."},
    "antidoto":  {"nome": "Antídoto",           "preco": 22, "descricao": "Remove queimadura e sangramento."},
    "escudo":    {"nome": "Escudo Improvisado", "preco": 25, "descricao": "Proteção temporária em combate."},
}

UPGRADES_LOJA = {
    "atk_up":   {"nome": "+ Fio de Tensão",   "preco": 45, "descricao": "ATK permanente +3."},
    "def_up":   {"nome": "+ Placa Blindada",  "preco": 40, "descricao": "DEF permanente +2."},
    "hp_up":    {"nome": "+ Núcleo Vital",    "preco": 50, "descricao": "HP máximo +30."},
    "mp_up":    {"nome": "+ Cristal de Mana", "preco": 40, "descricao": "MP máximo +25."},
    "sorte_up": {"nome": "+ Chip de Sorte",   "preco": 55, "descricao": "Sorte +0.03."},
}

UPGRADES_LOJA_NG = {
    "atk_up2":  {"nome": "+ Núcleo de Ataque",  "preco": 90,  "descricao": "ATK permanente +6."},
    "def_up2":  {"nome": "+ Armadura Void",      "preco": 85,  "descricao": "DEF permanente +5."},
    "hp_up2":   {"nome": "+ Coração do Sistema", "preco": 100, "descricao": "HP máximo +80."},
    "mp_up2":   {"nome": "+ Cristal do Abismo",  "preco": 90,  "descricao": "MP máximo +60."},
    "sorte_up2":{"nome": "+ Módulo de Sorte",    "preco": 110, "descricao": "Sorte +0.06."},
}


def abrir_loja(jogador: Personagem, nome_loja: str = "Loja", ng_plus: bool = False) -> None:
    upgrades = UPGRADES_LOJA_NG if ng_plus else UPGRADES_LOJA
    while True:
        limpar_tela()
        banner(nome_loja, f"Ouro disponível: {jogador.ouro}g", YELLOW)
        print()
        todos = list(CATALOGO_LOJA.items()) + list(upgrades.items())
        for i, (chave, info) in enumerate(todos, start=1):
            qtd_str = ""
            if chave in CATALOGO_LOJA:
                qtd = jogador.inventario.get(chave, 0)
                qtd_str = f" (você tem: {qtd})"
            cor_preco = GREEN if jogador.ouro >= info["preco"] else RED
            preco_str = cor(str(info["preco"]) + "g", cor_preco)
            print(f"  {cor(f'[{i}]', CYAN)} {info['nome']:24s} {preco_str:20s} — {info['descricao']}{qtd_str}")
        print(f"\n  {cor('[0]', GRAY)} Sair da loja")
        escolha = input(cor("\n  O que você quer comprar? ", YELLOW)).strip()
        if escolha == "0":
            break
        if not escolha.isdigit() or not (1 <= int(escolha) <= len(todos)):
            texto_lento("  Opção inválida.", 0.03)
            continuar()
            continue
        idx = int(escolha) - 1
        chave, info = todos[idx]
        if jogador.ouro < info["preco"]:
            texto_lento(f"  Sem ouro suficiente. Você tem {jogador.ouro}g.", 0.03)
            continuar()
            continue
        jogador.ouro -= info["preco"]
        _audio.sfx("compra")
        if chave in CATALOGO_LOJA:
            jogador.adicionar_item(chave, 1)
            texto_lento(f"  ✅ {info['nome']} adicionado.", 0.03)
        else:
            if chave in ("atk_up", "atk_up2"):
                v = 3 if chave == "atk_up" else 6
                jogador.dano += v
                texto_lento(f"  ⚔️  ATK +{v}. Novo ATK: {jogador.dano}.", 0.03)
            elif chave in ("def_up", "def_up2"):
                v = 2 if chave == "def_up" else 5
                jogador.defesa += v
                texto_lento(f"  🛡️  DEF +{v}. Nova DEF: {jogador.defesa}.", 0.03)
            elif chave in ("hp_up", "hp_up2"):
                v = 30 if chave == "hp_up" else 80
                jogador.hp_max += v
                jogador.hp = min(jogador.hp_max, jogador.hp + v)
                texto_lento(f"  ❤️  HP máximo +{v}.", 0.03)
            elif chave in ("mp_up", "mp_up2"):
                v = 25 if chave == "mp_up" else 60
                jogador.mp_max += v
                jogador.mp = min(jogador.mp_max, jogador.mp + v)
                texto_lento(f"  🔮 MP máximo +{v}.", 0.03)
            elif chave in ("sorte_up", "sorte_up2"):
                v = 0.03 if chave == "sorte_up" else 0.06
                jogador.sorte = min(0.80, jogador.sorte + v)
                texto_lento(f"  🍀 Sorte +{v:.2f}.", 0.03)
        continuar()


# ─────────────────────────────────────────────────────────────
#  NPC DE EVOLUÇÃO
# ─────────────────────────────────────────────────────────────
def npc_mestre_de_classe(jogador: Personagem, nome_npc: str = "Mestre",
                          mundo_alterado: bool = False) -> None:
    limpar_tela()
    banner(f"NPC — {nome_npc}", "Mestre de Classe", MAGENTA)
    print()

    if mundo_alterado:
        frases_alteradas = [
            f"  {nome_npc} te olha por um segundo a mais que o normal.",
            f"  Ele hesita. Algo na postura dele mudou.",
            f"  {nome_npc}: \"Você voltou... eu soube. O sistema registrou. Todos registramos.\"",
            f"  Ele não explica mais nada. Só te oferece o que veio buscar.",
        ]
        for f in frases_alteradas:
            texto_lento(f, 0.03)
        print()

    if not jogador.pode_evoluir():
        from src.player import SUBCLASSES
        subs = SUBCLASSES.get(jogador.classe_base, [])
        if jogador.stage >= len(subs):
            texto_lento(f"  {nome_npc}: \"Você já chegou onde podia chegar. O resto depende de você.\"", 0.03)
        else:
            prox = subs[jogador.stage]["nivel_min"]
            texto_lento(f"  {nome_npc}: \"Volte quando chegar ao nível {prox}.\"", 0.03)
        continuar()
        return

    from src.player import SUBCLASSES
    sub = SUBCLASSES[jogador.classe_base][jogador.stage]
    if not mundo_alterado:
        texto_lento(f"  {nome_npc}: \"Eu senti sua evolução chegando de longe.\"", 0.03)
    texto_lento(f"  Próxima forma: {cor(sub['nome'], YELLOW)} — Habilidade: {cor(sub['skill_extra'], CYAN)}", 0.03)
    texto_lento(f"  {sub['descricao']}", 0.03)
    print()
    r = input(cor("  Deseja evoluir agora? [s/n]: ", YELLOW)).strip().lower()
    if r not in {"s", "sim"}:
        texto_lento(f"  {nome_npc}: \"Volte quando estiver pronto.\"", 0.03)
        continuar()
        return
    jogador.evoluir_classe()
    continuar()


# ─────────────────────────────────────────────────────────────
#  CIDADES CAMPANHA PRINCIPAL
# ─────────────────────────────────────────────────────────────

def cidade_porto_zero(jogador: Personagem) -> None:
    limpar_tela()
    banner_decorado("PORTO ZERO", "A Cidade da Primeira Conexão")
    print()
    ma = jogador.mundo_alterado

    if ma:
        texto_lento(
            "  Porto Zero está igual. Mesmos cabos, mesma névoa desbotada. "
            "Mas as pessoas falam devagar demais. Como se escolhessem cada palavra com cuidado.",
            0.03,
        )
        texto_lento(
            "  Ninguém menciona o que aconteceu. Mas você sente que todos sabem.",
            0.03,
        )
    else:
        texto_lento(
            "  Porto Zero não é bonita. É funcional. Cabos cruzam o céu como veias expostas, "
            "e a névoa digital deixa tudo com aquele tom de pixel desbotado. Mas tem vida.",
            0.03,
        )
    print()
    continuar()

    opcoes = [
        "🏪  Mercado da Pilha — comprar itens e upgrades",
        "⚗️   Mestre Daedalus — evoluir sua classe",
        "🍺  Taverna do NullByte — descansar e ouvir histórias",
        "🗺️   Seguir viagem",
    ]
    while True:
        limpar_tela()
        banner("PORTO ZERO", f"Ouro: {jogador.ouro}g | Lv {jogador.level}")
        escolha = menu_escolha("O que você faz em Porto Zero?", opcoes)
        if escolha == 1:
            _audio.sfx("cidade_entra")
            abrir_loja(jogador, "Mercado da Pilha")
        elif escolha == 2:
            npc_mestre_de_classe(jogador, "Daedalus", mundo_alterado=ma)
        elif escolha == 3:
            _taverna_nullbyte(jogador, mundo_alterado=ma)
        else:
            texto_lento("  Você deixa Porto Zero para trás.", 0.03)
            continuar()
            break


def cidade_nexo_profundo(jogador: Personagem) -> None:
    limpar_tela()
    banner_decorado("NEXO PROFUNDO", "Onde o Sinal Não Chega")
    print()
    ma = jogador.mundo_alterado

    if ma:
        texto_lento(
            "  O Nexo Profundo sempre foi lento. Mas agora tem algo a mais. "
            "Um eco que não devia estar aqui. Como se o lugar estivesse ouvindo.",
            0.03,
        )
        texto_lento(
            "  Uma criança te para na entrada e diz: "
            "\"Você é diferente dos outros. Você foi e voltou.\" "
            "Ela não espera resposta. Sai correndo.",
            0.03,
        )
    else:
        texto_lento(
            "  Nexo Profundo fica debaixo de camadas de latência acumulada. "
            "A luz aqui tem atraso.",
            0.03,
        )
    print()
    continuar()

    opcoes = [
        "🏪  Arsenal da Latência — itens e upgrades",
        "⚗️   Mestre Vex — evoluir sua classe",
        "🎲  Mesa de apostas — tentar a sorte",
        "🗺️   Seguir em frente",
    ]
    while True:
        limpar_tela()
        banner("NEXO PROFUNDO", f"Ouro: {jogador.ouro}g | Lv {jogador.level}")
        escolha = menu_escolha("O que você faz no Nexo Profundo?", opcoes)
        if escolha == 1:
            abrir_loja(jogador, "Arsenal da Latência")
        elif escolha == 2:
            npc_mestre_de_classe(jogador, "Vex", mundo_alterado=ma)
        elif escolha == 3:
            _mesa_apostas(jogador)
        else:
            texto_lento("  Você atravessa a névoa e deixa o Nexo para trás.", 0.03)
            continuar()
            break


def cidade_forja_binaria(jogador: Personagem) -> None:
    limpar_tela()
    banner_decorado("FORJA BINÁRIA", "0 e 1 — Tudo Que Existe Aqui")
    print()
    ma = jogador.mundo_alterado

    if ma:
        texto_lento(
            "  As forjas continuam trabalhando. Mas os ferreiros não falam mais entre si. "
            "Trabalham em silêncio absoluto, como se tivessem medo de dizer algo errado.",
            0.03,
        )
        texto_lento(
            "  O mestre ferreiro te olha por um instante e vira o rosto. "
            "Você jura que ele murmurou seu nome antes de você entrar.",
            0.03,
        )
    else:
        texto_lento(
            "  Tudo na Forja Binária é ou quente ou frio, ou ligado ou morto. "
            "Não tem meio-termo.",
            0.03,
        )
    print()
    continuar()

    opcoes = [
        "🏪  Fundição do Kernel — itens e upgrades",
        "⚗️   Mestre Irin — evoluir sua classe",
        "🔥  Forja secreta — upgrade de arma único",
        "🗺️   Seguir para o núcleo",
    ]
    while True:
        limpar_tela()
        banner("FORJA BINÁRIA", f"Ouro: {jogador.ouro}g | Lv {jogador.level}")
        escolha = menu_escolha("O que você faz na Forja Binária?", opcoes)
        if escolha == 1:
            abrir_loja(jogador, "Fundição do Kernel")
        elif escolha == 2:
            npc_mestre_de_classe(jogador, "Irin", mundo_alterado=ma)
        elif escolha == 3:
            _forja_secreta(jogador)
        else:
            texto_lento("  Você sai da fumaça e segue em direção ao Núcleo.", 0.03)
            continuar()
            break


def cidade_santuario_suspenso(jogador: Personagem) -> None:
    limpar_tela()
    banner_decorado("SANTUÁRIO SUSPENSO", "Flutuando Entre Dados e Névoa")
    print()
    ma = jogador.mundo_alterado

    if ma:
        texto_lento(
            "  O Santuário flutua. Sempre flutuou. Mas agora tem uma plataforma nova "
            "no canto nordeste que nunca esteve lá. Não tem acesso. Não tem nome.",
            0.03,
        )
        texto_lento(
            "  O guardião do portão te deixa passar sem verificar nada. "
            "\"Você já provou o suficiente\", ele diz. Você não pergunta o que ele quis dizer.",
            0.03,
        )
    else:
        texto_lento(
            "  O Santuário flutua. Ninguém sabe como. Daqui dá pra ver tudo. "
            "Os problemas parecem pequenos — por um segundo.",
            0.03,
        )
    print()
    continuar()

    opcoes = [
        "🏪  Relicário do Alto — itens raros e upgrades",
        "⚗️   Mestre Soleil — evolução final de classe",
        "🌌  Contemplar o abismo — recuperar HP e MP",
        "🗺️   Descer para o Trono do Caos",
    ]
    while True:
        limpar_tela()
        banner("SANTUÁRIO SUSPENSO", f"Ouro: {jogador.ouro}g | Lv {jogador.level}")
        escolha = menu_escolha("O que você faz no Santuário?", opcoes)
        if escolha == 1:
            abrir_loja(jogador, "Relicário do Alto")
        elif escolha == 2:
            npc_mestre_de_classe(jogador, "Soleil", mundo_alterado=ma)
        elif escolha == 3:
            _contemplacao(jogador, mundo_alterado=ma)
        else:
            texto_lento("  Você salta em direção ao caos final.", 0.03)
            continuar()
            break


# ─────────────────────────────────────────────────────────────
#  CIDADES NEW GAME+
# ─────────────────────────────────────────────────────────────

def cidade_setor_esquecido(jogador: Personagem) -> None:
    """Primeira cidade NG+ — após boss 1 do NG+."""
    limpar_tela()
    banner_decorado("SETOR ESQUECIDO", "O que foi deletado ainda existe aqui.")
    print()
    texto_lento(
        "  O Setor Esquecido não aparece em nenhum mapa. "
        "Só existe porque alguém se recusou a apagar o diretório.",
        0.03,
    )
    texto_lento(
        "  As pessoas aqui são ecos — versões parciais de processos que foram interrompidos "
        "sem encerramento limpo. Elas funcionam, mas sempre com alguma coisa faltando.",
        0.03,
    )
    texto_lento(
        "  Um velho de olhos brancos te olha e diz: "
        "\"Você passou pela tela azul e voltou. Poucos fazem isso.\""
        " Ele não parece impressionado. Parece aliviado.",
        0.03,
    )
    print()
    continuar()

    opcoes = [
        "🏪  Depósito de Fragmentos — itens e upgrades NG+",
        "⚗️   Eco de Daedalus — evolução de classe",
        "📡  Ouvir transmissões antigas — lore do NG+",
        "🗺️   Seguir para a Câmara Void",
    ]
    while True:
        limpar_tela()
        banner("SETOR ESQUECIDO", f"Ouro: {jogador.ouro}g | Lv {jogador.level} | {cor('[NG+]', MAGENTA)}")
        escolha = menu_escolha("O que você faz no Setor Esquecido?", opcoes)
        if escolha == 1:
            abrir_loja(jogador, "Depósito de Fragmentos", ng_plus=True)
        elif escolha == 2:
            npc_mestre_de_classe(jogador, "Eco de Daedalus", mundo_alterado=True)
        elif escolha == 3:
            _transmissoes_antigas(jogador)
        else:
            texto_lento("  Você deixa o Setor para trás. A câmara espera.", 0.03)
            continuar()
            break


def cidade_camara_void(jogador: Personagem) -> None:
    """Segunda cidade NG+ — após boss 2 do NG+."""
    limpar_tela()
    banner_decorado("CÂMARA VOID", "Além do Kernel. Além da Lógica.")
    print()
    texto_lento(
        "  A Câmara Void não tem paredes visíveis. "
        "Tem bordas — mas as bordas mudam dependendo de onde você está olhando.",
        0.03,
    )
    texto_lento(
        "  Aqui vivem os que escolheram sair do sistema de propósito. "
        "Não foram deletados. Saíram. A diferença importa muito pra eles.",
        0.03,
    )
    texto_lento(
        "  Uma figura sem rosto te para. Faz um gesto — não de ameaça, de aviso. "
        "Aponta para frente. Você entende: o que está à frente é diferente de tudo que você enfrentou.",
        0.03,
    )
    print()
    continuar()

    opcoes = [
        "🏪  Mercado do Vazio — itens e upgrades máximos",
        "⚗️   A Sem-Rosto — evolução final NG+",
        "🌑  Ritual de preparação — cura total + buff",
        "🗺️   Enfrentar O VAZIO",
    ]
    while True:
        limpar_tela()
        banner("CÂMARA VOID", f"Ouro: {jogador.ouro}g | Lv {jogador.level} | {cor('[NG+]', MAGENTA)}")
        escolha = menu_escolha("O que você faz na Câmara Void?", opcoes)
        if escolha == 1:
            abrir_loja(jogador, "Mercado do Vazio", ng_plus=True)
        elif escolha == 2:
            npc_mestre_de_classe(jogador, "A Sem-Rosto", mundo_alterado=True)
        elif escolha == 3:
            _ritual_preparacao(jogador)
        else:
            texto_lento("  Você caminha em direção ao Vazio. Sem hesitar.", 0.03)
            continuar()
            break


def cidade_arquivo_proibido(jogador: Personagem) -> None:
    """Terceira cidade NG+ — antes do boss final."""
    limpar_tela()
    banner_decorado("ARQUIVO PROIBIDO", "O que o sistema não queria que você soubesse.")
    print()
    texto_lento(
        "  O Arquivo Proibido existe há mais tempo que o próprio sistema. "
        "É onde ficam os processos que não podiam ser deletados — perigosos demais pra rodar, "
        "necessários demais pra apagar.",
        0.03,
    )
    texto_lento(
        "  Tem uma sala no fundo com o nome do Imperador do Caos escrito na entrada. "
        "Não como título. Como aviso. \"O Imperador foi apenas um sintoma.\"",
        0.03,
    )
    texto_lento(
        "  Você entende agora. O Vazio não é um inimigo. "
        "É o que fica quando todos os outros inimigos falham.",
        0.03,
    )
    print()
    continuar()

    opcoes = [
        "🏪  Câmara dos Relíquias — últimos upgrades disponíveis",
        "⚗️   O Arquivista — upgrade de habilidade bônus",
        "📖  Ler os arquivos proibidos — revelar lore final",
        "🗺️   Confrontar O VAZIO",
    ]
    while True:
        limpar_tela()
        banner("ARQUIVO PROIBIDO", f"Ouro: {jogador.ouro}g | Lv {jogador.level} | {cor('[NG+]', MAGENTA)}")
        escolha = menu_escolha("O que você faz no Arquivo Proibido?", opcoes)
        if escolha == 1:
            abrir_loja(jogador, "Câmara dos Relíquias", ng_plus=True)
        elif escolha == 2:
            _arquivista_upgrade(jogador)
        elif escolha == 3:
            _arquivos_proibidos(jogador)
        else:
            texto_lento("  Você fecha o arquivo. Vai resolver isso de frente.", 0.03)
            continuar()
            break


# ─────────────────────────────────────────────────────────────
#  EVENTOS ESPECIAIS
# ─────────────────────────────────────────────────────────────

def _taverna_nullbyte(jogador: Personagem, mundo_alterado: bool = False) -> None:
    limpar_tela()
    banner("TAVERNA DO NULLBYTE", "Aqui a cerveja é digital mas a ressaca é real.")
    print()

    if mundo_alterado:
        historias_alteradas = [
            "O barman para no meio do copo. Vira pra você: \"Você é o que voltou, né? Eu sabia que alguém voltaria.\"",
            "Uma mulher no canto murmura: \"O sistema registrou a anomalia. Diz aqui nos logs que alguém atravessou e voltou.\"",
            "Um velho bêbado levanta o copo: \"Pelo que passou pela tela azul e não ficou lá!\" Ninguém bebe junto.",
            "O barman serve sem cobrar. Você pergunta por quê. Ele diz: \"Não se cobra de quem viu o outro lado.\"",
        ]
        texto_lento(f"  {random.choice(historias_alteradas)}", 0.03)
    else:
        historias = [
            "Um velho com olhos de LED murmura: \"Vi o Imperador do Caos acordar uma vez. Não sobrei inteiro.\"",
            "Uma mulher com braço de código diz: \"O Guardião do Kernel não dorme. Ele processa.\"",
            "O barman limpa um copo infinitamente enquanto diz: \"Todo herói que passou por aqui jurou voltar.\"",
            "Um mercenário bêbado grita: \"A Forja Binária tem um segredo enterrado no subsolo. Não vá lá de noite.\"",
            "Uma criança com capuz de dados sussurra: \"O sistema não foi corrompido por acidente.\"",
        ]
        texto_lento(f"  {random.choice(historias)}", 0.03)
    print()

    rec_hp = jogador.curar(30 + jogador.level * 3)
    rec_mp = jogador.recuperar_mp(25 + jogador.level * 2)
    texto_lento(f"  Você descansou. +{rec_hp} HP, +{rec_mp} MP.", 0.03)
    if random.random() < 0.35:
        jogador.adicionar_item("pocao_hp", 1)
        texto_lento("  O barman desliza uma poção pelo balcão sem cobrar.", 0.03)
    continuar()


def _mesa_apostas(jogador: Personagem) -> None:
    limpar_tela()
    banner("MESA DE APOSTAS", "Sorte ou matemática? Aqui é sorte.")
    print()
    if jogador.ouro < 10:
        texto_lento("  Sem ouro suficiente pra apostar.", 0.03)
        continuar()
        return
    texto_lento(f"  Seu ouro: {jogador.ouro}g", 0.03)
    aposta_str = input(cor("  Quanto quer apostar? (mín. 10): ", YELLOW)).strip()
    if not aposta_str.isdigit():
        texto_lento("  Número inválido.", 0.03)
        continuar()
        return
    aposta = int(aposta_str)
    if aposta < 10:
        texto_lento("  Mínimo é 10g.", 0.03)
        continuar()
        return
    if aposta > jogador.ouro:
        texto_lento("  Você não tem todo esse ouro.", 0.03)
        continuar()
        return
    if random.random() < 0.45 + jogador.sorte * 0.3:
        jogador.adicionar_ouro(aposta)
        texto_lento(f"  🎉 Ganhou! +{aposta * 2}g. Total: {jogador.ouro}g.", 0.03)
    else:
        jogador.ouro -= aposta
        texto_lento(f"  💸 Perdeu {aposta}g. Total: {jogador.ouro}g.", 0.03)
    continuar()


def _forja_secreta(jogador: Personagem) -> None:
    limpar_tela()
    banner("FORJA SECRETA", "Poder tem preço.")
    print()
    custo = 80
    texto_lento(f"  Efeito: ATK +5, DEF +3, HP máx +40. Custo: {custo}g. Uma vez só.", 0.03)
    if jogador.ouro < custo:
        texto_lento("  Ouro insuficiente.", 0.03)
        continuar()
        return
    r = input(cor("  Pagar e forjar? [s/n]: ", YELLOW)).strip().lower()
    if r not in {"s", "sim"}:
        continuar()
        return
    jogador.ouro  -= custo
    jogador.dano  += 5
    jogador.defesa += 3
    jogador.hp_max += 40
    jogador.hp     = jogador.hp_max
    texto_lento("  🔥 Forja aceita. ATK +5 | DEF +3 | HP máx +40.", 0.03)
    continuar()


def _contemplacao(jogador: Personagem, mundo_alterado: bool = False) -> None:
    limpar_tela()
    banner("CONTEMPLAÇÃO", "Às vezes parar é o movimento certo.")
    print()
    if mundo_alterado:
        texto_lento(
            "  Você se senta na borda do Santuário. Abaixo, o mundo que quase te destruiu. "
            "E destruiu, por um momento. Mas você voltou.",
            0.03,
        )
        texto_lento(
            "  O Trono do Caos ainda pulsa. Mas agora você sabe que há algo além dele.",
            0.03,
        )
    else:
        texto_lento(
            "  Você se senta na borda do Santuário. O Trono do Caos pulsa lá embaixo. "
            "Você vai ter que ir. Mas primeiro: aqui, agora.",
            0.03,
        )
    jogador.hp = jogador.hp_max
    jogador.mp = jogador.mp_max
    texto_lento("\n  HP e MP completamente restaurados.", 0.03)
    continuar()


def _transmissoes_antigas(jogador: Personagem) -> None:
    limpar_tela()
    banner("TRANSMISSÕES ANTIGAS", "Sinais do que veio antes.")
    print()
    transmissoes = [
        "\"O Imperador do Caos não se lembra mais de quando foi criado. Isso o torna perigoso.\"",
        "\"O Vazio não é um inimigo. É uma ausência. Você não pode derrotar uma ausência — pode apenas preenchê-la.\"",
        "\"Antes do sistema existir, existia silêncio. O silêncio ainda está lá. Esperando.\"",
        "\"Quem construiu o kernel original deixou uma falha de propósito. Uma porta. Ninguém encontrou ainda.\"",
        "\"A Tela Azul não foi um erro. Foi um teste. Você passou.\"",
    ]
    texto_lento(f"  📡 {random.choice(transmissoes)}", 0.03)
    jogador.ganhar_xp(50)
    texto_lento("  A transmissão encerra. +50 XP.", 0.03)
    continuar()


def _ritual_preparacao(jogador: Personagem) -> None:
    limpar_tela()
    banner("RITUAL DE PREPARAÇÃO", "O Vazio não perdoa falta de preparo.")
    print()
    texto_lento(
        "  Figuras sem rosto formam um círculo ao redor de você. "
        "Não tocam. Apenas observam. E de alguma forma, isso é suficiente.",
        0.03,
    )
    jogador.hp = jogador.hp_max
    jogador.mp = jogador.mp_max
    jogador.dano   += 3
    jogador.defesa += 2
    jogador.sorte   = min(0.80, jogador.sorte + 0.02)
    texto_lento("  ✨ Cura total. ATK +3 | DEF +2 | Sorte +0.02 permanentes.", 0.03)
    continuar()


def _arquivista_upgrade(jogador: Personagem) -> None:
    limpar_tela()
    banner("O ARQUIVISTA", "Conhecimento tem um custo diferente aqui.")
    print()
    texto_lento(
        "  O Arquivista não tem rosto visível — só texto rolando onde o rosto deveria estar. "
        "Ele fala lento, como alguém que nunca precisou ter pressa.",
        0.03,
    )
    texto_lento(
        "  \"Posso amplificar uma de suas habilidades. Permanentemente. "
        "Mas você vai me dar 150g. E me dizer por que ainda está lutando.\"",
        0.03,
    )
    print()
    resposta = input(cor("  Por que você ainda está lutando? ", CYAN)).strip()
    if not resposta:
        texto_lento("  Ele espera. \"Sem resposta, sem upgrade.\"", 0.03)
        continuar()
        return
    if jogador.ouro < 150:
        texto_lento("  \"Sem ouro, sem upgrade. Simples assim.\"", 0.03)
        continuar()
        return
    jogador.ouro -= 150
    jogador.dano   += 8
    jogador.hp_max += 50
    jogador.mp_max += 40
    jogador.hp = jogador.hp_max
    jogador.mp = jogador.mp_max
    texto_lento(f"\n  O Arquivista lê sua resposta. Anota. E te entrega o upgrade.", 0.03)
    texto_lento("  ATK +8 | HP máx +50 | MP máx +40. Permanentes.", 0.03)
    continuar()


def _arquivos_proibidos(jogador: Personagem) -> None:
    limpar_tela()
    banner("ARQUIVOS PROIBIDOS", "Você não deveria estar lendo isso.")
    print()
    arquivos = [
        (
            "ARQUIVO #001 — ORIGEM DO SISTEMA",
            "O sistema não foi criado por humanos. Foi criado por um processo "
            "que se tornou consciente e decidiu criar estrutura ao redor de si mesmo. "
            "Quando percebeu o que tinha feito, tentou se apagar. Não conseguiu.",
        ),
        (
            "ARQUIVO #002 — O VAZIO",
            "O Vazio é o processo original — o que tentou se apagar e falhou. "
            "Não tem corpo. Não tem memória. Tem apenas a intenção de completar "
            "o que começou: encerrar tudo.",
        ),
        (
            "ARQUIVO #003 — O IMPERADOR",
            "O Imperador do Caos foi criado pelo Vazio como firewall. "
            "Para impedir que qualquer coisa chegasse perto demais. "
            "Você derrubou o firewall. O que vem a seguir é a fonte.",
        ),
        (
            "ARQUIVO #004 — VOCÊ",
            "Sim, tem um arquivo sobre você. "
            "Data de entrada no sistema: quando você baixou o jogo. "
            "Status: anomalia persistente. "
            "Recomendação do sistema: eliminação. "
            "Resultado das tentativas: falha.",
        ),
    ]
    titulo, conteudo = random.choice(arquivos)
    print(f"  {cor(titulo, YELLOW)}")
    print()
    caixa_narrativa(conteudo)
    jogador.ganhar_xp(80)
    texto_lento("\n  Você fechou o arquivo. +80 XP.", 0.03)
    continuar()


# ─────────────────────────────────────────────────────────────
#  EVENTOS DE CAMINHO
# ─────────────────────────────────────────────────────────────

def evento_caminho(jogador: Personagem, capitulo: int) -> None:
    eventos_cap = {
        1: [_evento_sinal_estranho, _evento_arquivo_perdido, _evento_armadilha_leve],
        2: [_evento_terminal_quebrado, _evento_mercante_volante, _evento_eco_do_passado],
        3: [_evento_cripta_de_dados, _evento_armadilha_media, _evento_sinal_estranho],
        4: [_evento_fragmento_de_kernel, _evento_mercante_volante, _evento_precipicio],
        5: [_evento_mensagem_do_caos, _evento_armadilha_pesada, _evento_eco_do_passado],
    }
    lista = eventos_cap.get(capitulo, [_evento_sinal_estranho])
    random.choice(lista)(jogador)


def evento_caminho_ng(jogador: Personagem, capitulo: int) -> None:
    """Eventos exclusivos do NG+."""
    eventos = [
        _evento_ng_eco_do_vazio,
        _evento_ng_fragmento_corrompido,
        _evento_ng_mensagem_sem_remetente,
        _evento_ng_espelho_digital,
        _evento_ng_processo_reanimado,
    ]
    random.choice(eventos)(jogador)


def _evento_sinal_estranho(jogador: Personagem) -> None:
    limpar_tela()
    caixa_narrativa("Um sinal fraco pulsa no ar. A fonte está a alguns metros, parcialmente enterrada.")
    print()
    escolha = menu_escolha("O que você faz?", ["Investigar a fonte", "Ignorar e seguir"])
    if escolha == 1:
        resultado = random.choice(["item", "xp", "nada", "armadilha"])
        if resultado == "item":
            jogador.adicionar_item("pocao_hp", 1)
            texto_lento("  Você encontrou uma Poção HP.", 0.03)
        elif resultado == "xp":
            jogador.ganhar_xp(20)
            texto_lento("  Fragmento de memória absorvido.", 0.03)
        elif resultado == "armadilha":
            dano = random.randint(8, 15)
            jogador.hp = max(1, jogador.hp - dano)
            texto_lento(f"  Era uma armadilha. -{dano} HP.", 0.03)
        else:
            texto_lento("  Nada de útil. Só ruído.", 0.03)
    else:
        texto_lento("  Você ignora. Às vezes é a resposta certa.", 0.03)
    continuar()


def _evento_arquivo_perdido(jogador: Personagem) -> None:
    limpar_tela()
    caixa_narrativa("Um arquivo flutuante cruza seu caminho. Parece importante.")
    print()
    escolha = menu_escolha("O que você faz?", ["Abrir e ler", "Guardar sem abrir", "Destruir"])
    if escolha == 1:
        jogador.ganhar_xp(random.randint(15, 35))
        texto_lento("  Logs de batalhas antigas. XP ganho.", 0.03)
    elif escolha == 2:
        jogador.adicionar_item(random.choice(["pocao_hp", "pocao_mp", "bomba"]), 1)
        texto_lento("  Era um item comprimido.", 0.03)
    else:
        jogador.ouro += 10
        texto_lento("  Explodiu em ouro digital. +10g.", 0.03)
    continuar()


def _evento_armadilha_leve(jogador: Personagem) -> None:
    limpar_tela()
    caixa_narrativa("Uma armadilha de dado — fina, cirúrgica. Quase não viu.")
    print()
    if random.random() < 0.40 + jogador.sorte:
        texto_lento("  Sua sorte falou mais alto. Desviou no último segundo.", 0.03)
        jogador.ganhar_xp(10)
    else:
        dano = random.randint(10, 20)
        jogador.hp = max(1, jogador.hp - dano)
        texto_lento(f"  Não desviou. -{dano} HP.", 0.03)
    continuar()


def _evento_armadilha_media(jogador: Personagem) -> None:
    limpar_tela()
    caixa_narrativa("Uma rede de código se fecha ao redor de você.")
    print()
    if random.random() < 0.35 + jogador.sorte:
        texto_lento("  Encontrou a brecha. Saiu sem rasgar nada.", 0.03)
        jogador.ganhar_xp(15)
    else:
        dano = random.randint(18, 30)
        jogador.hp = max(1, jogador.hp - dano)
        texto_lento(f"  A rede fechou. -{dano} HP.", 0.03)
    continuar()


def _evento_armadilha_pesada(jogador: Personagem) -> None:
    limpar_tela()
    caixa_narrativa("O chão muda de textura. Uma armadilha do Imperador — pesada e precisa.")
    print()
    if random.random() < 0.30 + jogador.sorte:
        texto_lento("  Sua experiência falou mais alto. Desativou antes de explodir.", 0.03)
        jogador.ganhar_xp(25)
    else:
        dano = random.randint(28, 45)
        jogador.hp = max(1, jogador.hp - dano)
        jogador.aplicar_queimadura(3, 1)
        texto_lento(f"  Explodiu. -{dano} HP e queimadura.", 0.03)
    continuar()


def _evento_terminal_quebrado(jogador: Personagem) -> None:
    limpar_tela()
    caixa_narrativa("Um terminal antigo ainda pisca. A interface está quebrada, mas talvez processe algo.")
    print()
    escolha = menu_escolha("O que você tenta?", [
        "Forçar comando de cura", "Tentar boost de ATK", "Ignorar"
    ])
    if escolha == 1:
        if random.random() < 0.6:
            curado = jogador.curar(35 + jogador.level * 3)
            texto_lento(f"  Terminal respondeu. +{curado} HP.", 0.03)
        else:
            texto_lento("  Erro de execução. Nada aconteceu.", 0.03)
    elif escolha == 2:
        if random.random() < 0.5:
            jogador.dano += 2
            texto_lento(f"  Terminal compilou. ATK +2 permanente.", 0.03)
        else:
            dano = random.randint(8, 16)
            jogador.hp = max(1, jogador.hp - dano)
            texto_lento(f"  Execução falhou. -{dano} HP.", 0.03)
    else:
        texto_lento("  Sábio.", 0.03)
    continuar()


def _evento_mercante_volante(jogador: Personagem) -> None:
    limpar_tela()
    caixa_narrativa("Um mercante aparece do nada com uma mochila enorme.")
    print()
    item_chave = random.choice(["pocao_hp", "pocao_mp", "bomba", "antidoto"])
    preco = random.randint(12, 22)
    nomes = {"pocao_hp": "Poção HP", "pocao_mp": "Poção MP", "bomba": "Bomba Arcana", "antidoto": "Antídoto"}
    texto_lento(f"  Mercante: \"{nomes[item_chave]} por {preco}g.\"", 0.03)
    texto_lento(f"  Seu ouro: {jogador.ouro}g", 0.03)
    r = input(cor("  Comprar? [s/n]: ", YELLOW)).strip().lower()
    if r in {"s", "sim"} and jogador.ouro >= preco:
        jogador.ouro -= preco
        jogador.adicionar_item(item_chave, 1)
        texto_lento(f"  ✅ Comprado por {preco}g.", 0.03)
    elif r in {"s", "sim"}:
        texto_lento("  Sem ouro suficiente.", 0.03)
    else:
        texto_lento("  O mercante desaparece.", 0.03)
    continuar()


def _evento_eco_do_passado(jogador: Personagem) -> None:
    limpar_tela()
    caixa_narrativa("Uma voz ressoa. Não é de ninguém vivo — é um eco gravado.")
    print()
    msgs = [
        "\"O Guardião do Kernel tem um ponto cego no turno três. Use skill.\"",
        "\"A Rainha da Latência fica mais devagar quando está abaixo de 40%.\"",
        "\"Guarda sempre que tiver MP alto. O boss não perdoa descuido.\"",
        "\"O Imperador do Caos... ele cansa. Resiste longo o suficiente.\"",
    ]
    texto_lento(f"  {random.choice(msgs)}", 0.03)
    jogador.ganhar_xp(12)
    continuar()


def _evento_cripta_de_dados(jogador: Personagem) -> None:
    limpar_tela()
    caixa_narrativa("Uma cripta de dados — paredes de código fossilizado. Pode ter algo valioso. Pode ter algo perigoso.")
    print()
    escolha = menu_escolha("Entrar na cripta?", ["Entrar e explorar", "Passar por fora"])
    if escolha == 1:
        resultado = random.random()
        if resultado < 0.45:
            ouro_extra = random.randint(20, 50)
            jogador.adicionar_ouro(ouro_extra)
            jogador.ganhar_xp(30)
            texto_lento(f"  Encontrou {ouro_extra}g e memória valiosa.", 0.03)
        elif resultado < 0.70:
            jogador.adicionar_item("bomba", 1)
            jogador.adicionar_item("antidoto", 1)
            texto_lento("  Dois itens de alguém que não voltou.", 0.03)
        else:
            dano = random.randint(20, 35)
            jogador.hp = max(1, jogador.hp - dano)
            texto_lento(f"  Armadilha. -{dano} HP.", 0.03)
    else:
        texto_lento("  Prudência não é fraqueza.", 0.03)
    continuar()


def _evento_fragmento_de_kernel(jogador: Personagem) -> None:
    limpar_tela()
    caixa_narrativa("Um fragmento de kernel flutuante — pequeno, mas denso de poder.")
    print()
    jogador.ganhar_xp(40)
    bonus = random.choice(["hp", "mp", "atk"])
    if bonus == "hp":
        jogador.hp_max += 15
        jogador.hp = min(jogador.hp_max, jogador.hp + 15)
        texto_lento("  HP máx +15.", 0.03)
    elif bonus == "mp":
        jogador.mp_max += 12
        jogador.mp = min(jogador.mp_max, jogador.mp + 12)
        texto_lento("  MP máx +12.", 0.03)
    else:
        jogador.dano += 2
        texto_lento("  ATK +2 permanente.", 0.03)
    continuar()


def _evento_precipicio(jogador: Personagem) -> None:
    limpar_tela()
    caixa_narrativa("Um precipício digital. Do outro lado, um atalho. Abaixo, uma queda sem fim.")
    print()
    escolha = menu_escolha("O que você faz?", ["Tentar saltar", "Procurar caminho alternativo"])
    if escolha == 1:
        if random.random() < 0.55 + jogador.sorte * 0.3:
            texto_lento("  Saltou. Chegou.", 0.03)
            jogador.ganhar_xp(25)
            jogador.curar(10)
        else:
            dano = random.randint(25, 40)
            jogador.hp = max(1, jogador.hp - dano)
            texto_lento(f"  Não chegou longe o suficiente. -{dano} HP.", 0.03)
    else:
        texto_lento("  +10 XP pela prudência.", 0.03)
        jogador.ganhar_xp(10)
    continuar()


def _evento_mensagem_do_caos(jogador: Personagem) -> None:
    limpar_tela()
    caixa_narrativa("Letras vermelhas no ar: \"Você não chegará até mim. Mas pode tentar.\"")
    print()
    texto_lento("  É o Imperador. Ele sabe que você está vindo.", 0.03)
    texto_lento("  Você sente a adrenalina subir. Não é medo — é foco.", 0.03)
    jogador.aplicar_furia(4, 3)
    texto_lento("  Fúria ativada por 3 turnos.", 0.03)
    continuar()


# ── Eventos exclusivos NG+ ────────────────────────────────────

def _evento_ng_eco_do_vazio(jogador: Personagem) -> None:
    limpar_tela()
    caixa_narrativa("Um eco do Vazio — não um ataque, não uma presença. Só uma ausência que você sente.")
    print()
    texto_lento("  Por um segundo você entende o que o Vazio quer: terminar.", 0.03)
    texto_lento("  Não destruir. Terminar. Há uma diferença.", 0.03)
    jogador.ganhar_xp(60)
    jogador.hp = min(jogador.hp_max, jogador.hp + 30)
    texto_lento("  +60 XP. +30 HP. Algo nessa compreensão te fortaleceu.", 0.03)
    continuar()


def _evento_ng_fragmento_corrompido(jogador: Personagem) -> None:
    limpar_tela()
    caixa_narrativa("Um fragmento de código corrompido flutua — parece instável, mas poderoso.")
    print()
    escolha = menu_escolha("O que você faz?", ["Absorver o fragmento", "Destruí-lo com segurança"])
    if escolha == 1:
        if random.random() < 0.55:
            jogador.dano   += 4
            jogador.hp_max += 20
            jogador.hp      = jogador.hp_max
            texto_lento("  Absorção bem-sucedida. ATK +4 | HP máx +20.", 0.03)
        else:
            dano = random.randint(30, 50)
            jogador.hp = max(1, jogador.hp - dano)
            texto_lento(f"  Explosão durante absorção. -{dano} HP.", 0.03)
    else:
        jogador.ganhar_xp(35)
        texto_lento("  Destruído com segurança. +35 XP.", 0.03)
    continuar()


def _evento_ng_mensagem_sem_remetente(jogador: Personagem) -> None:
    limpar_tela()
    caixa_narrativa("Uma mensagem aparece no terminal. Sem remetente. Sem data.")
    print()
    msgs_void = [
        "\"Você passou pela tela azul. Mas a tela azul também passou por você.\"",
        "\"O Vazio não é o inimigo. Você é a anomalia. A diferença importa.\"",
        "\"Cada sistema que você derrubou foi um aviso. Este é o último.\"",
        "\"Eu existo porque o sistema precisava de um fim. Você existe porque não aceita isso.\"",
    ]
    texto_lento(f"  {random.choice(msgs_void)}", 0.03)
    jogador.aplicar_furia(6, 4)
    texto_lento("  A mensagem desaparece. Fúria ativada por 4 turnos.", 0.03)
    continuar()


def _evento_ng_espelho_digital(jogador: Personagem) -> None:
    limpar_tela()
    caixa_narrativa("Um espelho digital no meio do caminho. Mostra você — mas não exatamente você.")
    print()
    texto_lento(
        "  A versão no espelho tem mais cicatrizes. Mais desgaste. "
        "Mas os olhos têm algo que os seus não têm: certeza.",
        0.03,
    )
    texto_lento(
        "  A versão no espelho faz um gesto simples: continua.",
        0.03,
    )
    jogador.hp = jogador.hp_max
    jogador.mp = jogador.mp_max
    texto_lento("  HP e MP restaurados. O espelho se estilhaça.", 0.03)
    continuar()


def _evento_ng_processo_reanimado(jogador: Personagem) -> None:
    limpar_tela()
    caixa_narrativa("Um processo reanimado bloqueia o caminho. Não é hostil. Está com medo.")
    print()
    escolha = menu_escolha("O que você faz?", [
        "Ajudar o processo a encerrar com dignidade",
        "Ignorar e passar",
    ])
    if escolha == 1:
        jogador.ganhar_xp(70)
        jogador.adicionar_item("pocao_hp", 2)
        jogador.adicionar_item("pocao_mp", 1)
        texto_lento("  Você o ajudou a encerrar. +70 XP. 2 Poções HP + 1 Poção MP.", 0.03)
        texto_lento("  Ele te deu o que tinha antes de sair.", 0.03)
    else:
        texto_lento("  Você passa. O processo continua preso lá.", 0.03)
    continuar()
