# ChongPlus Image Skill

Agent Skill para generar imagenes y editar imagenes de referencia mediante la API de ChongPlus Image.

[English](../README.md) | [简体中文](README.zh-CN.md) | [繁體中文](README.zh-TW.md) | [日本語](README.ja.md) | [Русский](README.ru.md) | [한국어](README.ko.md)

## Funciones

- Generacion de imagenes desde texto con `gpt-image-2`
- Edicion a partir de una imagen de referencia
- Guarda la API Key en la configuracion local del usuario actual
- Compatible con respuestas de imagen Base64 y URL
- Solo requiere la biblioteca estandar de Python

## Requisitos

- Un cliente compatible con Agent Skills y ejecucion de scripts locales, como Codex
- Python 3.9 o posterior
- Una API Key de ChongPlus con acceso a `gpt-image-2`

Los clientes de chat normales no pueden instalar Skills, ejecutar codigo local ni guardar credenciales de forma segura. En ese caso, use la API directamente.

## Instalar y usar en Codex

Copie lo siguiente directamente en Codex:

```text
Instala y usa el ChongPlus Image Skill:
https://github.com/Rodert/chongplus-image-skill

En el primer uso, pídeme de forma proactiva mi ChongPlus API Key. Guárdala de forma segura en la configuración local del usuario y léela y reutilízala automáticamente en solicitudes posteriores. No me pidas configurar una variable de entorno manualmente.

Documentación oficial:
https://api.chongplus.plus/tools/image-studio/docs/
```

Tras instalarlo, abra una conversación nueva de Codex y solicite generar o editar una imagen. El cliente incluido guarda la clave localmente y la reutiliza en solicitudes posteriores de imágenes ChongPlus.

¿No tiene una API Key? Inicie sesion en [ChongPlus Keys](https://api.chongplus.plus/keys), cree una clave y seleccione el grupo de generacion de imagenes.

## Uso local

Ejecute desde la raiz del repositorio:

```bash
python3 scripts/chongplus_image.py config --set-key
python3 scripts/chongplus_image.py generate \
  --prompt "A cinematic mountain landscape at sunrise" \
  --size 1536x1024 --output-dir ./outputs
```

La clave se guarda en macOS/Linux en `~/.config/chongplus-image/config.json` (o `$XDG_CONFIG_HOME`) y en Windows en `%APPDATA%\\chongplus-image\\config.json`. En Unix, el directorio usa permiso `0700` y el archivo `0600`.

`config --check` solo comprueba la configuracion local. Una generacion real puede consumir cuota. Si recibe `403 / error code: 1010`, mantenga los encabezados predeterminados del cliente y pida al operador de ChongPlus que revise los eventos del firewall de Cloudflare.

## Personalizar el Skill

Para un flujo de imagenes personalizado, entregue este repositorio y la [documentacion de la API de ChongPlus Image](https://api.chongplus.plus/tools/image-studio/docs/) a un AI Agent. La documentacion es la fuente de verdad para endpoints, parametros, tamanos compatibles y formatos de respuesta.
