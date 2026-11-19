# Orientações para agentes de IA

## Contexto

- Projeto Django em português para vitrine, pedidos e encomendas de uma padaria.
- O app principal é `confeitaria`; as configurações ficam em `nucleo/settings.py`.
- Os nomes de campos, URLs, templates e mensagens seguem o português já usado no projeto.

## Regras para alterações

- Leia os arquivos relacionados antes de editar e mantenha as mudanças limitadas à tarefa.
- `Pedido` e `Encomenda` pertencem ao usuário em `cliente`. Listas, detalhes, edição e exclusão devem sempre filtrar pelo usuário autenticado, sem exceção para `is_staff`.
- Ao criar pedidos ou encomendas, preencha `cliente` no servidor com `request.user`; nunca aceite esse campo do formulário.
- A baixa de estoque do `Pedido` ocorre na mesma transação do salvamento, em `confeitaria/estoque.py`. Cancelar ou excluir um pedido ativo estorna a quantidade. Não deixe o saldo negativo.
- O grupo `Clientes` é associado a usuários novos que não são staff. O grupo `Equipe` cadastra produtos e registra movimentos de estoque. Não libere essas operações só porque o usuário é `is_staff`.
- O app `ia` guarda conversas por `usuario` e responde com o cardápio real e com os pedidos ou encomendas desse usuário. Sem `IA_API_KEY` e `IA_API_URL`, use o assistente local. Não envie pedidos de outros usuários ao modelo e não grave a chave no repositório.
- A tela do assistente é `apps/ia/templates/assistente.html`, carregada pelo `TEMPLATES["DIRS"]`. Não mova esse arquivo para um caminho que o padrão `*/ia/templates/*` deixe de incluir.
- Use Django Forms, CBVs e templates existentes. Preserve CSRF e mensagens de erro/sucesso.
- Crie migrações quando alterar modelos e não edite migrações aplicadas para esconder mudanças de esquema.
- Não inclua `.env`, `.env.*`, senhas, chaves, dados do banco ou credenciais nos commits, prompts ou arquivos enviados a serviços externos.
- Para enviar e-mail em produção, configure o backend SMTP por variáveis de ambiente; o backend de console é apenas para desenvolvimento.
- Bibliotecas de interface externas são carregadas por CDN no layout base. Mantenha inicialização e uso dos plugins em `confeitaria/static/confeitaria/js/site.js`.

## Verificação

1. Instale as dependências de `requirements.txt`.
2. Execute `python manage.py check`.
3. Execute `python manage.py test`.
4. Antes de publicar no App Engine, confira as variáveis secretas, aplique as migrações e gere os arquivos estáticos.
5. A validação externa da plataforma TestAI é manual e depende de acesso do aluno.

## Preparação do Gitingest

No TestAI, use exatamente estes padrões, sem acrescentar outros:

Include: `*.py, *.md, *.js, *.yaml, *.txt, *form.html, *list.html, *detail.html, base*.html, */ia/templates/*`

Exclude: `__init__.py, admin.py, apps.py, tests.py, */migrations/*, venv/*, .venv/*, env/*, staticfiles/*, node_modules/*, *.min.js, */vendor/*, */libs/*`

Os templates de formulário, lista e detalhe terminam em `_form.html`, `_list.html` e `_detail.html`. O layout fica em `base_layout/base.html`. A tela do assistente fica em `apps/ia/templates/`. Não envie `.env`, senhas, chaves ou dados do banco.
