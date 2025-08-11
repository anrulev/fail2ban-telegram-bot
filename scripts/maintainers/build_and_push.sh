#!/bin/bash

# Внутренний скрипт для мейнтейнеров: сборка и публикация образа в Docker Hub

set -euo pipefail

IMAGE_NAME="fail2ban-telegram-bot"
DOCKER_HUB_USERNAME="yourusername"
VERSION=$(date +"%Y.%m.%d")

echo "Проверка авторизации в Docker Hub..."
if ! docker info | grep -q "Username: $DOCKER_HUB_USERNAME"; then
  echo "Вы не авторизованы в Docker Hub или имя пользователя не совпадает."
  echo "Выполните: docker login"
  exit 1
fi

echo "Сборка образа $IMAGE_NAME:$VERSION..."
docker build -t $IMAGE_NAME:$VERSION .
docker tag $IMAGE_NAME:$VERSION $IMAGE_NAME:latest

echo "Публикация образа в Docker Hub..."
docker tag $IMAGE_NAME:$VERSION $DOCKER_HUB_USERNAME/$IMAGE_NAME:$VERSION
docker tag $IMAGE_NAME:$VERSION $DOCKER_HUB_USERNAME/$IMAGE_NAME:latest

docker push $DOCKER_HUB_USERNAME/$IMAGE_NAME:$VERSION
docker push $DOCKER_HUB_USERNAME/$IMAGE_NAME:latest

echo "Готово! Образ $DOCKER_HUB_USERNAME/$IMAGE_NAME:$VERSION опубликован."


