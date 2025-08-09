#!/bin/bash

# Настройки
IMAGE_NAME="fail2ban-telegram-bot"
DOCKER_HUB_USERNAME="yourusername"
VERSION=$(date +"%Y.%m.%d")

# Проверка авторизации в Docker Hub
echo "Проверка авторизации в Docker Hub..."
if ! docker info | grep -q "Username: $DOCKER_HUB_USERNAME"; then
    echo "Вы не авторизованы в Docker Hub или имя пользователя не совпадает."
    echo "Выполните команду: docker login"
    exit 1
fi

# Сборка образа
echo "Сборка образа $IMAGE_NAME:$VERSION..."
docker build -t $IMAGE_NAME:$VERSION .
docker tag $IMAGE_NAME:$VERSION $IMAGE_NAME:latest

# Публикация образа в Docker Hub
echo "Публикация образа в Docker Hub..."
docker tag $IMAGE_NAME:$VERSION $DOCKER_HUB_USERNAME/$IMAGE_NAME:$VERSION
docker tag $IMAGE_NAME:$VERSION $DOCKER_HUB_USERNAME/$IMAGE_NAME:latest

docker push $DOCKER_HUB_USERNAME/$IMAGE_NAME:$VERSION
docker push $DOCKER_HUB_USERNAME/$IMAGE_NAME:latest

echo "Готово! Образ $DOCKER_HUB_USERNAME/$IMAGE_NAME:$VERSION опубликован." 