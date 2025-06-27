## PJ-TP2
# Projeto Final da Disciplina de Técnicas de Programação 2

## Visão Geral do Projeto
- Objetivo: Construir um site de comparação de preços de produtos

- Tecnologias Utilizadas: O backend será desenvolvido em Python e o frontend em JavaScript com Next.js.

- Metodologia: Desenvolvimento Orientado a Testes (TDD)  e a metodologia ágil Kanban para gestão de tarefas.

# Ferramentas do Projeto

| Componente | Ferramenta Escolhida |
| :--- | :--- |
| **Linguagens** | Python & Javascript  |
| **Frameworks** | Node.js, Next.js  |
| **Padrão de Código** | PEP 8 e Airbnb JavaScript  |
| **Verificadores de Código** | flake8, JSLint  |
| **Formatador de Código** | Black, Prettier  |
| **Framework de Teste** | Pytest, Jest  |
| **Verificador de Cobertura** | coverage.py, Jest --coverage  |
| **Documentação** | ???  |
| **Controle de Versão** | Github  |
| **Gestão de Projeto** | Asana  |

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




Passo a passo para Configuração e Utilização (Backend)
Este tutorial guiará você pela configuração do ambiente de desenvolvimento do backend do projeto PJ-TP2. Certifique-se de ter Python 3.10+ e Git instalados em sua máquina.

1. Clonar o repositório
Abra o terminal e clone o repositório. O cd PJ-TP2 navegará para a raiz do projeto.

git clone https://github.com/marcelo-mrodrigues/PJ-TP2.git
cd PJ-TP2

2. Instalar Dependências e Configurar Ambiente do Backend
Utilize o comando make install para criar o ambiente virtual Python, instalar todas as dependências Python listadas no backend/requirements.txt e configurar os hooks de pre-commit para o backend.

make install

3. Configurar Variáveis de Ambiente (.env)
Para o ambiente de desenvolvimento local, você precisará de um arquivo .env para carregar as variáveis de ambiente, incluindo as credenciais do banco de dados e configurações do Django.

Na pasta backend (ao lado do manage.py), crie um arquivo chamado .env (note o ponto no início) e adicione o seguinte conteúdo.

Importante: Substitua SUA_DATABASE_URL_DO_RAILWAY pela URL real do seu serviço PostgreSQL no Railway. Esta URL está disponível no painel do Railway, na aba "Variables" do seu serviço de banco de dados.

# backend/.env
DATABASE_URL="SUA_DATABASE_URL_DO_RAILWAY"
DJANGO_DEBUG="True"
DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"

ATENÇÃO: O arquivo .env NÃO DEVE ser commitado no Git, pois contém informações sensíveis. Verifique se backend/.env está presente no seu arquivo .gitignore (na raiz do projeto).

4. Aplicar as Migrações do Banco de Dados
Com a DATABASE_URL configurada via .env, o Django pode se conectar ao seu banco de dados. Agora, aplique as migrações para criar todas as tabelas (tanto as padrão do Django quanto as customizadas do seu app core).

# Navegue para a pasta backend para executar os comandos manage.py
cd backend
# Ative o ambiente virtual para que manage.py funcione
source venv/bin/activate
python manage.py makemigrations core
python manage.py migrate
cd .. # Volte para a raiz do projeto

(As tabelas padrão do Django, como auth_user, serão criadas junto com suas tabelas customizadas como core_produto, core_usuario, etc. Isso é esperado.)

5. Criar Superusuário (para acesso ao Django Admin)
Crie um usuário administrador para acessar o painel de administração do Django. Siga as instruções no terminal.

# Navegue para a pasta backend para executar o comando manage.py
cd backend
# Ative o ambiente virtual
source venv/bin/activate
python manage.py createsuperuser
cd .. # Volte para a raiz do projeto

6. Rodar o Servidor de Desenvolvimento do Backend (Django)
Inicie o servidor de desenvolvimento do Django.

make run-backend

O servidor Django estará acessível em http://127.0.0.1:8000/.

7. (Opcional) Rodar os Testes
Utilize o comando make test para rodar os testes.

make test

