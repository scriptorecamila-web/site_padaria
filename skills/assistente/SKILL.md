---
name: assistente
description: Orienta mudanças no app ia, na tela do assistente e no contexto usado por agentes.
---

# Assistente da padaria

- O app Django é `ia`. A tela fica em `apps/ia/templates/assistente.html` e a lista em `apps/ia/templates/conversa_list.html`.
- Cada `Conversa` pertence a `usuario`. Liste, abra e continue apenas conversas de `request.user`, inclusive quando `is_staff` for verdadeiro.
- Grave o autor no servidor. O formulário aceita a pergunta e o identificador da conversa, nunca o usuário.
- A resposta local usa o cardápio e os pedidos ou encomendas dessa conta. Sem `IA_API_KEY` e `IA_API_URL`, não chame API externa.
- Se a API estiver configurada, envie só o cardápio e os registros do usuário atual. A chave permanece no ambiente.
- Não grave chave, senha ou `.env` no código, nas skills ou em `contexto_projeto.md`.
