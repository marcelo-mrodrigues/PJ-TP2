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
| **Documentação** | Doxygen  |
| **Controle de Versão** | Github  |
| **Gestão de Projeto** | Asana  |

# TUTORIAL DE PREPARAÇÃO DE AMBIENTE [no vscode linux]
## essa etapa 0 é apenas para quem não conseguir a partir do 1
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




# Passo a passo para Configuração e Utilização (Backend)
Este tutorial guiará você pela configuração do ambiente de desenvolvimento do backend do projeto PJ-TP2. Certifique-se de ter Python 3.10+ e Git instalados em sua máquina.

##  0 - Instale Python e Postgre SQL (caso já tenha instalado pule essa etapa):

1. Instalação do Python:

Linux (Baseado em Debian/Ubuntu):

```
sudo apt update
sudo apt install python3 python3-venv python3-pip
```
windows:

Baixe o instalador mais recente (versão 3.10 ou superior) em python.org/downloads/windows. Certifique-se de marcar a opção "Add Python to PATH" durante a instalação.

2. Instalação do Postgre SQL:
 O PostgreSQL é necessário caso você deseje executar um banco de dados local para desenvolvimento; caso contrário, a conexão com o banco de dados do Railway (Passo 3) é suficiente.

Linux (Baseado em Debian/Ubuntu):
```
sudo apt install postgresql postgresql-contrib -y
sudo service postgresql status # pra ver se instalou com sucesso
```
windows:

Baixe o instalador do PostgreSQL (que geralmente inclui o pgAdmin) em postgresql.org/download/windows. Siga as instruções do instalador para definir a senha do usuário postgres e escolher a porta (padrão é 5432).

##  1 - Clone o repositório: 
No diretório onde você deseja clonar o repositório, execute o seguinte comando para clonar o repositório:

```
git clone https://github.com/marcelo-mrodrigues/PJ-TP2.git
cd PJ-TP2
```

##  2 - Instalar Dependências e Configurar Ambiente do Backend
Utilize o comando make install para criar o ambiente virtual Python, instalar todas as dependências Python listadas no backend/requirements.txt e configurar os hooks de pre-commit para o backend.

```
make install
```
##  3 - Configurar Variáveis de Ambiente (.env)
Para o ambiente de desenvolvimento local, você precisará de um arquivo .env para carregar as variáveis de ambiente, incluindo as credenciais do banco de dados e configurações do Django.

Na pasta backend (ao lado do manage.py), crie um arquivo chamado .env (note o ponto no início) e adicione o seguinte conteúdo.
```
DATABASE_URL="SUA_DATABASE_URL_DO_RAILWAY"
DJANGO_DEBUG="True"
DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"
```
Importante: Substitua SUA_DATABASE_URL_DO_RAILWAY pela URL real do seu serviço PostgreSQL no Railway.

##  4- Rodar o Servidor de Desenvolvimento do Backend (Django)
Inicie o servidor de desenvolvimento do Django.
```
make run-backend
```
O servidor Django estará acessível em http://127.0.0.1:8000/.


##  5- (Opicional) Fazer alteração no banco de dados
Com a DATABASE_URL configurada via .env, o Django pode se conectar ao seu banco de dados. Agora você pode alterar as tabelas do banco com as classes presentes no backend/core/models.py

1. Navegue para a pasta backend para executar os comandos manage.py
```
cd backend
```
2. Ative o ambiente virtual para que manage.py funcione
```
source venv/bin/activate # ou .\env\Scripts\activate no Windows
python manage.py makemigrations core
python manage.py migrate
cd .. # Volte para a raiz do projeto
```


##  6- (Opicional)Criar Superusuário (para acesso ao Django Admin)
Crie um usuário administrador para acessar o painel de administração do Django. Siga as instruções no terminal.

1. Navegue para a pasta backend para executar o comando manage.py
```
cd backend
```
2. Ative o ambiente virtual
```
source venv/bin/activate
python manage.py createsuperuser
cd .. # Volte para a raiz do projeto
```

##  7- (Opcional) Rodar os Testes
Utilize o comando make test para rodar os testes.
```
make test
```
com esses comandos você pode executar os testes, e criar um report, com esse reporte você pode acessar um HTML que te mostra que linhas testou ou não.


```
cd backend/
source venv/bin/activate
python manage.py test core # pra testar toda core
python manage.py test core.testModels # pra testar um dos arquivos de teste
coverage run manage.py test core # coverage total do core
coverage report # pra passar pro html
coverage html # pra abrir o html do coverage no navegador
```
