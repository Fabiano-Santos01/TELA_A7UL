import random
from typing import List

from src.base import Combatente
from src.utils import texto_lento


class Mob(Combatente):
    def __init__(self, nome: str, hp: int, dano: int, defesa: int, sorte: float,
                 skill: str, xp: int, ouro: int):
        super().__init__(nome, hp, dano, defesa, sorte)
        self.skill = skill
        self.xp = xp
        self.ouro = ouro

    def frase_entrada(self) -> str:
        frases = [
            f"{self.nome} surge do lixo digital sem aviso.",
            f"{self.nome} para no caminho. Não vai sair por bem.",
            f"{self.nome} fareja você como processo zumbi farejando CPU.",
            f"Um {self.nome} aparece. Não parece amigável.",
        ]
        return random.choice(frases)

    def frase_ataque(self) -> str:
        frases = [
            f"{self.nome} avança sem pensar duas vezes.",
            f"{self.nome} tenta abrir sua defesa na marra.",
            f"{self.nome} vem no braço, sem cerimônia.",
            f"{self.nome} lança um golpe torto mas pesado.",
        ]
        return random.choice(frases)

    def frase_skill(self) -> str:
        frases = [
            f"{self.nome} prepara algo sujo.",
            f"{self.nome} muda a forma antes de bater.",
            f"{self.nome} solta uma jogada perigosa.",
        ]
        return random.choice(frases)

    def frase_morte(self) -> str:
        frases = [
            f"{self.nome} some em fragmentos de ruído.",
            f"{self.nome} cai, e o código ao redor some junto.",
            f"{self.nome} se desmonta como arquivo corrompido.",
            f"O {self.nome} pisca uma vez e desaparece do registro.",
        ]
        return random.choice(frases)

    def atacar(self, alvo: Combatente) -> str:
        if self.esta_atordoado():
            texto_lento(f"💫 {self.nome} está atordoado e perdeu o turno.", 0.03)
            return "stun"
        texto_lento(self.frase_ataque(), 0.03)
        base = self.dano + self.rage_bonus
        chance_critico = min(0.30, 0.10 + self.sorte)
        if random.random() < chance_critico:
            dano = int(round(base * 1.75))
            texto_lento(f"⚡ CRÍTICO! {self.nome} acertou em cheio: {dano} de dano.", 0.03)
        else:
            dano = int(round(base))
            texto_lento(f"{self.nome} atacou {alvo.nome}. {dano} de dano.", 0.03)
        alvo.receber_dano(dano, origem=self.nome)
        return "ataque"

    def habilidade(self, alvo: Combatente) -> str:
        if self.esta_atordoado():
            texto_lento(f"💫 {self.nome} não conseguiu usar {self.skill}.", 0.03)
            return "stun"
        texto_lento(self.frase_skill(), 0.03)
        texto_lento(f"✨ {self.nome} ativou {self.skill}.", 0.03)

        sk = self.skill

        if sk == "Mordida Corrupta":
            dano = int(round((self.dano + 2) * 1.2))
            alvo.receber_dano(dano, origem=self.nome)
            alvo.aplicar_sangramento(2, 2)
            texto_lento(f"🩸 Sangramento leve aplicado em {alvo.nome}.", 0.03)
        elif sk == "Desvio de Dados":
            dano = int(round((self.dano + 2) * 1.25))
            alvo.receber_dano(dano, origem=self.nome)
            if random.random() < 0.30:
                alvo.aplicar_defesa_extra(-2, 2)
                texto_lento(f"📉 A defesa de {alvo.nome} vacilou.", 0.03)
        elif sk == "Linha Quebrada":
            dano = int(round((self.dano + 3) * 1.35))
            alvo.receber_dano(dano, origem=self.nome)
            if random.random() < 0.20:
                alvo.stun_turns = max(alvo.stun_turns, 1)
                texto_lento(f"💥 {alvo.nome} ficou atordoado.", 0.03)
        elif sk == "Faísca Rápida":
            dano = int(round((self.dano + 2) * 1.15))
            alvo.receber_dano(dano, origem=self.nome)
            self.curar(3)
            texto_lento(f"⚡ {self.nome} deu um golpe rápido e recuperou energia.", 0.03)
        elif sk == "Ruído de Fundo":
            dano = int(round(self.dano * 1.10))
            alvo.receber_dano(dano, origem=self.nome)
            alvo.aplicar_vulnerabilidade(1.08, 2)
            texto_lento(f"📡 {alvo.nome} ficou desorientado.", 0.03)
        elif sk == "Erro Fatal":
            dano = int(round((self.dano + 4) * 1.45))
            alvo.receber_dano(dano, origem=self.nome)
            alvo.aplicar_queimadura(3, 2)
            texto_lento(f"🔥 {alvo.nome} está queimando.", 0.03)
        elif sk == "Lacuna Rápida":
            dano = int(round((self.dano + 5) * 1.35))
            alvo.receber_dano(dano, origem=self.nome)
            curado = self.curar(4 + self.dano // 4)
            if curado > 0:
                texto_lento(f"🌀 {self.nome} se recompôs um pouco.", 0.03)
        elif sk == "Pulso Negativo":
            dano = int(round((self.dano + 5) * 1.40))
            alvo.receber_dano(dano, origem=self.nome)
            alvo.aplicar_defesa_extra(-1, 2)
            texto_lento(f"📴 {alvo.nome} perdeu estabilidade.", 0.03)
        elif sk == "Queimadura":
            dano = int(round((self.dano + 6) * 1.45))
            alvo.receber_dano(dano, origem=self.nome)
            alvo.aplicar_queimadura(4, 2)
            texto_lento(f"🔥 Chamas no corpo de {alvo.nome}.", 0.03)
        elif sk == "Ataque em Loop":
            texto_lento("🔁 Dois pulsos de energia atravessam o campo.", 0.03)
            for _ in range(2):
                dano = int(round((self.dano + 3) * 0.85))
                alvo.receber_dano(dano, origem=self.nome)
        elif sk == "Eco Caótico":
            dano = int(round((self.dano + 6) * 1.50))
            alvo.receber_dano(dano, origem=self.nome)
            self.aplicar_furia(3, 2)
            texto_lento(f"📢 {self.nome} entrou em fúria.", 0.03)
        elif sk == "Registro Explosivo":
            dano = int(round((self.dano + 7) * 1.55))
            alvo.receber_dano(dano, origem=self.nome)
            alvo.aplicar_sangramento(4, 2)
            texto_lento(f"💣 {alvo.nome} levou dano explosivo.", 0.03)
        # ── Skills exclusivas do NG+ ──────────────────────────
        elif sk == "Corrupção Profunda":
            dano = int(round((self.dano + 8) * 1.55))
            alvo.receber_dano(dano, origem=self.nome)
            alvo.aplicar_queimadura(5, 3)
            alvo.aplicar_sangramento(4, 2)
            texto_lento(f"🕳️  {alvo.nome} foi corrompido em dois níveis.", 0.03)
        elif sk == "Glitch de Realidade":
            # Efeito aleatório pesado
            ef = random.choice(["burn", "bleed", "stun", "vuln"])
            dano = int(round((self.dano + 6) * 1.45))
            alvo.receber_dano(dano, origem=self.nome)
            if ef == "burn":
                alvo.aplicar_queimadura(6, 3)
                texto_lento("🔥 Glitch queimou o alvo por 3 turnos.", 0.03)
            elif ef == "bleed":
                alvo.aplicar_sangramento(6, 3)
                texto_lento("🩸 Glitch abriu ferida profunda.", 0.03)
            elif ef == "stun":
                alvo.stun_turns = max(alvo.stun_turns, 2)
                texto_lento(f"💫 Glitch travou {alvo.nome} por 2 turnos.", 0.03)
            else:
                alvo.aplicar_vulnerabilidade(1.22, 3)
                texto_lento(f"📉 Glitch deixou {alvo.nome} crítico.", 0.03)
        elif sk == "Pulso do Abismo":
            for _ in range(3):
                dano = int(round(self.dano * 0.75))
                alvo.receber_dano(dano, origem=self.nome)
            texto_lento("🌑 Três pulsos do abismo atravessaram o campo.", 0.03)
        elif sk == "Reescrita de Memória":
            dano = int(round((self.dano + 9) * 1.60))
            alvo.receber_dano(dano, origem=self.nome)
            alvo.aplicar_defesa_extra(-4, 3)
            self.curar(int(dano * 0.3))
            texto_lento(f"🧠 Memória reescrita. {self.nome} absorveu parte do impacto.", 0.03)
        elif sk == "Fragmento Fantasma":
            dano = int(round((self.dano + 7) * 1.50))
            alvo.receber_dano(dano, origem=self.nome)
            if random.random() < 0.45:
                alvo.stun_turns = max(alvo.stun_turns, 1)
                alvo.aplicar_vulnerabilidade(1.15, 2)
                texto_lento(f"👻 Fragmento atordoou e expôs {alvo.nome}.", 0.03)
        elif sk == "Loop Infinito":
            hits = random.randint(2, 5)
            for i in range(hits):
                dano = int(round(self.dano * 0.65))
                alvo.receber_dano(dano, origem=self.nome)
                texto_lento(f"🔁 Iteração {i+1}/{hits}: {dano}.", 0.03)
                if not alvo.esta_vivo():
                    break
        elif sk == "Void Strike":
            def_salva = alvo.defesa
            alvo.defesa = 0
            dano = int(round((self.dano + 10) * 1.65))
            alvo.receber_dano(dano, origem=self.nome)
            alvo.defesa = def_salva
            texto_lento(f"🕳️  Void Strike ignora toda defesa. {dano} de dano puro.", 0.03)
        elif sk == "Cascata de Erros":
            texto_lento("💥 Uma cascata de erros se propaga...", 0.03)
            dano_base = self.dano + 5
            for i in range(4):
                mult = 0.5 + i * 0.25
                dano = int(round(dano_base * mult))
                alvo.receber_dano(dano, origem=self.nome)
                texto_lento(f"   Erro {i+1}: {dano} de dano.", 0.03)
                if not alvo.esta_vivo():
                    break
        else:
            return self.atacar(alvo)

        return "skill"


class Boss(Combatente):
    def __init__(self, nome: str, hp: int, dano: int, defesa: int, sorte: float,
                 skill: str, falar: str, xp: int, ouro: int):
        super().__init__(nome, hp, dano, defesa, sorte)
        self.skill = skill
        self.falar = falar
        self.xp = xp
        self.ouro = ouro
        self.falas_ativadas: List[int] = []

    def frase_entrada(self) -> str:
        frases = [
            f"{self.nome} entra na arena sem pedir licença.",
            f"O clima fecha de vez. {self.nome} chegou.",
            f"{self.nome} olha para você como quem já escolheu o vencedor.",
            f"Uma presença pesada domina o ambiente. É {self.nome}.",
        ]
        return random.choice(frases)

    def frase_morte(self) -> str:
        frases = [
            f"{self.nome} colapsa em silêncio digital.",
            f"O código de {self.nome} se fragmenta para sempre.",
            f"{self.nome} cai. O sistema registra. Ninguém chora.",
        ]
        return random.choice(frases)

    def falar_fase(self) -> None:
        porcentagem = (self.hp / self.hp_max) * 100 if self.hp_max else 0
        fases = [
            (90, "Então você realmente veio até aqui..."),
            (75, "Ainda acha que pode me parar?"),
            (60, self.falar),
            (45, "Agora você está começando a entender o erro."),
            (30, "Eu ainda nem comecei de verdade."),
            (15, "Isso... não... era... para... acontecer..."),
        ]
        for limite, fala in fases:
            if porcentagem <= limite and limite not in self.falas_ativadas:
                self.falas_ativadas.append(limite)
                texto_lento(f"\n🗣️  {self.nome}: \"{fala}\"\n", 0.03)
                break

    def atacar(self, alvo: Combatente) -> str:
        if self.esta_atordoado():
            texto_lento(f"💫 {self.nome} perdeu a chance de atacar.", 0.03)
            return "stun"
        texto_lento(f"{self.nome} arma um golpe pesado.", 0.03)
        chance_critico = min(0.38, 0.16 + self.sorte)
        base = self.dano + self.rage_bonus
        if random.random() < chance_critico:
            dano = int(round(base * 2.0))
            texto_lento(f"⚡ CRÍTICO! {self.nome} desferiu {dano} de dano em {alvo.nome}.", 0.03)
        else:
            dano = int(round(base))
            texto_lento(f"{self.nome} atacou {alvo.nome}: {dano} de dano.", 0.03)
        alvo.receber_dano(dano, origem=self.nome)
        self.falar_fase()
        return "ataque"

    def habilidade(self, alvo: Combatente) -> str:
        if self.esta_atordoado():
            texto_lento(f"💫 {self.nome} não conseguiu usar {self.skill}.", 0.03)
            return "stun"
        texto_lento(f"🔥 {self.nome} ativou {self.skill}!", 0.03)

        sk = self.skill

        if sk == "Bafo Infernal":
            dano = int(round(self.dano * 1.65))
            alvo.receber_dano(dano, origem=self.nome)
            alvo.aplicar_queimadura(5, 3)
            texto_lento(f"🔥 {alvo.nome} está em chamas.", 0.03)
        elif sk == "Delay Absoluto":
            dano = int(round(self.dano * 1.45))
            alvo.receber_dano(dano, origem=self.nome)
            alvo.stun_turns = max(alvo.stun_turns, 1)
            texto_lento(f"⏳ {alvo.nome} ficou travado.", 0.03)
        elif sk == "Estrutura Fraturada":
            dano = int(round(self.dano * 1.75))
            alvo.receber_dano(dano, origem=self.nome)
            alvo.aplicar_defesa_extra(-3, 3)
            texto_lento(f"💢 A defesa de {alvo.nome} foi comprometida.", 0.03)
        elif sk == "Tempestade Binária":
            texto_lento("🌩️  Uma sequência de ataques paralelos varre a arena.", 0.03)
            for _ in range(2):
                dano = int(round(self.dano * 0.90))
                alvo.receber_dano(dano, origem=self.nome)
            alvo.aplicar_sangramento(5, 2)
        elif sk == "Colapso de Memória":
            dano = int(round(self.dano * 1.80))
            alvo.receber_dano(dano, origem=self.nome)
            alvo.aplicar_vulnerabilidade(1.18, 2)
            self.curar(int(self.hp_max * 0.08))
            texto_lento(f"🧠 {self.nome} consumiu parte da sua energia e se recuperou.", 0.03)
        elif sk == "Apocalipse de Código":
            dano = int(round(self.dano * 1.90))
            alvo.receber_dano(dano, origem=self.nome)
            alvo.aplicar_queimadura(6, 2)
            alvo.aplicar_sangramento(5, 2)
            self.aplicar_furia(5, 3)
            texto_lento(f"☠️  {alvo.nome} foi atingido por múltiplos efeitos.", 0.03)
        # ── Skills exclusivas NG+ ─────────────────────────────
        elif sk == "Reboot Forçado":
            dano = int(round(self.dano * 1.85))
            alvo.receber_dano(dano, origem=self.nome)
            alvo.stun_turns = max(alvo.stun_turns, 2)
            alvo.aplicar_vulnerabilidade(1.20, 3)
            texto_lento(f"🔄 {alvo.nome} foi reiniciado à força. Atordoado por 2 turnos.", 0.03)
        elif sk == "Kernel Panic":
            texto_lento("💀 KERNEL PANIC — todos os sistemas falhando...", 0.03)
            for _ in range(3):
                dano = int(round(self.dano * 0.85))
                alvo.receber_dano(dano, origem=self.nome)
            alvo.aplicar_queimadura(7, 3)
            alvo.aplicar_sangramento(6, 3)
            self.curar(int(self.hp_max * 0.12))
            texto_lento(f"💥 Kernel panic aplicou 3 golpes + efeitos + cura em {self.nome}.", 0.03)
        elif sk == "Singularidade Negra":
            def_salva = alvo.defesa
            alvo.defesa = 0
            dano = int(round(self.dano * 2.20))
            alvo.receber_dano(dano, origem=self.nome)
            alvo.defesa = def_salva
            alvo.aplicar_vulnerabilidade(1.25, 3)
            texto_lento(f"🌑 Singularidade Negra. Defesa ignorada. {dano} de dano devastador.", 0.03)
        elif sk == "Overwrite Total":
            dano = int(round(self.dano * 2.0))
            alvo.receber_dano(dano, origem=self.nome)
            alvo.aplicar_queimadura(8, 3)
            alvo.aplicar_sangramento(7, 3)
            alvo.stun_turns = max(alvo.stun_turns, 1)
            self.aplicar_furia(8, 4)
            texto_lento(f"📝 Overwrite Total. {alvo.nome} foi completamente sobrescrito.", 0.03)
        elif sk == "Void Absolute":
            # Skill definitiva do boss final do NG+
            texto_lento("🕳️  O VAZIO SE ABRE...", 0.05)
            import time as _t
            _t.sleep(0.6)
            def_salva = alvo.defesa
            alvo.defesa = 0
            for i in range(5):
                mult = 0.6 + i * 0.18
                dano = int(round(self.dano * mult))
                alvo.receber_dano(dano, origem=self.nome)
                texto_lento(f"   Onda {i+1}: {dano}.", 0.02)
                if not alvo.esta_vivo():
                    break
            alvo.defesa = def_salva
            alvo.aplicar_queimadura(10, 4)
            alvo.aplicar_sangramento(8, 4)
            alvo.aplicar_vulnerabilidade(1.30, 3)
            self.curar(int(self.hp_max * 0.15))
            texto_lento("🕳️  O vazio recua. Por enquanto.", 0.03)
        else:
            return self.atacar(alvo)

        self.falar_fase()
        return "skill"

    def escolher_acao(self, alvo: Combatente) -> str:
        self.falar_fase()
        vida = self.hp / self.hp_max if self.hp_max else 0
        if vida <= 0.30 and random.random() < 0.72:
            return self.habilidade(alvo)
        if vida <= 0.55 and random.random() < 0.48:
            return self.habilidade(alvo)
        if random.random() < 0.32:
            return self.habilidade(alvo)
        return self.atacar(alvo)


# ─────────────────────────────────────────────────────────────
#  CAMPANHA PRINCIPAL
# ─────────────────────────────────────────────────────────────
def criar_inimigos() -> List[Mob]:
    return [
        Mob("Processo Morto",       22,  4, 0, 0.02, "Faísca Rápida",     18,  3),
        Mob("Bit Corrompido",       28,  5, 0, 0.03, "Ruído de Fundo",    22,  4),
        Mob("Rato de Stack",        35,  6, 1, 0.03, "Mordida Corrupta",  28,  5),
        Mob("Bug de Memória",       42,  7, 1, 0.04, "Desvio de Dados",   32,  6),
        Mob("Imp do Terminal",      52,  8, 2, 0.06, "Linha Quebrada",    38,  8),
        Mob("Códice Fendido",       60,  9, 2, 0.05, "Erro Fatal",        44,  9),
        Mob("Gárgula do Cache",     70, 10, 3, 0.07, "Lacuna Rápida",     52, 11),
        Mob("Drone da Falha",       80, 11, 3, 0.07, "Pulso Negativo",    58, 13),
        Mob("Serpente de Firewall", 92, 12, 4, 0.09, "Queimadura",        66, 16),
        Mob("Noctívago do Kernel", 104, 13, 5, 0.10, "Ataque em Loop",    74, 18),
        Mob("Cultista do Ping",    118, 14, 4, 0.11, "Eco Caótico",       84, 20),
        Mob("Golem de Log",        132, 15, 6, 0.10, "Registro Explosivo",96, 24),
    ]


def criar_bosses() -> List[Boss]:
    return [
        Boss("Capetão do Stack",   160, 16,  5, 0.11, "Bafo Infernal",
             "Achei que não passariam dos primeiros bugs.", 110, 45),
        Boss("Rainha da Latência", 210, 19,  7, 0.14, "Delay Absoluto",
             "Aqui tudo chega tarde. Inclusive a sua sorte.", 145, 65),
        Boss("Arquiteto de Ruínas",260, 22,  8, 0.15, "Estrutura Fraturada",
             "Construí ruínas que vocês não vão entender.", 185, 85),
        Boss("Guardião do Kernel", 320, 25, 10, 0.17, "Tempestade Binária",
             "O núcleo não aceita visitantes.", 230, 110),
        Boss("Imperador do Caos",  480, 29, 12, 0.21, "Apocalipse de Código",
             "O fim do sistema veio para ficar. E você veio junto.", 300, 150),
    ]


# ─────────────────────────────────────────────────────────────
#  NEW GAME+ — Beyond the Kernel
# ─────────────────────────────────────────────────────────────
def criar_inimigos_ng() -> List[Mob]:
    """10 mobs do NG+ — mais pesados, com skills inéditas."""
    return [
        # ── Setor Esquecido
        Mob("Eco do Sistema",      180, 24,  8, 0.14, "Glitch de Realidade",  140, 35),
        Mob("Processo Reanimado",  210, 26,  9, 0.15, "Corrupção Profunda",   160, 40),
        # ── Câmara Void
        Mob("Sombra de Processo",  240, 28, 10, 0.16, "Fragmento Fantasma",   185, 48),
        Mob("Daemon Invertido",    265, 30, 11, 0.17, "Pulso do Abismo",      200, 55),
        # ── Arquivo Proibido
        Mob("Bit do Vazio",        290, 32, 12, 0.18, "Loop Infinito",        220, 62),
        Mob("Entidade de Stack",   320, 34, 13, 0.19, "Reescrita de Memória", 245, 70),
        # ── Núcleo Corrompido
        Mob("Kernel Fantasma",     355, 36, 14, 0.20, "Cascata de Erros",     270, 78),
        Mob("Glitch Primordial",   390, 38, 15, 0.21, "Void Strike",          295, 86),
        # ── Antecâmara do Vazio
        Mob("Fragmento do Caos",   430, 40, 16, 0.22, "Glitch de Realidade",  320, 95),
        Mob("Executável Corrompido",470, 42, 17, 0.23, "Cascata de Erros",     350, 105),
    ]


def criar_bosses_ng() -> List[Boss]:
    """3 bosses do NG+ — muito mais duros que o Imperador."""
    return [
        Boss(
            "Overseer do Setor",   650, 36, 14, 0.25,
            "Reboot Forçado",
            "Você não deveria existir nessa iteração do sistema.",
            380, 180,
        ),
        Boss(
            "Núcleo Corrompido",   820, 42, 16, 0.28,
            "Kernel Panic",
            "Cada vez que você me derrota, eu recompilo mais forte.",
            480, 240,
        ),
        Boss(
            "O VAZIO",            1200, 52, 20, 0.32,
            "Void Absolute",
            "Eu sou o que fica quando tudo mais falha. Você deveria ter parado no Imperador.",
            700, 350,
        ),
    ]


# ─────────────────────────────────────────────────────────────
#  MODO RECRUTADOR — campanha compacta independente
# ─────────────────────────────────────────────────────────────
def criar_inimigos_recrutador() -> List[Mob]:
    return [
        Mob("Processo Fantasma",   55,  9, 2, 0.07, "Ruído de Fundo",   45, 10),
        Mob("Bug Persistente",     75, 11, 3, 0.08, "Linha Quebrada",    55, 14),
        Mob("Daemon Corrupto",     95, 13, 4, 0.10, "Erro Fatal",        70, 18),
        Mob("Kernel Instável",    115, 15, 5, 0.11, "Eco Caótico",       85, 22),
    ]


def criar_bosses_recrutador() -> List[Boss]:
    return [
        Boss(
            "Gerente de Projeto",  200, 18,  7, 0.14,
            "Delay Absoluto",
            "Cada requisito que você cumpre, eu adiciono três novos.",
            120, 55,
        ),
        Boss(
            "O Sistema Legado",    320, 22, 10, 0.17,
            "Estrutura Fraturada",
            "Ninguém entende meu código. Inclusive eu.",
            200, 90,
        ),
    ]
