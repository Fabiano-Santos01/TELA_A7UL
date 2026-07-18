import json
import random
from pathlib import Path
from typing import Dict, List, Optional, Any

from src.base import Combatente
from src.utils import texto_lento, exibir_estado, menu_escolha, continuar, cor, CYAN, YELLOW, GREEN, MAGENTA, RED, BOLD, RESET
from src.audio import audio as _audio


# ─────────────────────────────────────────────────────────────
#  CLASSES BASE
# ─────────────────────────────────────────────────────────────
CLASSES_BASE: Dict[str, Dict[str, Any]] = {
    "Bruxo": {
        "hp": 115, "dano": 13, "defesa": 7, "sorte": 0.12, "mp": 75,
        "skill": "Bom Humor",
        "descricao": "Equilibrado. Cura e ataque ao mesmo tempo. Bom pra quem quer controle.",
    },
    "Bruxo da Programação": {
        "hp": 105, "dano": 15, "defesa": 6, "sorte": 0.15, "mp": 90,
        "skill": "Encontrar Bug",
        "descricao": "Especialista em dano múltiplo. Corrói a defesa do inimigo com precisão.",
    },
    "Berserker": {
        "hp": 155, "dano": 20, "defesa": 11, "sorte": 0.08, "mp": 50,
        "skill": "Fúria do Carcará",
        "descricao": "Tanque bruto. Alto HP e ATK, mas gasta MP rápido.",
    },
    "Sanguinário": {
        "hp": 130, "dano": 18, "defesa": 7, "sorte": 0.17, "mp": 62,
        "skill": "Frenesi",
        "descricao": "Vampirismo em combate. Se cura com o que causa. Estilo agressivo.",
    },
    "Tecnomante": {
        "hp": 100, "dano": 14, "defesa": 7, "sorte": 0.16, "mp": 100,
        "skill": "Cache Arcano",
        "descricao": "Mago de foco. Acumula bônus para explodir o inimigo no momento certo.",
    },
    "Paladino do Código": {
        "hp": 145, "dano": 17, "defesa": 14, "sorte": 0.09, "mp": 62,
        "skill": "Selo de Patch",
        "descricao": "Defesa altíssima. Usa a própria blindagem para atacar. Difícil de matar.",
    },
    "Assassino de Stack": {
        "hp": 108, "dano": 22, "defesa": 5, "sorte": 0.22, "mp": 58,
        "skill": "Corte Fantasma",
        "descricao": "Alta sorte e golpes múltiplos. Frágil, mas letal nas mãos certas.",
    },
    "Hacker Selvagem": {
        "hp": 120, "dano": 17, "defesa": 8, "sorte": 0.14, "mp": 70,
        "skill": "Injeção de Caos",
        "descricao": "Ataca e aplica efeitos aleatórios no inimigo. Imprevisível.",
    },
}

# ─────────────────────────────────────────────────────────────
#  SUBCLASSES
# ─────────────────────────────────────────────────────────────
SUBCLASSES: Dict[str, List[Dict[str, Any]]] = {
    "Bruxo": [
        {"nome": "Bruxo Astral",        "nivel_min": 5,  "skill_extra": "Vínculo Etéreo",
         "descricao": "Ganha regen passiva e dano arcano aumentado.",
         "bonus": {"hp": 25, "mp": 20, "dano": 5, "defesa": 2, "sorte": 0.02}},
        {"nome": "Mago de Compilação",  "nivel_min": 10, "skill_extra": "Sobrecarga Arcana",
         "descricao": "Libera dois feitiços por turno com chance de crit.",
         "bonus": {"hp": 30, "mp": 25, "dano": 7, "defesa": 3, "sorte": 0.02}},
        {"nome": "Arquimago do Código", "nivel_min": 15, "skill_extra": "Singularidade",
         "descricao": "Golpe único que escala com MP atual. Devastador.",
         "bonus": {"hp": 40, "mp": 35, "dano": 10, "defesa": 4, "sorte": 0.03}},
    ],
    "Bruxo da Programação": [
        {"nome": "Debugger Arcano",       "nivel_min": 5,  "skill_extra": "Stack Trace",
         "descricao": "Analisa o inimigo e aplica vulnerabilidade antes de atacar.",
         "bonus": {"hp": 20, "mp": 25, "dano": 6, "defesa": 2, "sorte": 0.03}},
        {"nome": "Engenheiro de Stack",   "nivel_min": 10, "skill_extra": "Recursão Fatal",
         "descricao": "Ataque que se repete enquanto há MP disponível.",
         "bonus": {"hp": 25, "mp": 30, "dano": 8, "defesa": 2, "sorte": 0.03}},
        {"nome": "Mestre da Arquitetura","nivel_min": 15, "skill_extra": "Refactoring Letal",
         "descricao": "Reconstrói o próprio código em combate — cura e causa dano máximo.",
         "bonus": {"hp": 35, "mp": 40, "dano": 11, "defesa": 3, "sorte": 0.04}},
    ],
    "Berserker": [
        {"nome": "Fúria Primordial",    "nivel_min": 5,  "skill_extra": "Rugido Ancestral",
         "descricao": "Intimida o inimigo reduzindo seu ATK por turnos.",
         "bonus": {"hp": 35, "mp": 10, "dano": 7, "defesa": 4, "sorte": 0.01}},
        {"nome": "Berserker Ancestral", "nivel_min": 10, "skill_extra": "Tempestade de Ferro",
         "descricao": "Três golpes rápidos com bônus de fúria acumulada.",
         "bonus": {"hp": 45, "mp": 12, "dano": 9, "defesa": 5, "sorte": 0.01}},
        {"nome": "Titã de Guerra",      "nivel_min": 15, "skill_extra": "Colapso Total",
         "descricao": "Um único golpe que ignora metade da defesa do alvo.",
         "bonus": {"hp": 60, "mp": 15, "dano": 13, "defesa": 7, "sorte": 0.02}},
    ],
    "Sanguinário": [
        {"nome": "Cortesão Carmesim", "nivel_min": 5,  "skill_extra": "Pulso Carmesim",
         "descricao": "Aplica sangramento massivo e drena HP passivamente.",
         "bonus": {"hp": 28, "mp": 15, "dano": 6, "defesa": 2, "sorte": 0.04}},
        {"nome": "Lâmina Rubra",      "nivel_min": 10, "skill_extra": "Dança Sangrenta",
         "descricao": "Ataca dois alvos simulados — se um falha, o outro crit.",
         "bonus": {"hp": 35, "mp": 18, "dano": 8, "defesa": 3, "sorte": 0.04}},
        {"nome": "Ceifador do Sangue","nivel_min": 15, "skill_extra": "Colheita Sombria",
         "descricao": "Quanto menos HP o inimigo tem, mais dano causa.",
         "bonus": {"hp": 45, "mp": 22, "dano": 11, "defesa": 4, "sorte": 0.05}},
    ],
    "Tecnomante": [
        {"nome": "Tecnomante de Núcleo",  "nivel_min": 5,  "skill_extra": "Pulso de Núcleo",
         "descricao": "Gera bônus de ATK baseado em MP atual.",
         "bonus": {"hp": 22, "mp": 30, "dano": 6, "defesa": 2, "sorte": 0.03}},
        {"nome": "Arquiteto de Sistemas", "nivel_min": 10, "skill_extra": "Deploy Letal",
         "descricao": "Constrói um ataque acumulado com 3x o foco atual.",
         "bonus": {"hp": 28, "mp": 38, "dano": 8, "defesa": 3, "sorte": 0.03}},
        {"nome": "Soberano do Compilador","nivel_min": 15, "skill_extra": "Compilação Final",
         "descricao": "Toda a mana restante se converte em dano puro.",
         "bonus": {"hp": 35, "mp": 50, "dano": 11, "defesa": 4, "sorte": 0.04}},
    ],
    "Paladino do Código": [
        {"nome": "Guardião do Patch", "nivel_min": 5,  "skill_extra": "Barreira de Hotfix",
         "descricao": "Absorve o próximo ataque e reflete parte do dano.",
         "bonus": {"hp": 32, "mp": 15, "dano": 5, "defesa": 5, "sorte": 0.01}},
        {"nome": "Cruzado do Kernel", "nivel_min": 10, "skill_extra": "Julgamento do Root",
         "descricao": "Ataque sagrado que ignora guard e causa dano fixo.",
         "bonus": {"hp": 40, "mp": 18, "dano": 7, "defesa": 7, "sorte": 0.02}},
        {"nome": "Paladino Supremo",  "nivel_min": 15, "skill_extra": "Permissão Divina",
         "descricao": "Cura total + escudo por 3 turnos + dano divino.",
         "bonus": {"hp": 55, "mp": 25, "dano": 10, "defesa": 10, "sorte": 0.02}},
    ],
    "Assassino de Stack": [
        {"nome": "Lâmina Oculta",       "nivel_min": 5,  "skill_extra": "Sombra Afiada",
         "descricao": "Golpe invisível com alta chance de crítico.",
         "bonus": {"hp": 22, "mp": 18, "dano": 7, "defesa": 1, "sorte": 0.05}},
        {"nome": "Sombra de Produção",  "nivel_min": 10, "skill_extra": "Exploit Zero-Day",
         "descricao": "Ataca antes do inimigo agir. Ignora defesa parcialmente.",
         "bonus": {"hp": 28, "mp": 22, "dano": 9, "defesa": 2, "sorte": 0.05}},
        {"nome": "Executor Silencioso", "nivel_min": 15, "skill_extra": "Null Pointer",
         "descricao": "Um golpe que pode matar instantaneamente inimigos com <20% HP.",
         "bonus": {"hp": 36, "mp": 28, "dano": 13, "defesa": 3, "sorte": 0.06}},
    ],
    "Hacker Selvagem": [
        {"nome": "Intruso do Sistema", "nivel_min": 5,  "skill_extra": "SQL Injection",
         "descricao": "Ataque que bypassa parte da defesa e aplica dois efeitos.",
         "bonus": {"hp": 24, "mp": 20, "dano": 6, "defesa": 2, "sorte": 0.04}},
        {"nome": "Root sem Permissão", "nivel_min": 10, "skill_extra": "Privilege Escalation",
         "descricao": "Dobra o próximo dano e rouba bônus de defesa do inimigo.",
         "bonus": {"hp": 30, "mp": 25, "dano": 8, "defesa": 3, "sorte": 0.04}},
        {"nome": "Fantasma da Rede",   "nivel_min": 15, "skill_extra": "Ghost Protocol",
         "descricao": "Fica intocável por 1 turno e contra-ataca com força total.",
         "bonus": {"hp": 40, "mp": 32, "dano": 11, "defesa": 4, "sorte": 0.05}},
    ],
}

ITENS_BASE: Dict[str, int] = {
    "pocao_hp": 2, "pocao_mp": 1, "bomba": 1, "antidoto": 1, "escudo": 0,
}


class Personagem(Combatente):
    def __init__(self, nome: str, classe_base: str, sexo: str = "m"):
        if classe_base not in CLASSES_BASE:
            raise ValueError(f"Classe inválida: {classe_base}")

        dados = CLASSES_BASE[classe_base]
        super().__init__(
            nome=nome,
            hp_max=int(dados["hp"]),
            dano=int(dados["dano"]),
            defesa=int(dados["defesa"]),
            sorte=float(dados["sorte"]),
        )
        self.sexo = sexo  # 'm' ou 'f'
        self.classe_base = classe_base
        self.classe_atual = classe_base
        self.skill = dados["skill"]
        self.skill_extra: Optional[str] = None
        self.mp_max = int(dados["mp"])
        self.mp = self.mp_max

        self.level = 1
        self.xp = 0
        self.next_xp = 55
        self.ouro = 10
        self.stage = 0

        self.focus_turns = 0
        self.focus_bonus = 0
        self.regen_turns = 0
        self.regen_power = 0
        self.ghost_turns = 0
        self.counter_ready = False

        self.inventario: Dict[str, int] = dict(ITENS_BASE)

        # ── Flags de progressão ──────────────────────────────
        self.bsod_visto: bool = False        # viu a tela azul neste save
        self.ng_plus: bool = False           # está em modo NG+
        self.mundo_alterado: bool = False    # mundo pós-BSOD ativo
        self.encontro_index: int = 0         # progresso na campanha

    # ── Pronomes adaptativos ─────────────────────────────────
    @property
    def ele_ela(self) -> str:
        return "ela" if self.sexo == "f" else "ele"

    @property
    def seu_sua(self) -> str:
        return "sua" if self.sexo == "f" else "seu"

    @property
    def satisfeit(self) -> str:
        return "satisfeita" if self.sexo == "f" else "satisfeito"

    @property
    def entediad(self) -> str:
        return "entediada" if self.sexo == "f" else "entediado"

    @property
    def pronto_a(self) -> str:
        return "pronta" if self.sexo == "f" else "pronto"

    @staticmethod
    def escolher_classe_interativa() -> str:
        nomes = list(CLASSES_BASE.keys())
        print()
        for i, nome in enumerate(nomes, start=1):
            dados = CLASSES_BASE[nome]
            print(f"  {cor(f'[{i}]', CYAN)} {cor(nome, YELLOW)}")
            print(f"      {dados['descricao']}")
            print(f"      HP:{dados['hp']} ATK:{dados['dano']} DEF:{dados['defesa']} MP:{dados['mp']}")
            print()
        indice = menu_escolha("Escolha sua classe inicial:", nomes)
        return nomes[indice - 1]

    def mostrar_status(self) -> None:
        exibir_estado(self.nome, self.hp, self.hp_max, self.mp, self.mp_max,
                      self.level, self.xp, self.next_xp)
        skill_str = self.skill
        if self.skill_extra:
            skill_str += f" / {self.skill_extra}"
        print(f"  Classe: {cor(self.classe_atual, MAGENTA)} | Skill: {cor(skill_str, CYAN)} | Ouro: {cor(str(self.ouro), YELLOW)}")
        status = self.resumo_status()
        if status != "Sem efeitos ativos":
            print(f"  Status: {status}")
        resumo = self._resumo_inventario()
        if resumo:
            print(f"  {resumo}")
        if self.ng_plus:
            print(f"  {cor('[NG+]', MAGENTA)} Beyond the Kernel")

    def _resumo_inventario(self) -> str:
        nomes_itens = {
            "pocao_hp": "PçHP", "pocao_mp": "PçMP",
            "bomba": "Bomba", "antidoto": "Antídoto", "escudo": "Escudo",
        }
        partes = [f"{nomes_itens[k]}:{v}" for k, v in self.inventario.items() if v > 0 and k in nomes_itens]
        return "Itens: " + " | ".join(partes) if partes else ""

    def recuperar_mp(self, valor: int) -> int:
        mp_antes = self.mp
        self.mp = min(self.mp_max, self.mp + max(0, int(valor)))
        return self.mp - mp_antes

    def aplicar_efeitos_inicio_turno(self) -> List[str]:
        mensagens = super().aplicar_efeitos_inicio_turno()
        if self.regen_turns > 0:
            self.regen_turns -= 1
            curado = self.curar(self.regen_power)
            if curado > 0:
                mensagens.append(f"✨ {self.nome} regenera {curado} HP.")
            if self.regen_turns == 0:
                self.regen_power = 0
        if self.focus_turns > 0:
            self.focus_turns -= 1
            mensagens.append(f"🎯 {self.nome} mantém o foco.")
            if self.focus_turns == 0:
                self.focus_bonus = 0
        if self.ghost_turns > 0:
            self.ghost_turns -= 1
            mensagens.append(f"👻 {self.nome} ainda está no modo fantasma.")
        return mensagens

    def turno_está_bloqueado(self) -> bool:
        if self.stun_turns > 0:
            self.stun_turns -= 1
            texto_lento(f"💫 {self.nome} está atordoado e não pode agir.", 0.03)
            return True
        return False

    def ganhar_xp(self, quantidade: int) -> None:
        quantidade = max(0, int(quantidade))
        self.xp += quantidade
        texto_lento(f"⭐ +{quantidade} XP. ({self.xp}/{self.next_xp})", 0.03)
        while self.xp >= self.next_xp:
            self.xp -= self.next_xp
            self.level += 1
            texto_lento(f"\n{'='*50}", 0.01)
            texto_lento(f"🏅 {self.nome} subiu para o NÍVEL {self.level}!", 0.03)
            _audio.sfx("level_up")
            continuar("\n  ENTER para ver os ganhos...")
            self._subir_nivel()
            texto_lento(f"{'='*50}", 0.01)
            texto_lento(f"📊 XP restante: {self.xp}/{self.next_xp}", 0.03)

    def _subir_nivel(self) -> None:
        mult_ng = 1.4 if self.ng_plus else 1.0
        inc_hp  = int((16 + self.level * 2 + self.stage * 3) * mult_ng)
        inc_mp  = int((9  + self.level     + self.stage * 2) * mult_ng)
        inc_atk = int((2  + self.stage) * mult_ng)
        inc_def = 1
        self.hp_max += inc_hp
        self.mp_max += inc_mp
        self.dano   += inc_atk
        self.defesa += inc_def
        self.sorte   = min(0.65, self.sorte + 0.01)
        self.hp      = self.hp_max
        self.mp      = self.mp_max
        self.next_xp = int(55 + self.level * 20 + self.stage * 15)
        if self.ng_plus:
            self.next_xp = int(self.next_xp * 1.5)
        texto_lento(f"  📈 HP +{inc_hp} | MP +{inc_mp} | ATK +{inc_atk} | DEF +{inc_def}", 0.03)

    def pode_evoluir(self) -> bool:
        subs = SUBCLASSES.get(self.classe_base, [])
        if self.stage >= len(subs):
            return False
        return self.level >= subs[self.stage]["nivel_min"]

    def evoluir_classe(self) -> None:
        subs = SUBCLASSES.get(self.classe_base, [])
        if self.stage >= len(subs):
            texto_lento("Você já atingiu a evolução máxima desta classe.", 0.03)
            return
        if not self.pode_evoluir():
            prox = subs[self.stage]["nivel_min"]
            texto_lento(f"Você precisa ser nível {prox} para evoluir. (Atual: {self.level})", 0.03)
            return
        sub = subs[self.stage]
        self.stage        += 1
        self.classe_atual  = sub["nome"]
        self.skill_extra   = sub["skill_extra"]
        b = sub["bonus"]
        self.hp_max  += b["hp"]
        self.mp_max  += b["mp"]
        self.dano    += b["dano"]
        self.defesa  += b["defesa"]
        self.sorte    = min(0.80, self.sorte + b["sorte"])
        self.hp       = self.hp_max
        self.mp       = self.mp_max
        _audio.sfx("evolucao")
        texto_lento(f"\n✨ {self.nome} evoluiu para {cor(self.classe_atual, YELLOW)}!", 0.03)
        texto_lento(f"   Nova habilidade: {cor(self.skill_extra, CYAN)}", 0.03)
        texto_lento(f"   {sub['descricao']}", 0.03)
        texto_lento(f"   HP +{b['hp']} | MP +{b['mp']} | ATK +{b['dano']} | DEF +{b['defesa']}", 0.03)

    def adicionar_ouro(self, valor: int) -> None:
        self.ouro += max(0, int(valor))

    def adicionar_item(self, nome_item: str, quantidade: int = 1) -> None:
        self.inventario[nome_item] = self.inventario.get(nome_item, 0) + max(0, int(quantidade))

    def tem_item(self, nome_item: str) -> bool:
        return self.inventario.get(nome_item, 0) > 0

    def usar_item(self, nome_item: str, alvo: Optional["Combatente"] = None) -> str:
        alvo = alvo or self
        qtd = self.inventario.get(nome_item, 0)
        if qtd <= 0:
            return "Você não tem esse item."
        if nome_item == "bomba" and alvo is self:
            return "A bomba precisa de um alvo inimigo."
        if nome_item == "pocao_hp":
            self.inventario[nome_item] = qtd - 1
            curado = self.curar(40 + self.stage * 12 + self.level * 2)
            return f"🧪 {self.nome} recuperou {curado} HP."
        if nome_item == "pocao_mp":
            self.inventario[nome_item] = qtd - 1
            rec = self.recuperar_mp(35 + self.stage * 10)
            return f"🔮 {self.nome} recuperou {rec} MP."
        if nome_item == "bomba":
            self.inventario[nome_item] = qtd - 1
            dano = int(round((self.dano + self.stage * 4 + self.level * 2) * 1.4))
            alvo.receber_dano(dano, origem=self.nome)
            return f"💣 Bomba causou {dano} de dano em {alvo.nome}."
        if nome_item == "antidoto":
            self.inventario[nome_item] = qtd - 1
            self.burn_turns  = 0
            self.bleed_turns = 0
            curado = self.curar(20 + self.stage * 5)
            return f"🧴 Efeitos negativos removidos. +{curado} HP."
        if nome_item == "escudo":
            self.inventario[nome_item] = qtd - 1
            self.aplicar_guardia(2, 0.45)
            self.aplicar_defesa_extra(4 + self.stage * 2, 2)
            return f"🛡️  {self.nome} recebeu proteção temporária."
        return "Item desconhecido."

    def atacar(self, alvo: "Combatente") -> None:
        if self.turno_está_bloqueado():
            return
        base = self.dano + self.focus_bonus + self.rage_bonus
        chance_critico = min(0.50, 0.18 + self.sorte)
        texto_lento(f"{self.nome} parte para cima.", 0.03)
        if random.random() < chance_critico:
            dano = int(round(base * 2.0))
            texto_lento(f"⚡ CRÍTICO! {self.nome} causou {dano} de dano.", 0.03)
            _audio.sfx("critico")
        else:
            dano = int(round(base))
            _audio.sfx("ataque")
        alvo.receber_dano(dano, origem=self.nome)

    def meditar(self) -> None:
        ganho_mp = 20 + self.stage * 6
        ganho_hp = 10 + self.stage * 3
        self.recuperar_mp(ganho_mp)
        self.curar(ganho_hp)
        texto_lento(f"🧘 {self.nome} respirou fundo. +{ganho_hp} HP, +{ganho_mp} MP.", 0.03)

    def defender(self) -> None:
        self.aplicar_guardia(1, 0.45)
        self.aplicar_defesa_extra(3 + self.stage, 1)
        texto_lento(f"🛡️  {self.nome} entrou em posição defensiva.", 0.03)

    # ─────────────────────────────────────────────────────────
    #  SKILLS
    # ─────────────────────────────────────────────────────────
    _CUSTO_SKILL: Dict[str, int] = {
        "Bom Humor": 14, "Encontrar Bug": 26, "Fúria do Carcará": 22,
        "Frenesi": 20, "Cache Arcano": 24, "Selo de Patch": 18,
        "Corte Fantasma": 22, "Injeção de Caos": 20,
    }
    _CUSTO_SKILL_EXTRA: Dict[str, int] = {
        "Vínculo Etéreo": 18, "Sobrecarga Arcana": 28, "Singularidade": 40,
        "Stack Trace": 20, "Recursão Fatal": 30, "Refactoring Letal": 35,
        "Rugido Ancestral": 18, "Tempestade de Ferro": 28, "Colapso Total": 40,
        "Pulso Carmesim": 20, "Dança Sangrenta": 28, "Colheita Sombria": 32,
        "Pulso de Núcleo": 20, "Deploy Letal": 32, "Compilação Final": 0,
        "Barreira de Hotfix": 22, "Julgamento do Root": 30, "Permissão Divina": 40,
        "Sombra Afiada": 18, "Exploit Zero-Day": 28, "Null Pointer": 35,
        "SQL Injection": 20, "Privilege Escalation": 30, "Ghost Protocol": 35,
    }

    def usar_skill(self, alvo: "Combatente", usar_extra: bool = False) -> None:
        if self.turno_está_bloqueado():
            return
        if usar_extra and self.skill_extra:
            skill_nome = self.skill_extra
            custo = self._CUSTO_SKILL_EXTRA.get(skill_nome, 25)
        else:
            skill_nome = self.skill
            custo = self._CUSTO_SKILL.get(skill_nome, 20)
        if self.mp < custo:
            texto_lento(f"Mana insuficiente para {skill_nome}. ({self.mp}/{custo})", 0.03)
            return
        self.mp -= custo
        texto_lento(f"✨ {self.nome} ativou {cor(skill_nome, CYAN)}!", 0.03)
        _audio.sfx("magia")
        self._executar_skill(alvo, skill_nome)

    def _executar_skill(self, alvo: "Combatente", skill: str) -> None:
        s = skill
        if s == "Bom Humor":
            cura = 22 + self.stage * 8 + self.level * 2
            self.focus_bonus = 6 + self.stage * 3
            self.focus_turns = 3
            self.regen_power = 8 + self.stage * 2
            self.regen_turns = 2
            self.curar(cura)
            dano = int(round((self.dano + self.focus_bonus) * 1.1))
            alvo.receber_dano(dano, origem=self.nome)
            texto_lento(f"🌟 Humor bom, ataque melhor. Curou {cura} HP e causou {dano} de dano.", 0.03)
        elif s == "Encontrar Bug":
            hits = 3 + self.stage
            for i in range(hits):
                mult = 1.0 + random.uniform(0.20, 0.45) + self.stage * 0.04
                dano = int(round((self.dano + self.focus_bonus) * mult))
                alvo.receber_dano(dano, origem=self.nome)
                texto_lento(f"🐛 Bug {i+1}/{hits}: {dano} de dano.", 0.03)
                if not alvo.esta_vivo(): break
            if random.random() < 0.40 + self.stage * 0.04 and alvo.esta_vivo():
                alvo.aplicar_defesa_extra(-2, 2)
                texto_lento(f"📉 Defesa de {alvo.nome} foi corrompida.", 0.03)
            self.recuperar_mp(5)
        elif s == "Fúria do Carcará":
            dano = int(round((self.dano + self.rage_bonus) * (1.8 + self.stage * 0.14)))
            alvo.receber_dano(dano, origem=self.nome)
            self.aplicar_furia(6 + self.stage * 3, 3)
            self.aplicar_defesa_extra(-(self.defesa // 3), 2)
            texto_lento(f"🦅 Fúria solta. Dano e raiva ao máximo.", 0.03)
        elif s == "Frenesi":
            dano = int(round((self.dano + self.focus_bonus) * (1.55 + self.stage * 0.12)))
            alvo.receber_dano(dano, origem=self.nome)
            cura = max(6, int(round(dano * 0.38)))
            self.curar(cura)
            alvo.aplicar_sangramento(4 + self.stage * 2, 2)
            texto_lento(f"🩸 Frenesi encaixou. Curou {cura} HP.", 0.03)
            _audio.sfx("cura")
        elif s == "Cache Arcano":
            self.focus_bonus = 5 + self.stage * 4
            self.focus_turns = 3
            dano = int(round((self.dano + self.focus_bonus) * 1.45))
            alvo.receber_dano(dano, origem=self.nome)
            if random.random() < 0.45:
                alvo.aplicar_defesa_extra(-1, 2)
                texto_lento(f"💾 Cache de {alvo.nome} corrompido.", 0.03)
        elif s == "Selo de Patch":
            dano = int(round((self.dano + self.defesa) * 1.3))
            alvo.receber_dano(dano, origem=self.nome)
            self.curar(14 + self.stage * 5)
            self.defesa += 1
            texto_lento(f"🛡️  Blindagem reforçada. Dano: {dano}.", 0.03)
        elif s == "Corte Fantasma":
            hits = 2 + self.stage
            for i in range(hits):
                dano = int(round((self.dano + self.focus_bonus) * (0.85 + 0.14 * self.stage)))
                alvo.receber_dano(dano, origem=self.nome)
                texto_lento(f"🗡️  Corte {i+1}/{hits}: {dano}.", 0.03)
                if not alvo.esta_vivo(): break
            if random.random() < 0.30 + self.sorte * 0.5:
                alvo.stun_turns = max(alvo.stun_turns, 1)
                texto_lento(f"💨 {alvo.nome} perdeu o ritmo.", 0.03)
        elif s == "Injeção de Caos":
            dano = int(round((self.dano + self.focus_bonus) * 1.35))
            alvo.receber_dano(dano, origem=self.nome)
            ef = random.choice(["burn", "bleed", "vuln", "stun"])
            if ef == "burn":
                alvo.aplicar_queimadura(4 + self.stage, 2)
                texto_lento("🔥 Caos injeta fogo.", 0.03)
            elif ef == "bleed":
                alvo.aplicar_sangramento(4 + self.stage, 2)
                texto_lento("🩸 Caos injeta sangramento.", 0.03)
            elif ef == "vuln":
                alvo.aplicar_vulnerabilidade(1.14, 2)
                texto_lento("📉 Caos injeta vulnerabilidade.", 0.03)
            elif ef == "stun":
                if random.random() < 0.35:
                    alvo.stun_turns = max(alvo.stun_turns, 1)
                    texto_lento(f"💫 Caos atordoou {alvo.nome}.", 0.03)
        elif s == "Vínculo Etéreo":
            self.regen_power = 14 + self.stage * 4
            self.regen_turns = 4
            dano = int(round(self.dano * 1.3))
            alvo.receber_dano(dano, origem=self.nome)
            texto_lento("🌐 Vínculo ativo. Regeneração por 4 turnos.", 0.03)
        elif s == "Sobrecarga Arcana":
            for _ in range(2):
                dano = int(round(self.dano * (1.4 + random.uniform(0, 0.3))))
                alvo.receber_dano(dano, origem=self.nome)
            texto_lento("⚡ Dois feitiços simultâneos.", 0.03)
        elif s == "Singularidade":
            dano = int(round((self.dano + self.mp) * 1.1))
            self.mp = max(0, self.mp - 20)
            alvo.receber_dano(dano, origem=self.nome)
            texto_lento(f"🌀 Singularidade consumiu mana: {dano} de dano.", 0.03)
        elif s == "Stack Trace":
            alvo.aplicar_vulnerabilidade(1.20, 3)
            dano = int(round(self.dano * 1.4))
            alvo.receber_dano(dano, origem=self.nome)
            texto_lento("🔍 Stack trace analisado. Vulnerabilidade aplicada.", 0.03)
        elif s == "Recursão Fatal":
            hits = min(6, self.mp // 8)
            for i in range(max(1, hits)):
                dano = int(round(self.dano * 0.7))
                alvo.receber_dano(dano, origem=self.nome)
                self.mp = max(0, self.mp - 8)
                if not alvo.esta_vivo(): break
            texto_lento(f"🔁 Recursão: {max(1, hits)} golpes.", 0.03)
        elif s == "Refactoring Letal":
            self.hp = self.hp_max
            self.mp = self.mp_max
            dano = int(round(self.dano * 2.0))
            alvo.receber_dano(dano, origem=self.nome)
            texto_lento(f"♻️  Código refatorado. HP e MP cheios. Dano: {dano}.", 0.03)
        elif s == "Rugido Ancestral":
            alvo.aplicar_defesa_extra(-4, 3)
            alvo.aplicar_vulnerabilidade(1.15, 2)
            texto_lento(f"🦁 Rugido ancestral. {alvo.nome} enfraquecido.", 0.03)
        elif s == "Tempestade de Ferro":
            self.aplicar_furia(8 + self.stage * 2, 2)
            for i in range(3):
                dano = int(round((self.dano + self.rage_bonus) * 0.8))
                alvo.receber_dano(dano, origem=self.nome)
                texto_lento(f"⚔️  Golpe {i+1}/3: {dano}.", 0.03)
                if not alvo.esta_vivo(): break
        elif s == "Colapso Total":
            def_salva = alvo.defesa
            alvo.defesa = alvo.defesa // 2
            dano = int(round(self.dano * 2.2))
            alvo.receber_dano(dano, origem=self.nome)
            alvo.defesa = def_salva
            texto_lento(f"💥 Defesa ignorada pela metade. {dano} de dano puro.", 0.03)
        elif s == "Pulso Carmesim":
            alvo.aplicar_sangramento(7 + self.stage * 2, 4)
            dano = int(round(self.dano * 1.3))
            alvo.receber_dano(dano, origem=self.nome)
            self.regen_power = 6 + self.stage
            self.regen_turns = 3
            texto_lento("🩸 Sangramento profundo + regen passiva.", 0.03)
        elif s == "Dança Sangrenta":
            for i in range(2):
                mult = 1.2 if i == 0 else 1.6
                dano = int(round(self.dano * mult))
                alvo.receber_dano(dano, origem=self.nome)
                texto_lento(f"💃 Passo {i+1}: {dano}.", 0.03)
                if not alvo.esta_vivo(): break
        elif s == "Colheita Sombria":
            pct = alvo.hp / alvo.hp_max if alvo.hp_max else 1
            mult = 1.2 + (1.0 - pct) * 1.5
            dano = int(round(self.dano * mult))
            alvo.receber_dano(dano, origem=self.nome)
            texto_lento(f"☠️  Quanto menos HP o inimigo tem, mais dói. {dano} de dano.", 0.03)
        elif s == "Pulso de Núcleo":
            bonus = self.mp // 5
            dano = int(round((self.dano + bonus) * 1.3))
            alvo.receber_dano(dano, origem=self.nome)
            texto_lento(f"💡 Pulso de núcleo. {dano}.", 0.03)
        elif s == "Deploy Letal":
            dano = int(round((self.dano + self.focus_bonus * 3) * 1.4))
            alvo.receber_dano(dano, origem=self.nome)
            self.focus_bonus = 0
            self.focus_turns = 0
            texto_lento(f"🚀 Deploy liberado. {dano} de dano.", 0.03)
        elif s == "Compilação Final":
            dano = int(round(self.mp * 1.5))
            self.mp = 0
            alvo.receber_dano(dano, origem=self.nome)
            texto_lento(f"💾 Toda a mana virou dano. {dano}. MP zerado.", 0.03)
        elif s == "Barreira de Hotfix":
            self.aplicar_guardia(3, 0.55)
            self.counter_ready = True
            texto_lento("🛡️  Barreira ativa por 3 turnos. Próximo ataque será refletido.", 0.03)
        elif s == "Julgamento do Root":
            def_salva = alvo.defesa
            alvo.defesa = 0
            dano = int(round(self.dano * 1.7))
            alvo.receber_dano(dano, origem=self.nome)
            alvo.defesa = def_salva
            texto_lento(f"⚖️  Julgamento ignora toda defesa. {dano} de dano sagrado.", 0.03)
        elif s == "Permissão Divina":
            self.hp = self.hp_max
            self.mp = self.mp_max
            self.aplicar_guardia(3, 0.50)
            dano = int(round(self.dano * 1.8))
            alvo.receber_dano(dano, origem=self.nome)
            texto_lento(f"✨ Permissão divina: cura total, escudo 3T e {dano} de dano.", 0.03)
        elif s == "Sombra Afiada":
            sorte_salva = self.sorte
            self.sorte = min(0.85, self.sorte + 0.25)
            dano = int(round(self.dano * 1.5))
            alvo.receber_dano(dano, origem=self.nome)
            self.sorte = sorte_salva
            texto_lento("🌑 Ataque nas sombras. Alta chance de crítico.", 0.03)
        elif s == "Exploit Zero-Day":
            alvo.aplicar_vulnerabilidade(1.20, 2)
            def_salva = alvo.defesa
            alvo.defesa = alvo.defesa // 2
            dano = int(round(self.dano * 1.6))
            alvo.receber_dano(dano, origem=self.nome)
            alvo.defesa = def_salva
            texto_lento(f"🕳️  Zero-day explorado. {dano} de dano.", 0.03)
        elif s == "Null Pointer":
            if alvo.hp <= alvo.hp_max * 0.20:
                alvo.hp = 0
                texto_lento(f"☠️  NULL POINTER EXCEPTION. {alvo.nome} foi eliminado.", 0.03)
            else:
                dano = int(round(self.dano * 1.8))
                alvo.receber_dano(dano, origem=self.nome)
                texto_lento(f"❌ Alvo não está baixo o suficiente. Dano padrão: {dano}.", 0.03)
        elif s == "SQL Injection":
            alvo.aplicar_vulnerabilidade(1.15, 2)
            alvo.aplicar_sangramento(3 + self.stage, 2)
            dano = int(round(self.dano * 1.35))
            alvo.receber_dano(dano, origem=self.nome)
            texto_lento("💉 Injeção concluída. Dois efeitos aplicados.", 0.03)
        elif s == "Privilege Escalation":
            self.dano += 4
            self.aplicar_furia(5 + self.stage, 3)
            dano = int(round(self.dano * 1.5))
            alvo.receber_dano(dano, origem=self.nome)
            texto_lento(f"⬆️  Privilégio escalado. ATK permanente +4.", 0.03)
        elif s == "Ghost Protocol":
            self.ghost_turns = 2
            dano = int(round(self.dano * 1.9))
            alvo.receber_dano(dano, origem=self.nome)
            texto_lento("👻 Modo fantasma ativado. 2 turnos de esquiva + contra-ataque.", 0.03)
        else:
            texto_lento(f"✨ {self.nome} usou {skill}.", 0.03)
            dano = int(round(self.dano * 1.2))
            alvo.receber_dano(dano, origem=self.nome)

    def salvar(self, caminho) -> None:
        path = Path(caminho)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "nome": self.nome, "sexo": self.sexo,
            "classe_base": self.classe_base, "classe_atual": self.classe_atual,
            "skill": self.skill, "skill_extra": self.skill_extra,
            "hp_max": self.hp_max, "hp": self.hp,
            "mp_max": self.mp_max, "mp": self.mp,
            "dano": self.dano, "defesa": self.defesa, "sorte": self.sorte,
            "level": self.level, "xp": self.xp, "next_xp": self.next_xp,
            "ouro": self.ouro, "stage": self.stage,
            "focus_turns": self.focus_turns, "focus_bonus": self.focus_bonus,
            "regen_turns": self.regen_turns, "regen_power": self.regen_power,
            "ghost_turns": self.ghost_turns, "counter_ready": self.counter_ready,
            "guard_turns": self.guard_turns, "guard_reduction": self.guard_reduction,
            "rage_turns": self.rage_turns, "rage_bonus": self.rage_bonus,
            "bleed_turns": self.bleed_turns, "bleed_damage": self.bleed_damage,
            "burn_turns": self.burn_turns, "burn_damage": self.burn_damage,
            "vulnerable_turns": self.vulnerable_turns,
            "vulnerable_multiplier": self.vulnerable_multiplier,
            "stun_turns": self.stun_turns,
            "defesa_bonus": self.defesa_bonus, "defesa_bonus_turns": self.defesa_bonus_turns,
            "inventario": self.inventario,
            "bsod_visto": self.bsod_visto,
            "ng_plus": self.ng_plus,
            "mundo_alterado": self.mundo_alterado,
            "encontro_index": self.encontro_index,
        }
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def carregar(cls, caminho) -> "Personagem":
        path = Path(caminho)
        d = json.loads(path.read_text(encoding="utf-8"))
        p = cls(d["nome"], d["classe_base"], d.get("sexo", "m"))
        p.classe_atual  = d.get("classe_atual", p.classe_atual)
        p.skill         = d.get("skill", p.skill)
        p.skill_extra   = d.get("skill_extra")
        p.hp_max        = int(d.get("hp_max", p.hp_max))
        p.hp            = min(p.hp_max, int(d.get("hp", p.hp_max)))
        p.mp_max        = int(d.get("mp_max", p.mp_max))
        p.mp            = min(p.mp_max, int(d.get("mp", p.mp_max)))
        p.dano          = int(d.get("dano", p.dano))
        p.defesa        = int(d.get("defesa", p.defesa))
        p.sorte         = float(d.get("sorte", p.sorte))
        p.level         = int(d.get("level", p.level))
        p.xp            = int(d.get("xp", p.xp))
        p.next_xp       = int(d.get("next_xp", p.next_xp))
        p.ouro          = int(d.get("ouro", p.ouro))
        p.stage         = int(d.get("stage", p.stage))
        p.focus_turns   = int(d.get("focus_turns", 0))
        p.focus_bonus   = int(d.get("focus_bonus", 0))
        p.regen_turns   = int(d.get("regen_turns", 0))
        p.regen_power   = int(d.get("regen_power", 0))
        p.ghost_turns   = int(d.get("ghost_turns", 0))
        p.counter_ready = bool(d.get("counter_ready", False))
        p.guard_turns   = int(d.get("guard_turns", 0))
        p.guard_reduction = float(d.get("guard_reduction", 0.35))
        p.rage_turns    = int(d.get("rage_turns", 0))
        p.rage_bonus    = int(d.get("rage_bonus", 0))
        p.bleed_turns   = int(d.get("bleed_turns", 0))
        p.bleed_damage  = int(d.get("bleed_damage", 0))
        p.burn_turns    = int(d.get("burn_turns", 0))
        p.burn_damage   = int(d.get("burn_damage", 0))
        p.vulnerable_turns = int(d.get("vulnerable_turns", 0))
        p.vulnerable_multiplier = float(d.get("vulnerable_multiplier", 1.12))
        p.stun_turns    = int(d.get("stun_turns", 0))
        p.defesa_bonus  = int(d.get("defesa_bonus", 0))
        p.defesa_bonus_turns = int(d.get("defesa_bonus_turns", 0))
        inv = d.get("inventario", {})
        p.inventario = {str(k): int(v) for k, v in inv.items()} if isinstance(inv, dict) else dict(ITENS_BASE)
        for item, qtd in ITENS_BASE.items():
            p.inventario.setdefault(item, qtd)
        p.bsod_visto     = bool(d.get("bsod_visto", False))
        p.ng_plus        = bool(d.get("ng_plus", False))
        p.mundo_alterado = bool(d.get("mundo_alterado", False))
        p.encontro_index = int(d.get("encontro_index", 0))
        return p

    def resumo_completo(self) -> str:
        skill_str = self.skill + (f" / {self.skill_extra}" if self.skill_extra else "")
        ng = " [NG+]" if self.ng_plus else ""
        return (
            f"{self.nome} | {self.classe_atual}{ng} | Lv {self.level} | "
            f"HP {self.hp}/{self.hp_max} | MP {self.mp}/{self.mp_max} | "
            f"ATK {self.dano} | DEF {self.defesa} | Skills: {skill_str}"
        )
