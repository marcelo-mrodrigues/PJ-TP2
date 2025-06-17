## PJ-TP2
# Projeto Final da Disciplina de Técnicas de Programação 2

## Visão Geral do Projeto
- Objetivo: Construir um site de comparação de preços de produtos

- Tecnologias Utilizadas: O backend será desenvolvido em Python e o frontend em JavaScript com Next.js.

- Metodologia: Desenvolvimento Orientado a Testes (TDD)  e a metodologia ágil Kanban para gestão de tarefas.

# Ferramentas do Projeto

| Componente | Ferramenta Escolhida |
| :--- | :--- |
| **Linguagens** | [cite_start]Python & Javascript  |
| **Frameworks** | [cite_start]Node.js, Next.js  |
| **Padrão de Código** | [cite_start]PEP 8 e Airbnb JavaScript  |
| **Verificadores de Código** | [cite_start]flake8, JSLint  |
| **Formatador de Código** | [cite_start]Black, Prettier  |
| **Framework de Teste** | [cite_start]Pytest, Jest  |
| [cite_start]**Verificador de Cobertura** | coverage.py, Jest --coverage  |
| **Documentação** | [cite_start]???  |
| **Controle de Versão** | [cite_start]Github  |
| **Gestão de Projeto** | [cite_start]Asana  |

## TUTORIAL DE PREPARAÇÃO DE AMBIENTE [no vscode linux]
# essa etapa 0 é apenas para quem não conseguir a partir do 1
0.  Ter python, Git, Make e instale o Node.js
- curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
- feche e abra o vscode, e então rode: nvm install --lts
- veja se instalou node -v npm -v
- crie o arquivo de requisitos do backend: mkdir -p backend depois: touch backend/requirements.txt

- no arquivo, cole: pytest
coverage
flake8
pylint
black
pre-commit

- executar: npx create-next-app@latest frontend e responder de acordo


1.  CLONE O REPOSITORIO (git)
2.  rode `make install` (make)
3.  venv/ `source backend/venv/bin/activate` (ative o ambiente virtual)
4. rode `test` pra ver se ta tudo certo