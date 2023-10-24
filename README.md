# todoapi

## Como executar

1 - Clone o projeto utilizando o método que você preferir.

2 - Defina a variável de ambiente **SECRET_KEY**:
```bash
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex())')"
```
Como alternativa, você pode deixá-la hardcoded no `compose.yaml` ou colocá-la em um arquivo `.env`.

3 - Navegue até a raiz do projeto e inicie o contêiner:
```bash
docker compose up -d
```

4 - Aplique as migrações de banco de dados (se posteriormente, você optar por destruir o volume, será necessário refazer essa etapa):
```bash
docker exec -t todoapi poetry run alembic upgrade head
```

5 - Acesse a [documentação da API](http://0.0.0.0:8000/docs).

## FAQ

### Como rodar os testes?

```bash
docker exec -it todoapi poetry run task test
```

### Como excluir o contêiner?

```bash
docker compose down
```

### Como excluir o contêiner e o volume?

```bash
docker compose down -v
```
