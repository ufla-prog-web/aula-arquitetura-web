# Laboratório HTTP com `HTTPServer`

Pequeno servidor didático, sem dependências externas, para estudar HTTP na prática.

## O que você pode testar

- métodos `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `OPTIONS` e `HEAD`;
- cabeçalhos de requisição e resposta;
- cookies (`Set-Cookie` e `Cookie`);
- códigos de status HTTP;
- redirecionamentos (`Location`);
- query strings;
- corpo JSON ou texto;
- informações do cliente e versão HTTP recebida.

## Requisitos

- Python 3.9 ou superior.

Não é necessário instalar bibliotecas com `pip`.

## Executar

```bash
python server.py
```

Abra no navegador:

```text
http://127.0.0.1:8000
```

Para usar outra porta:

```bash
python server.py --port 8080
```

Para aceitar conexões de outros computadores da rede local:

```bash
python server.py --host 0.0.0.0 --port 8000
```

> Para estudo, prefira `127.0.0.1`. Ao usar `0.0.0.0`, o servidor pode ficar acessível a outros dispositivos da rede.

## Endpoints

| Método | Endpoint | Objetivo |
|---|---|---|
| vários | `/api/inspect` | ecoa método, cabeçalhos, cookies, query e corpo |
| GET | `/api/status/<codigo>` | responde deliberadamente com um status entre 200 e 599 |
| GET | `/api/cookies/set` | envia `Set-Cookie` |
| GET | `/api/cookies/read` | mostra o cabeçalho `Cookie` recebido |
| GET | `/api/cookies/delete` | expira um cookie |
| GET | `/api/redirect` | envia `Location` com 301/302/303/307/308 |
| GET | `/api/headers` | devolve cabeçalhos de resposta personalizados |

## Exemplos com curl

### Inspecionar uma requisição

```bash
curl -i \
  -X POST \
  -H 'Content-Type: application/json' \
  -H 'X-Aula: HTTP' \
  -d '{"nome":"Ana"}' \
  'http://127.0.0.1:8000/api/inspect?turma=1'
```

### Testar um 404 proposital

```bash
curl -i http://127.0.0.1:8000/api/status/404
```

### Definir e reenviar cookie

```bash
curl -i -c cookies.txt 'http://127.0.0.1:8000/api/cookies/set?name=usuario&value=joao'
curl -i -b cookies.txt http://127.0.0.1:8000/api/cookies/read
```

### Ver um redirecionamento sem segui-lo

```bash
curl -i 'http://127.0.0.1:8000/api/redirect?code=302&to=/'
```

## Estrutura

```text
http_test_server/
├── server.py
├── README.md
└── web/
    ├── index.html
    ├── style.css
    └── app.js
```

## Observação

Este projeto usa `http.server.HTTPServer` propositalmente para fins didáticos. O servidor da biblioteca padrão do Python **não é recomendado para produção**.
