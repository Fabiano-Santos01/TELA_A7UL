# 🎮 TELA_A7UL
## 🎯 Objetivo

# Desenvolver um RPG de terminal utilizando Python para praticar Programação Orientada a Objetos, modularização, persistência de dados, lógica de programação e organização de projetos, simulando um projeto real de desenvolvimento de software.

# Recrutadores (RH) podem baixar o arquivo ( main.exe ) e jogar tanto o modo Lite = Curto/Recrutador ( Demo ) ou a versão completa Full = Longo/Recrutador
# O arquivo main.exe não está acompanhado de sons, isso irá depender se você possui as bibliotecas pygame e mais algumas nativas no python instaladas. Boa diversão ;

# Observação - Se por algum motivo você não conseguir executar o sistema de (Sons) tente usar este comando no seu terminal
# pip install -r requirements.txt
# Caso o áudio ainda não funcione corretamente: py -3.10 -m pip install --upgrade pygame
# E então aperte "Play/F5" no seu Vscode ou direto no terminal para rodar o game: py -3.10 main.py



![License](https://img.shields.io/badge/license-MIT-yellow)

# Um RPG de terminal desenvolvido em **Python**, inspirado em jogos clássicos de aventura, combinando combate por turnos, exploração, evolução de personagem e uma narrativa de horror tecnológico com pitadas de humor  ( +18 ).

# O projeto foi desenvolvido como forma de praticar **Programação Orientada a Objetos (POO)**, organização de projetos Python, manipulação de arquivos e persistência de dados.

---

# 📸 Demonstração

> Em breve serão adicionadas imagens e GIFs do jogo.

```
docs/
└── screenshots/
    ├── menu.png
    ├── combate.png
    ├── inventario.png
```

---

# ✨ Funcionalidades

- ⚔️ Sistema de combate por turnos
- 👤 Evolução de personagem
- 🎒 Sistema de inventário
- 💰 Loja
- 🏙️ Exploração de cidades
- 👹 Bosses
- 📖 Narrativa
- 💾 Sistema de Save em múltiplos slots
- 🔊 Sistema de áudio
- 🎲 Eventos
- ⭐ Sistema NG+

---

# 🛠 Tecnologias

- Python 3
- JSON
- Programação Orientada a Objetos (POO)
- Manipulação de arquivos
- Organização modular

---

# 📂 Estrutura do Projeto

```text
Tela_A7UL/

├── assets/
│   └── audio/
│
├── docs/
│     └── screenshots/
│           ├── Menu Tela Azul.png
│           ├── Inventário Tela Azul.png
│           └── Combate Tela Azul.png
├── saves/
│
├── src/
│   ├── __init__.py
│   ├── audio.py
│   ├── base.py
│   ├── combate.py
│   ├── enemy.py
│   ├── player.py
│   ├── tela_azul.py
│   ├── utils.py
│   └── world.py
│
├── tools/
│   └── gerar_sons.py
│
├── main.py
├── README.md
├── requirements.txt
├── CHANGELOG.md
└── LICENSE
```

---

# 🚀 Como executar

Clone o repositório:

```bash
git clone https://github.com/SEU-USUARIO/Tela_A7UL.git
```

Entre na pasta:

```bash
cd Tela_A7UL
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute o jogo:

```bash
python main.py
```

---

# 📚 Aprendizados

Durante o desenvolvimento deste projeto foram praticados conceitos como:

- Programação Orientada a Objetos (POO)
- Organização de projetos Python
- Manipulação de arquivos JSON
- Sistema de persistência de dados (Save System)
- Estruturas de dados
- Modularização
- Organização de código
- Lógica de programação

---

# 📌 Roadmap

- [x] Sistema de combate
- [x] Sistema de Save
- [x] Sistema de áudio
- [x] Bosses
- [x] Loja
- [x] Eventos
- [ ] Novos capítulos
- [ ] Novos inimigos
- [ ] Novos eventos

---

# 📄 Licença

Este projeto utiliza a licença **MIT** para o código-fonte.

---

# ⚖️ Aviso

© 2026 **Fabiano da Costa Santos**

O código deste projeto é disponibilizado para estudo, aprendizado e demonstração de portfólio.

A licença **MIT** aplica-se ao código-fonte. Entretanto, a narrativa, personagens, universo, identidade do projeto **TELA_A7UL** e demais elementos criativos permanecem protegidos por direitos autorais.

A utilização comercial desses elementos ou a publicação deste projeto como sendo de outra autoria não é autorizada sem o consentimento do autor.