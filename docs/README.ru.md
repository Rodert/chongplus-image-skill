# ChongPlus Image Skill

Agent Skill для генерации изображений и редактирования референсов через ChongPlus Image API.

[English](../README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Español](README.es.md) | [한국어](README.ko.md)

## Возможности

- Генерация изображений по тексту с `gpt-image-2`
- Редактирование по референсному изображению
- Сохранение API Key в локальной конфигурации текущего пользователя
- Поддержка ответов с изображением в Base64 и URL
- Только стандартная библиотека Python

## Требования

- Клиент с поддержкой Agent Skills и запуска локальных скриптов, например Codex
- Python 3.9 или новее
- ChongPlus API Key с доступом к `gpt-image-2`

Обычные чат-клиенты не могут автоматически установить Skill, выполнить локальный код или безопасно сохранить ключ. В таком случае используйте API напрямую.

## Установка и использование в Codex

Скопируйте следующий текст непосредственно в Codex:

```text
Установи и используй ChongPlus Image Skill:
https://github.com/Rodert/chongplus-image-skill

При первом использовании самостоятельно попроси меня ввести ChongPlus API Key. Безопасно сохрани ключ в локальной конфигурации пользователя, затем автоматически считывай и используй его для последующих запросов. Не проси меня вручную настраивать переменную окружения.

Официальная документация:
https://api.chongplus.plus/tools/image-studio/docs/
```

После установки откройте новый диалог Codex и запросите создание или редактирование изображения. Встроенный клиент сохранит ключ локально и автоматически повторно использует его в последующих запросах ChongPlus.

Нет API Key? Войдите на [ChongPlus Keys](https://api.chongplus.plus/keys), создайте ключ и выберите группу генерации изображений.

## Локальное использование

Запускайте из корня репозитория:

```bash
python3 scripts/chongplus_image.py config --set-key
python3 scripts/chongplus_image.py generate \
  --prompt "A cinematic mountain landscape at sunrise" \
  --size 1536x1024 --output-dir ./outputs
```

Ключ хранится в macOS/Linux в `~/.config/chongplus-image/config.json` (или `$XDG_CONFIG_HOME`), в Windows - в `%APPDATA%\\chongplus-image\\config.json`. В Unix каталог имеет права `0700`, а файл - `0600`.

`config --check` проверяет только локальную конфигурацию. Реальная генерация может расходовать квоту. При `403 / error code: 1010` не меняйте заголовки клиента по умолчанию и попросите оператора ChongPlus проверить события Cloudflare Firewall.

## Настройка Skill

Для собственного сценария генерации передайте AI Agent этот репозиторий и [документацию ChongPlus Image API](https://api.chongplus.plus/tools/image-studio/docs/). Документация является источником истины для endpoint, параметров, поддерживаемых размеров и форматов ответов.
