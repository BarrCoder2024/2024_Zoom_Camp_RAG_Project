docker build -t asktheraragbuddyreg.azurecr.io/frontend:latest ./frontend
docker build -t asktheraragbuddyreg.azurecr.io/backend:latest ./backend
docker build -t asktheraragbuddyreg.azurecr.io/redis:latest ./redis

az acr login --name asktheraragbuddyreg

docker push asktheraragbuddyreg.azurecr.io/frontend:latest
docker push asktheraragbuddyreg.azurecr.io/backend:latest
docker push asktheraragbuddyreg.azurecr.io/redis:latest

az acr repository list --name asktheraragbuddyreg --output table


#######################################################################

DELETE BELOW


docker build --no-cache -t asktheraragbuddyreg.azurecr.io/frontend:latest ./frontend
docker build --no-cache -t asktheraragbuddyreg.azurecr.io/backend:latest ./backend


az acr login --name asktheraragbuddyreg

docker push asktheraragbuddyreg.azurecr.io/frontend:latest
docker push asktheraragbuddyreg.azurecr.io/backend:latest



################################################################
Azure docker compose for backend

services:
  backend:
    image: asktheraragbuddyreg.azurecr.io/backend:latest
    ports:
      - "80:8000"
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis

  redis:
    image: asktheraragbuddyreg.azurecr.io/redis:latest
    ports:
      - "6379:6379"