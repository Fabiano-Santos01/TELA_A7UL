import random
import logging

_log = logging.getLogger("combate")
from pathlib import Path
from typing import List, Dict, Any, Optional

from src.utils import (
    limpar_tela, banner, texto_lento, menu_escolha, cor,
    GREEN, YELLOW, RED, CYAN, MAGENTA, BOLD, DIM, GRAY, WHITE, ORANGE,
    pausar, progress_bar, continuar, separador,
)
from src.player import Personagem
from src.enemy import Mob, Boss
from src.base import LogBatalha
from src.audio import audio as _audio


# ─────────────────────────────────────────────────────────────
#  NARRATIVAS DE CLIMA
# ─────────────────────────────────────────────────────────────
_CLIMA_MOB = [
    "O ar pesa. Ele procura uma brecha.",
    "O silêncio antes do golpe já dói mais que o golpe.",
    "A criatura aprende rápido demais.",
    "Não sobra espaço pra respirar aqui.",
    "Você sente os olhos dele antes de ver o movimento.",
]
_CLIMA_BOSS = [
    "O boss não tem pressa. Isso é o pior sinal.",
    "Cada segundo aqui custa mais do que parece.",
    "O chefe bagunça seu ritmo de propósito.",
    "O chão treme levemente. Ele está ficando sério.",
    "O ar ao redor do boss vibra como sinal de interferência.",
]
_CLIMA_NG = [
    "Aqui as regras antigas não se aplicam mais.",
    "Você sente que o sistema está processando você também.",
    "O inimigo te olha como se soubesse de onde você veio.",
    "Cada golpe parece mais pesado que o anterior. É o preço do NG+.",
    "A realidade ao redor vacila levemente. É normal aqui.",
]

# ─────────────────────────────────────────────────────────────
#  SISTEMA DE SAVE COM 3 SLOTS
# ─────────────────────────────────────────────────────────────
SAVE_DIR = Path(__file__).parent.parent / "saves"


def _slot_path(slot: int) -> Path:
    return SAVE_DIR / f"slot_{slot}.json"


def salvar_em_slot(jogador: Personagem, slot: int, silencioso: bool = False) -> None:
    SAVE_DIR.mkdir(exist_ok=True)
    jogador.salvar(_slot_path(slot))
    if not silencioso:
        texto_lento(f"  💾 Partida salva no Slot {slot}.", 0.03)
        _audio.sfx("save")


def carregar_de_slot(slot: int) -> Optional[Personagem]:
    p = _slot_path(slot)
    if not p.exists():
        return None
    try:
        jog = Personagem.carregar(p)
        _audio.sfx("load")
        return jog
    except Exception as e:
        _log.warning("Falha ao carregar slot %d: %s", slot, e)
        return None


def deletar_slot(slot: int) -> None:
    p = _slot_path(slot)
    if p.exists():
        p.unlink()


def resumo_slot(slot: int) -> str:
    p = _slot_path(slot)
    if not p.exists():
        return cor("[vazio]", GRAY)
    try:
        jog = Personagem.carregar(p)
        ng_str = cor(" [NG+]", MAGENTA) if jog.ng_plus else ""
        return (
            f"{cor(jog.nome, CYAN)} | {cor(jog.classe_atual, MAGENTA)} | "
            f"Lv {cor(str(jog.level), YELLOW)} | "
            f"HP {jog.hp}/{jog.hp_max}{ng_str}"
        )
    except Exception:
        return cor("[corrompido]", RED)


def tela_gerenciar_saves(slot_atual: Optional[int] = None) -> Optional[int]:
    while True:
        limpar_tela()
        banner("GERENCIAR SAVES", "3 slots disponíveis", CYAN)
        print()
        for i in range(1, 4):
            marca = cor(" ◄ atual", YELLOW) if slot_atual == i else ""
            print(f"  {cor(f'Slot {i}', CYAN)}: {resumo_slot(i)}{marca}")
        print()
        opcoes = [
            "Salvar no Slot 1", "Salvar no Slot 2", "Salvar no Slot 3",
            "Deletar Slot 1",   "Deletar Slot 2",   "Deletar Slot 3",
            "Voltar",
        ]
        escolha = menu_escolha("Escolha uma ação:", opcoes)
        if escolha <= 3:
            return escolha
        elif escolha <= 6:
            slot = escolha - 3
            confirm = input(cor(f"  Deletar Slot {slot}? Isso é permanente. [s/n]: ", RED)).strip().lower()
            if confirm in {"s", "sim"}:
                deletar_slot(slot)
                texto_lento(f"  🗑️  Slot {slot} deletado.", 0.03)
                pausar(0.8)
        else:
            return None


# ─────────────────────────────────────────────────────────────
#  CLASSE PRINCIPAL DE COMBATE
# ─────────────────────────────────────────────────────────────
class Combate:
    def __init__(
        self,
        jogador: Personagem,
        encontros: List[Dict[str, Any]],
        slot_ativo: int = 1,
        ng_plus: bool = False,
    ):
        self.jogador      = jogador
        self.encontros    = encontros
        self.turno        = 1
        self.slot_ativo   = slot_ativo
        self.ng_plus      = ng_plus
        self.npcs_disparados: set = set()
        self._bsod_disparado_nesta_sessao = False

    # ── Save ─────────────────────────────────────────────────
    def autosave(self) -> None:
        try:
            salvar_em_slot(self.jogador, self.slot_ativo, silencioso=True)
        except Exception as e:
            _log.warning("Falha no autosave (slot %d): %s", self.slot_ativo, e)

    def salvar_manual(self) -> None:
        slot = tela_gerenciar_saves(self.slot_ativo)
        if slot:
            salvar_em_slot(self.jogador, slot)
            self.slot_ativo = slot
            continuar()

    # ── Display ──────────────────────────────────────────────
    def _barra(self, atual: int, maximo: int, larg: int = 18) -> str:
        return progress_bar(int(max(0, atual)), int(max(1, maximo)), larg)

    def _tela_estado(self, inimigo: Any) -> None:
        limpar_tela()
        titulo = "BEYOND THE KERNEL" if self.ng_plus else "TELA AZUL.py"
        subtitulo = "NG+ — Além do sistema" if self.ng_plus else "Back-end, caos e persistência"
        cor_banner = MAGENTA if self.ng_plus else CYAN
        banner(titulo, subtitulo, cor_banner)
        print()
        print(cor("  ╔═ JOGADOR ══════════════════════════════════╗", CYAN))
        self.jogador.mostrar_status()
        print(cor("  ╚════════════════════════════════════════════╝", CYAN))
        print()
        print(cor("  ╔═ INIMIGO ══════════════════════════════════╗", MAGENTA))
        if hasattr(inimigo, "hp_max"):
            tipo_cor = RED if isinstance(inimigo, Boss) else YELLOW
            print(
                f"  {cor(inimigo.nome, tipo_cor)} | "
                f"HP {self._barra(inimigo.hp, inimigo.hp_max)} "
                f"{cor(f'{inimigo.hp}/{inimigo.hp_max}', WHITE)} | "
                f"ATK {cor(str(inimigo.dano), RED)} | "
                f"DEF {cor(str(inimigo.defesa), YELLOW)}"
            )
            if hasattr(inimigo, "resumo_status"):
                st = inimigo.resumo_status()
                if st != "Sem efeitos ativos":
                    print(f"  Status: {st}")
            if isinstance(inimigo, Boss):
                print(f"  Skill: {cor(inimigo.skill, MAGENTA)}")
        print(cor("  ╚════════════════════════════════════════════╝", MAGENTA))
        print()
        print(cor(f"  TURNO {self.turno}", YELLOW))
        separador()

    def _clima(self, inimigo: Any) -> None:
        vida = inimigo.hp / inimigo.hp_max if getattr(inimigo, "hp_max", 1) else 1
        if self.ng_plus:
            pool = list(_CLIMA_NG)
        else:
            pool = list(_CLIMA_BOSS if isinstance(inimigo, Boss) else _CLIMA_MOB)
        if vida < 0.35:
            pool += (
                ["O boss está com raiva real agora.", "Algo mudou no olhar dele."]
                if isinstance(inimigo, Boss)
                else ["Mesmo ferido, ainda quer morder.", "Ele vacila, mas não cede."]
            )
        if random.random() < 0.50:
            texto_lento(f"  {random.choice(pool)}", 0.03)

    # ── Intro / Recompensa ───────────────────────────────────
    def _intro_batalha(self, inimigo: Any) -> None:
        print()
        if isinstance(inimigo, Boss):
            _audio.sfx("boss_entra")
            nome_trilha = "boss_final" if self.ng_plus and inimigo.nome == "O VAZIO" else "boss"
            _audio.tocar_musica(nome_trilha)
        else:
            _audio.tocar_musica("ng_plus" if self.ng_plus else "combate")

        texto_lento(f"⚔️  {self.jogador.nome} cruzou com {cor(inimigo.nome, YELLOW)}.", 0.03)
        if hasattr(inimigo, "frase_entrada"):
            texto_lento(f"   {inimigo.frase_entrada()}", 0.03)
        if isinstance(inimigo, Boss):
            texto_lento(f"   👁️  Boss detectado. Skill: {cor(inimigo.skill, MAGENTA)}", 0.03)
        continuar("\n  [ ENTER para iniciar a batalha... ]")

    def _mostrar_recompensa(self, inimigo: Any) -> None:
        xp   = getattr(inimigo, "xp",   0)
        ouro = getattr(inimigo, "ouro", 0)
        self.jogador.adicionar_ouro(ouro)
        texto_lento(f"  💰 +{ouro} ouro.", 0.03)
        _audio.sfx("ouro")
        self.jogador.ganhar_xp(xp)

        drop = random.random()
        multiplicador = 1.3 if self.ng_plus else 1.0
        if drop < 0.22 * multiplicador:
            self.jogador.adicionar_item("pocao_hp", 1)
            texto_lento("  🧪 Poção HP encontrada.", 0.03)
        elif drop < 0.38 * multiplicador:
            self.jogador.adicionar_item("pocao_mp", 1)
            texto_lento("  🔮 Poção MP encontrada.", 0.03)
        elif drop < 0.46 * multiplicador:
            self.jogador.adicionar_item("bomba", 1)
            texto_lento("  💣 Bomba encontrada.", 0.03)
        elif drop < 0.52 * multiplicador:
            self.jogador.adicionar_item("antidoto", 1)
            texto_lento("  🧴 Antídoto encontrado.", 0.03)

        self.autosave()
        continuar()

    # ── Item em batalha ──────────────────────────────────────
    def _usar_item(self, inimigo: Any) -> None:
        limpar_tela()
        banner("INVENTÁRIO", "Escolha um item")
        _audio.sfx("inventario")
        itens = [
            ("Poção HP",  "pocao_hp"),
            ("Poção MP",  "pocao_mp"),
            ("Bomba",     "bomba"),
            ("Antídoto",  "antidoto"),
            ("Escudo",    "escudo"),
        ]
        for i, (nome_item, chave) in enumerate(itens, start=1):
            qtd = self.jogador.inventario.get(chave, 0)
            cor_qtd = GREEN if qtd > 0 else GRAY
            print(f"  {cor(f'[{i}]', CYAN)} {nome_item:18s} {cor(f'x{qtd}', cor_qtd)}")
        print(f"  {cor('[6]', GRAY)} Voltar")

        escolha = input(cor("\n  Escolha: ", YELLOW)).strip()
        if escolha == "6" or not escolha.isdigit() or not (1 <= int(escolha) <= 5):
            return

        idx = int(escolha) - 1
        _, chave = itens[idx]
        msg = self.jogador.usar_item(chave, inimigo if chave == "bomba" else None)
        texto_lento(f"  {msg}", 0.03)
        if "HP" in msg or "curou" in msg.lower():
            _audio.sfx("cura")
        self.autosave()
        continuar()

    # ── Campamento ───────────────────────────────────────────
    def _campamento(self) -> None:
        limpar_tela()
        banner("CAMPAMENTO RÁPIDO", "Respiro antes da próxima briga")
        texto_lento(
            "  Você encontra um canto protegido. "
            "Tempo suficiente para recuperar o fôlego.",
            0.03,
        )
        mult = 1.5 if self.ng_plus else 1.0
        rec_hp = self.jogador.curar(int((25 + self.jogador.level * 3) * mult))
        rec_mp = self.jogador.recuperar_mp(int((18 + self.jogador.level * 2) * mult))
        if random.random() < 0.50:
            self.jogador.adicionar_item("pocao_hp", 1)
            texto_lento("  Uma Poção HP estava guardada no canto.", 0.03)
        texto_lento(f"  +{rec_hp} HP | +{rec_mp} MP", 0.03)
        self.autosave()
        continuar()

    # ── NPCs de rota ─────────────────────────────────────────
    _NPC_EVENTOS = {
        2:  ("Glitch",       "Um sujeito com metade do rosto pixelado aparece no seu caminho.",
              [("Aceitar a dica de combate", "xp"), ("Pedir MP extra", "mp"), ("Ignorar", "nada")]),
        5:  ("Mara",         "Ela carrega frascos azuis e um sorriso que não inspira confiança total.",
              [("Comprar saúde", "hp"), ("Comprar foco arcano", "mp"), ("Negociar por poder", "atk")]),
        8:  ("Monge do Git", "Sentado sobre hardware morto, ele te olha como quem já sabe o próximo erro.",
              [("Aceitar disciplina", "def"), ("Pedir bênção de sorte", "sorte"), ("Sair sem parar", "nada")]),
        11: ("Guardiã Flux",  "Ela avisa que o núcleo não perdoa distração.",
              [("Cura completa", "cura"), ("Treino de ATK", "atk"), ("Info sobre o próximo boss", "xp")]),
        14: ("Oráculo Void",  "A voz dela soa como aviso e cobrança ao mesmo tempo.",
              [("Receber poder final", "final"), ("Pedir proteção", "def"), ("Seguir sem parar", "nada")]),
    }

    _NPC_EVENTOS_NG = {
        20: ("Glitch — Versão 2", "Ele está diferente. Mais sólido. Como se a tela azul o tivesse atualizado também.",
             [("Aceitar upgrade especial", "ng_atk"), ("Pedir cura total", "cura"), ("Ignorar", "nada")]),
        25: ("Mara Reescrita", "Ela te olha por um instante antes de falar. \"Você voltou. Eu sabia que voltaria.\"",
             [("Aceitar o kit de sobrevivência", "ng_kit"), ("Pedir boost de defesa", "ng_def"), ("Seguir", "nada")]),
    }

    def _verificar_npcs(self) -> None:
        tabela = self._NPC_EVENTOS_NG if self.ng_plus else self._NPC_EVENTOS
        ma = self.jogador.mundo_alterado

        for nivel, (nome, texto_base, opcoes) in tabela.items():
            if self.jogador.level >= nivel and nivel not in self.npcs_disparados:
                self.npcs_disparados.add(nivel)
                limpar_tela()
                banner(f"ENCONTRO — {nome}")

                if ma and not self.ng_plus:
                    # Diálogos alterados pós-BSOD
                    alterados = {
                        "Glitch": "Glitch te olha diferente. \"Você foi além. Eu vi nos logs.\"",
                        "Mara": "Mara não finge normalidade desta vez. \"Tome. Você vai precisar mais do que eu esperava.\"",
                        "Monge do Git": "O Monge não está no lugar habitual. Aparece de outro ângulo. \"O sistema te reconhece agora.\"",
                        "Guardiã Flux": "Flux não avisa mais. Simplesmente entrega o que você precisa.",
                        "Oráculo Void": "O Oráculo está calado. Depois de um momento: \"Você já sabe o que precisa fazer.\"",
                    }
                    dialogo = alterados.get(nome, texto_base)
                else:
                    dialogo = texto_base

                texto_lento(f"  {dialogo}", 0.03)
                print()
                escolha = menu_escolha("O que você faz?", [o[0] for o in opcoes])
                acao = opcoes[escolha - 1][1]
                self._aplicar_acao_npc(acao)
                self.autosave()
                continuar()

    def _aplicar_acao_npc(self, acao: str) -> None:
        j = self.jogador
        if acao == "xp":
            j.ganhar_xp(25)
            j.adicionar_ouro(10)
            texto_lento("  📚 Você aprendeu algo que vai fazer diferença.", 0.03)
        elif acao == "mp":
            r = j.recuperar_mp(30)
            texto_lento(f"  🔮 +{r} MP.", 0.03)
        elif acao == "hp":
            c = j.curar(30)
            j.adicionar_ouro(15)
            texto_lento(f"  🧪 +{c} HP.", 0.03)
        elif acao == "atk":
            j.dano += 3
            texto_lento(f"  ⚔️  ATK +3 permanente. Novo ATK: {j.dano}.", 0.03)
        elif acao == "def":
            j.defesa += 2
            texto_lento(f"  🛡️  DEF +2 permanente. Nova DEF: {j.defesa}.", 0.03)
        elif acao == "sorte":
            j.sorte = min(0.75, j.sorte + 0.03)
            texto_lento(f"  🍀 Sorte +0.03.", 0.03)
        elif acao == "cura":
            j.hp = j.hp_max
            j.mp = j.mp_max
            texto_lento("  ✨ Cura total. HP e MP no máximo.", 0.03)
        elif acao == "final":
            j.hp_max  += 30
            j.mp_max  += 30
            j.dano    += 6
            j.defesa  += 3
            j.sorte    = min(0.80, j.sorte + 0.04)
            j.hp       = j.hp_max
            j.mp       = j.mp_max
            texto_lento("  🌌 Poder final recebido.", 0.03)
        elif acao == "ng_atk":
            j.dano   += 8
            j.hp_max += 30
            j.hp      = j.hp_max
            texto_lento("  ⚡ Upgrade NG+: ATK +8 | HP máx +30.", 0.03)
        elif acao == "ng_def":
            j.defesa += 6
            j.hp_max += 40
            j.hp      = j.hp_max
            texto_lento("  🛡️  Upgrade NG+: DEF +6 | HP máx +40.", 0.03)
        elif acao == "ng_kit":
            j.adicionar_item("pocao_hp", 3)
            j.adicionar_item("pocao_mp", 2)
            j.adicionar_item("bomba", 2)
            j.adicionar_item("escudo", 1)
            texto_lento("  🎒 Kit de sobrevivência NG+: 3 Poções HP, 2 MP, 2 Bombas, 1 Escudo.", 0.03)

    # ── BSOD ─────────────────────────────────────────────────
    def _verificar_bsod(self, indice: int, total: int, boss_final_morreu: bool) -> bool:
        """Verifica e dispara a BSOD no momento certo."""
        if self._bsod_disparado_nesta_sessao:
            return False
        from src.tela_azul import deve_disparar_bsod, preparar_retorno_pos_bsod, disparar_tela_azul
        if not deve_disparar_bsod(indice, total, boss_final_morreu):
            return False

        # Salvar ANTES da BSOD
        self.jogador.bsod_visto = True
        self.jogador.mundo_alterado = True
        self.autosave()

        texto_lento("\n  Uma vibração estranha atravessa o terminal.", 0.03)
        pausar(0.8)
        texto_lento("  Como se algo tivesse sido escrito no lugar errado.", 0.03)
        pausar(1.0)

        preparar_retorno_pos_bsod()
        self._bsod_disparado_nesta_sessao = True
        disparar_tela_azul(self.jogador.nome)
        return True

    # ── Batalha ──────────────────────────────────────────────
    def batalha(self, inimigo: Any) -> bool:
        if hasattr(inimigo, "resetar_status_temporarios"):
            inimigo.resetar_status_temporarios()

        self.turno = 1
        log = LogBatalha(inimigo.nome)
        self._intro_batalha(inimigo)

        while self.jogador.esta_vivo() and inimigo.esta_vivo():
            self._tela_estado(inimigo)

            for msg in self.jogador.aplicar_efeitos_inicio_turno():
                texto_lento(f"  {msg}", 0.03)
                log.registrar("efeito", msg)
            for msg in inimigo.aplicar_efeitos_inicio_turno():
                texto_lento(f"  {msg}", 0.03)
                log.registrar("efeito", msg)

            if not self.jogador.esta_vivo() or not inimigo.esta_vivo():
                break

            self._clima(inimigo)

            # ── Turno do jogador ──────────────────────────
            if not self.jogador.turno_está_bloqueado():
                print()
                skill_extra_str = ""
                if self.jogador.skill_extra:
                    skill_extra_str = f"  {cor('[3]', CYAN)} Skill Extra ({self.jogador.skill_extra})\n"

                menu_str = (
                    f"  {cor('[1]', CYAN)} Atacar\n"
                    f"  {cor('[2]', CYAN)} Skill ({self.jogador.skill})\n"
                    f"{skill_extra_str}"
                    f"  {cor('[4]', CYAN)} Defender\n"
                    f"  {cor('[5]', CYAN)} Meditar\n"
                    f"  {cor('[6]', CYAN)} Item\n"
                    f"  {cor('[7]', CYAN)} Analisar inimigo\n"
                    f"  {cor('[8]', CYAN)} Tentar fugir\n"
                    f"  {cor('[9]', CYAN)} Log de batalha\n"
                    f"  {cor('[S]', YELLOW)} Salvar partida"
                )
                print(menu_str)
                acao = input(cor("\n  Escolha: ", YELLOW)).strip().lower()

                if acao == "1":
                    self.jogador.atacar(inimigo)
                    log.registrar("ataque", f"{self.jogador.nome} atacou {inimigo.nome}.")
                elif acao == "2":
                    self.jogador.usar_skill(inimigo, usar_extra=False)
                    log.registrar("skill", f"{self.jogador.nome} usou {self.jogador.skill}.")
                elif acao == "3" and self.jogador.skill_extra:
                    self.jogador.usar_skill(inimigo, usar_extra=True)
                    log.registrar("skill", f"{self.jogador.nome} usou {self.jogador.skill_extra}.")
                elif acao == "4":
                    self.jogador.defender()
                    log.registrar("defesa", f"{self.jogador.nome} defendeu.")
                elif acao == "5":
                    self.jogador.meditar()
                    log.registrar("cura", f"{self.jogador.nome} meditou.")
                elif acao == "6":
                    self._usar_item(inimigo)
                    log.registrar("item", f"{self.jogador.nome} usou item.")
                elif acao == "7":
                    texto_lento(
                        f"  ℹ️  {inimigo.nome} | HP {inimigo.hp}/{inimigo.hp_max} | "
                        f"ATK {inimigo.dano} | DEF {inimigo.defesa} | Skill: {getattr(inimigo, 'skill', '?')}",
                        0.03,
                    )
                    continuar()
                    continue
                elif acao == "8":
                    if isinstance(inimigo, Boss):
                        texto_lento("  🚫 Não dá pra fugir de boss.", 0.03)
                    else:
                        chance = 0.42 + self.jogador.sorte * 0.65
                        if inimigo.hp < inimigo.hp_max * 0.35:
                            chance += 0.12
                        if random.random() < min(0.88, chance):
                            texto_lento(f"  🏃 {self.jogador.nome} escapou.", 0.03)
                            self.autosave()
                            return True
                        else:
                            texto_lento("  ❌ Fuga falhou.", 0.03)
                elif acao == "9":
                    log.exibir()
                    continue
                elif acao == "s":
                    self.salvar_manual()
                    continue
                else:
                    texto_lento("  Opção inválida.", 0.03)
                    continue

            if not inimigo.esta_vivo():
                break

            # ── Turno do inimigo ──────────────────────────
            pausar(0.5)
            texto_lento(f"\n  👹 Turno de {inimigo.nome}...", 0.03)

            if self.jogador.ghost_turns > 0:
                texto_lento(f"  👻 {self.jogador.nome} está no modo fantasma. Ataque ignorado!", 0.03)
                if self.jogador.counter_ready:
                    dano_counter = int(round(self.jogador.dano * 1.5))
                    inimigo.receber_dano(dano_counter, origem=self.jogador.nome)
                    texto_lento(f"  ⚡ Contra-ataque! {dano_counter} de dano.", 0.03)
                    self.jogador.counter_ready = False
                log.registrar("esquiva", f"{self.jogador.nome} esquivou.")
            else:
                if isinstance(inimigo, Boss):
                    acao_ini = inimigo.escolher_acao(self.jogador)
                else:
                    acao_ini = (
                        inimigo.habilidade(self.jogador)
                        if random.random() < 0.32
                        else inimigo.atacar(self.jogador)
                    )
                log.registrar("ataque", f"{inimigo.nome} agiu ({acao_ini}).")

            if not self.jogador.esta_vivo():
                break

            continuar("\n  [ ENTER para próximo turno... ]")
            log.avancar_turno()
            self.turno += 1
            pausar(0.25)

        # ── Resultado ─────────────────────────────────────
        if self.jogador.esta_vivo():
            print()
            texto_lento(f"  🏅 {inimigo.nome} foi derrotado!", 0.03)
            if hasattr(inimigo, "frase_morte"):
                texto_lento(f"  {inimigo.frase_morte()}", 0.03)
            if isinstance(inimigo, Boss):
                texto_lento("  🔥 O capítulo perdeu seu guardião.", 0.03)
                _audio.sfx("vitoria")
                _audio.tocar_musica("exploracao" if not self.ng_plus else "ng_plus")
            self.autosave()
            continuar()
            return True

        texto_lento(f"\n  💀 {self.jogador.nome} caiu em batalha.", 0.03)
        _audio.sfx("derrota")
        self.autosave()
        continuar()
        return False

    # ── Loop principal ───────────────────────────────────────
    def iniciar(self) -> str:
        limpar_tela()
        if self.ng_plus:
            banner("BEYOND THE KERNEL", "O sistema real começa aqui.", MAGENTA)
            texto_lento(
                "  Você derrubou o Imperador do Caos. "
                "E então a tela azul te mostrou que ele era só o começo.",
                0.03,
            )
            _audio.tocar_musica("ng_plus")
        else:
            banner("INÍCIO DA JORNADA", "Sobreviva. Evolua. Termine.")
            texto_lento(
                "  Você entrou em um sistema corrompido. "
                "Não tem atalho. Não tem piedade. Mas tem saída — se você for bom o suficiente.",
                0.03,
            )
            _audio.tocar_musica("exploracao")
        continuar()

        total = len(self.encontros)

        for indice, encontro in enumerate(self.encontros, start=1):
            if not self.jogador.esta_vivo():
                break

            inimigo   = encontro["inimigo"]
            narrativa = encontro.get("narrativa", "")
            titulo    = encontro.get("titulo", f"Encontro {indice}")
            cidade_fn = encontro.get("cidade")
            evento_fn = encontro.get("evento")

            self.jogador.encontro_index = indice

            if cidade_fn:
                _audio.sfx("cidade_entra")
                _audio.tocar_musica("cidade")
                cidade_fn(self.jogador)
                _audio.tocar_musica("exploracao" if not self.ng_plus else "ng_plus")
                if not self.jogador.esta_vivo():
                    break

            if evento_fn:
                evento_fn(self.jogador)

            if narrativa:
                limpar_tela()
                banner(titulo)
                from src.utils import caixa_narrativa
                caixa_narrativa(narrativa)
                continuar()

            self._verificar_npcs()
            if not self.jogador.esta_vivo():
                break

            venceu = self.batalha(inimigo)

            # Verificar BSOD após boss final (indice == total) ou na metade
            if not self.ng_plus and venceu:
                boss_final = isinstance(inimigo, Boss) and indice == total
                if self._verificar_bsod(indice, total, boss_final):
                    # BSOD foi disparada — o jogo "fechou"
                    # Retornar "bsod" para o loop principal tratar
                    return "bsod"

            if not venceu:
                return "derrota"

            self._mostrar_recompensa(inimigo)
            self._verificar_npcs()

            if indice % 4 == 0:
                self._campamento()

        # ── Fim de campanha ───────────────────────────────
        if self.jogador.esta_vivo():
            limpar_tela()
            if self.ng_plus:
                banner("O VAZIO FOI CONFRONTADO", "Você chegou além do fim.", MAGENTA)
                texto_lento(
                    "\n  O VAZIO não foi destruído. Ele não pode ser destruído. "
                    "Mas foi contido. Por você. Por agora.",
                    0.03,
                )
                texto_lento(
                    "  O sistema registra a anomalia e não sabe o que fazer com ela. "
                    "Você é a primeira coisa que ele não conseguiu resolver.",
                    0.03,
                )
            else:
                banner("FIM DA CAMPANHA", "Você chegou onde poucos chegaram.", YELLOW)
                texto_lento(
                    "\n  Você atravessou o caos, derrubou cada guardião e sobreviveu ao núcleo. "
                    "O sistema está em silêncio. Por enquanto.",
                    0.03,
                )
            print()
            texto_lento(f"  🏆 {self.jogador.nome} terminou no nível {self.jogador.level}.", 0.03)
            texto_lento(f"  💰 Ouro acumulado: {self.jogador.ouro}g", 0.03)
            texto_lento(f"  📊 {self.jogador.resumo_completo()}", 0.03)
            self.autosave()
            _audio.tocar_musica("creditos")
            continuar("\n  [ ENTER para voltar ao menu... ]")
            return "vitoria_ng" if self.ng_plus else "vitoria"

        return "derrota"
