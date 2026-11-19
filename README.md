# Padaria Doce & Ponto

Aplicação Django para catálogo de produtos, pedidos e encomendas.

## Requisitos

- Python compatível com Django 5.2
- PostgreSQL configurado pelas variáveis `PGHOST`, `PGDATABASE`, `PGUSER`, `PGPASSWORD` e `PGPORT`
- Dependências de `requirements.txt`

## Executar localmente

1. Crie um ambiente virtual e instale `requirements.txt`.
2. Configure as variáveis de ambiente do banco e defina `DEBUG=True`.
3. Execute `python manage.py migrate`.
4. Crie um usuário com `python manage.py createsuperuser`.
5. Execute `python manage.py runserver`.

Em desenvolvimento, o envio de e-mails usa o backend de console. Para testar, cadastre um usuário com e-mail e solicite a recuperação de senha ou usuário; a mensagem aparecerá no terminal.

## Funcionalidades

- Pedidos e encomendas ficam associados ao usuário que os criou e só esse usuário pode listar, visualizar, alterar ou excluir seus registros.
- Listas de produtos, pedidos e encomendas têm filtros Django Filter e paginação que mantém os critérios selecionados.
- Operações de cadastro, alteração e exclusão informam o resultado por mensagens Django.
- A tela de login permite recuperação de senha por link temporário e recuperação de usuário por e-mail.
- A interface usa jQuery Mask, DataTables e jquery-confirm.
- Há seis modelos além do usuário: Produto, Pedido, Encomenda, MovimentoEstoque, Conversa e Mensagem.
- Confirmar um pedido baixa o estoque na mesma transação. Cancelar ou excluir um pedido ativo devolve a quantidade. O grupo Equipe também registra entradas e saídas manuais.
- Usuários comuns entram no grupo Clientes e fazem pedidos, encomendas e consultas ao assistente. O grupo Equipe cadastra o cardápio e o estoque.
- O assistente fica em `/assistente/`. Sem chave de API, ele responde com os produtos cadastrados. Com `IA_API_URL`, `IA_API_KEY` e `IA_MODELO`, a chamada usa um endpoint compatível com chat completions.

## Deploy no Google App Engine

O arquivo `app.yaml` contém a configuração inicial do serviço. Antes de publicar, é necessário ter um projeto Google Cloud com App Engine criado, faturamento habilitado, `gcloud` instalado/autenticado e acesso ao banco de produção.

1. Configure no ambiente de execução, sem gravar valores no repositório, `SECRET_KEY`, `PGHOST`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGPORT`, `ALLOWED_HOSTS` e as variáveis SMTP (`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`, `DEFAULT_FROM_EMAIL`).
2. Confirme que `DEBUG=False` e que `ALLOWED_HOSTS` contém o domínio real do serviço.
3. Aplique as migrações no banco de produção e gere estáticos com `python manage.py migrate` e `python manage.py collectstatic --noinput`.
4. Selecione o projeto correto com `gcloud config set project ID_DO_PROJETO` e publique com `gcloud app deploy`.
5. Obtenha o endereço publicado com `gcloud app browse`.

Credenciais não devem ser adicionadas a `app.yaml`, ao Gitingest ou ao Git; use a configuração segura de segredos do ambiente de execução. O deploy e o link final dependem da conta e do projeto Google Cloud do responsável, portanto não são executados automaticamente por este código.

## Atividade TestAI e Gitingest

A validação de conhecimentos no TestAI é uma atividade externa feita pelo aluno autenticado na plataforma; não existe integração de código nem credencial do TestAI neste projeto.

Para a auditoria, cole no Gitingest exatamente o Include e o Exclude descritos em `AGENTS.md` e em `contexto_projeto.md`. Não envie `.env`, `.env.*`, `venv/`, arquivos de banco ou credenciais.

## Testes

```powershell
python manage.py check
python manage.py test
```
