# FileBox — servidor de arquivos com HTTPServer

Projeto didático feito somente com a biblioteca padrão do Python e JavaScript puro.

## Recursos

- Interface web responsiva
- Upload por seleção ou arrastar-e-soltar
- Listagem de arquivos
- Busca por nome
- Download
- Exclusão
- API HTTP simples com `GET`, `PUT` e `DELETE`
- Nenhuma dependência externa

## Requisitos

- Python 3.10 ou superior

## Executar

No terminal, entre na pasta do projeto e execute:

```bash
python server.py
```

Depois abra no navegador:

```text
http://127.0.0.1:8000
```

Os arquivos enviados ficam na pasta `shared/`.

## Opções

Mudar a porta:

```bash
python server.py --port 9000
```

Permitir acesso de outros computadores da rede local:

```bash
python server.py --host 0.0.0.0
```

Usar outra pasta para armazenar arquivos:

```bash
python server.py --directory ./meus_arquivos
```

Alterar o limite de upload:

```bash
python server.py --max-upload-mb 500
```

## Endpoints HTTP

| Método | Rota | Função |
|---|---|---|
| GET | `/` | Interface web |
| GET | `/api/files` | Lista os arquivos em JSON |
| GET | `/files/<nome>` | Faz download |
| PUT | `/api/files/<nome>` | Envia ou substitui um arquivo |
| DELETE | `/api/files/<nome>` | Exclui um arquivo |

Exemplo com `curl`:

```bash
curl -T exemplo.pdf http://127.0.0.1:8000/api/files/exemplo.pdf
```

Listar arquivos:

```bash
curl http://127.0.0.1:8000/api/files
```

Excluir:

```bash
curl -X DELETE http://127.0.0.1:8000/api/files/exemplo.pdf
```

## Observação de segurança

Este projeto foi pensado para estudo e uso local/rede confiável. Ele **não possui autenticação** e utiliza HTTP sem criptografia. Não exponha diretamente na Internet. Para produção seriam necessários, entre outros pontos, HTTPS, autenticação, autorização, limites adicionais, auditoria e um servidor/proxy apropriado.
