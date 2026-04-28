# Sistema de Recomendação de Jogos

Este projeto implementa um sistema de recomendação de jogos baseado em conteúdo, utilizando KNN e similaridade de cosseno. A aplicação é composta por um **frontend (Angular)** e um **backend (FastAPI)**, que devem ser executados simultaneamente.

---

## Dependências

### Frontend (Angular)

Acesse o diretório do frontend e instale as dependências:
```bash
cd frontend
npm install
```

### Backend (FastAPI)

Acesse o diretório do backend e instale as dependências:
```bash
cd backend
pip install -r requirements.txt
```

## Como Executar

Para o funcionamento correto da aplicação, frontend e backend devem estar rodando ao mesmo tempo.
1. Iniciar o Backend
```bash
cd backend
fastapi run
```

2.Iniciar o Frontend
```bash
cd frontend
ng serve
```

## Acessando a Aplicação

Após iniciar ambos os serviços, abra o navegador e acesse:
http://localhost:4200
