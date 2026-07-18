import random
from typing import Optional, List

from src.utils import texto_lento, continuar


class LogBatalha:
    """Registra eventos de batalha com visual limpo."""

    def __init__(self, nome_inimigo: str):
        self.nome_inimigo = nome_inimigo
        self.eventos: List[tuple] = []
        self.turno_atual = 1

    def registrar(self, tipo: str, mensagem: str) -> None:
        self.eventos.append((self.turno_atual, tipo, mensagem))

    def avancar_turno(self) -> None:
        self.turno_atual += 1

    def exibir(self) -> None:
        from src.utils import limpar_tela, banner, cor, CYAN, MAGENTA, YELLOW, GREEN, GRAY

        limpar_tela()
        banner(f"LOG DE BATALHA — {self.nome_inimigo}")
        print()

        if not self.eventos:
            print(cor("Nenhum evento registrado.", GRAY))
        else:
            for turno, tipo, msg in self.eventos:
                if tipo == "ataque":
                    cor_tipo = YELLOW
                elif tipo == "skill":
                    cor_tipo = MAGENTA
                elif tipo in {"cura", "item"}:
                    cor_tipo = GREEN
                elif tipo == "efeito":
                    cor_tipo = CYAN
                else:
                    cor_tipo = GRAY

                print(f"{cor(f'T{turno}', GRAY)} {cor(f'[{tipo.upper()}]', cor_tipo)} {msg}")

        print()
        continuar("ENTER para voltar...")


class Combatente:
    def __init__(self, nome: str, hp_max: int, dano: int, defesa: int, sorte: float):
        self.nome = nome
        self.hp_max = max(1, int(hp_max))
        self.hp = self.hp_max
        self.dano = max(1, int(dano))
        self.defesa = max(0, int(defesa))
        self.sorte = max(0.0, min(0.95, float(sorte)))

        self.guard_turns = 0
        self.guard_reduction = 0.35

        self.rage_turns = 0
        self.rage_bonus = 0

        self.bleed_turns = 0
        self.bleed_damage = 0

        self.burn_turns = 0
        self.burn_damage = 0

        self.vulnerable_turns = 0
        self.vulnerable_multiplier = 1.12

        self.stun_turns = 0

        self.defesa_bonus = 0
        self.defesa_bonus_turns = 0

    def esta_vivo(self) -> bool:
        return self.hp > 0

    def resetar_status_temporarios(self) -> None:
        self.guard_turns = 0
        self.guard_reduction = 0.35
        self.rage_turns = 0
        self.rage_bonus = 0
        self.bleed_turns = 0
        self.bleed_damage = 0
        self.burn_turns = 0
        self.burn_damage = 0
        self.vulnerable_turns = 0
        self.vulnerable_multiplier = 1.12
        self.stun_turns = 0
        self.defesa_bonus = 0
        self.defesa_bonus_turns = 0

    def aplicar_efeitos_inicio_turno(self) -> List[str]:
        mensagens: List[str] = []

        if self.burn_turns > 0:
            self.hp -= self.burn_damage
            self.burn_turns -= 1
            mensagens.append(f"🔥 {self.nome} sofre {self.burn_damage} de dano por queimadura.")

        if self.bleed_turns > 0:
            self.hp -= self.bleed_damage
            self.bleed_turns -= 1
            mensagens.append(f"🩸 {self.nome} sofre {self.bleed_damage} de dano por sangramento.")

        if self.rage_turns > 0:
            self.rage_turns -= 1
            mensagens.append(f"⚔️  {self.nome} mantém o estado de fúria.")
            if self.rage_turns == 0:
                self.rage_bonus = 0

        if self.guard_turns > 0:
            self.guard_turns -= 1
            mensagens.append(f"🛡️  {self.nome} continua em guarda.")
            if self.guard_turns == 0:
                self.guard_reduction = 0.35

        if self.vulnerable_turns > 0:
            self.vulnerable_turns -= 1
            mensagens.append(f"📉 {self.nome} continua vulnerável.")
            if self.vulnerable_turns == 0:
                self.vulnerable_multiplier = 1.12

        if self.defesa_bonus_turns > 0:
            self.defesa_bonus_turns -= 1
            if self.defesa_bonus_turns == 0:
                self.defesa_bonus = 0

        if self.hp < 0:
            self.hp = 0

        return mensagens

    def aplicar_guardia(self, turnos: int = 1, reducao: float = 0.35) -> None:
        self.guard_turns = max(self.guard_turns, int(turnos))
        self.guard_reduction = max(0.10, min(0.60, float(reducao)))

    def aplicar_furia(self, bonus: int, turnos: int = 2) -> None:
        self.rage_bonus = max(self.rage_bonus, int(bonus))
        self.rage_turns = max(1, int(turnos))

    def aplicar_sangramento(self, dano: int, turnos: int = 2) -> None:
        self.bleed_damage = max(self.bleed_damage, int(dano))
        self.bleed_turns = max(self.bleed_turns, int(turnos))

    def aplicar_queimadura(self, dano: int, turnos: int = 2) -> None:
        self.burn_damage = max(self.burn_damage, int(dano))
        self.burn_turns = max(self.burn_turns, int(turnos))

    def aplicar_vulnerabilidade(self, multiplicador: float = 1.12, turnos: int = 2) -> None:
        self.vulnerable_multiplier = max(self.vulnerable_multiplier, float(multiplicador))
        self.vulnerable_turns = max(1, int(turnos))

    def aplicar_defesa_extra(self, bonus: int, turnos: int = 2) -> None:
        self.defesa_bonus = int(bonus)
        self.defesa_bonus_turns = max(1, int(turnos))

    def esta_atordoado(self) -> bool:
        if self.stun_turns > 0:
            self.stun_turns -= 1
            return True
        return False

    def resumo_status(self) -> str:
        status = []
        if self.guard_turns > 0:
            status.append(f"🛡️ {self.guard_turns}T")
        if self.rage_turns > 0:
            status.append(f"⚔️  {self.rage_turns}T")
        if self.bleed_turns > 0:
            status.append(f"🩸 {self.bleed_turns}T")
        if self.burn_turns > 0:
            status.append(f"🔥 {self.burn_turns}T")
        if self.vulnerable_turns > 0:
            status.append(f"📉 {self.vulnerable_turns}T")
        if self.stun_turns > 0:
            status.append(f"💫 {self.stun_turns}T")
        if self.defesa_bonus_turns > 0:
            status.append(f"🧱 {self.defesa_bonus_turns}T")
        return "Sem efeitos ativos" if not status else " | ".join(status)

    def receber_dano(self, dano: float, origem: Optional[str] = None) -> int:
        dano_real = float(dano)

        if self.guard_turns > 0:
            dano_real *= (1.0 - self.guard_reduction)

        if self.vulnerable_turns > 0:
            dano_real *= self.vulnerable_multiplier

        defesa_total = max(0, self.defesa + self.defesa_bonus)
        dano_real -= defesa_total

        chance_bloqueio = min(0.22, max(0.0, 0.05 + self.sorte * 0.35))
        bloqueio = 0
        if random.random() < chance_bloqueio:
            bloqueio = max(1, int(round(max(dano_real, 1) * 0.18)))
            dano_real -= bloqueio

        if dano_real < 1:
            dano_real = 1

        dano_int = int(round(dano_real))
        self.hp -= dano_int
        if self.hp < 0:
            self.hp = 0

        if origem:
            texto = f"{origem} causou {dano_int} de dano em {self.nome}."
        else:
            texto = f"{self.nome} recebeu {dano_int} de dano."

        if bloqueio > 0:
            texto += f" (bloqueio parcial de {bloqueio})"

        texto_lento(texto, 0.03)
        return dano_int

    def curar(self, valor: int) -> int:
        hp_antes = self.hp
        self.hp = min(self.hp_max, self.hp + max(0, int(valor)))
        return self.hp - hp_antes

    def alterar_defesa(self, valor: int) -> None:
        self.defesa = max(0, self.defesa + int(valor))

    def alterar_dano(self, valor: int) -> None:
        self.dano = max(1, self.dano + int(valor))
