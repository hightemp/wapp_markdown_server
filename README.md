# wapp_markdown_server

Сервер для markdown файлов.

## Вырианты запуска приложения

### С .env

```
MD_PATH=/home/user/md
```

### С параметром

```
dist/__main__ -b0.0.0.0:5022 -d /test/path
wapp_markdown_server.bin -b0.0.0.0:5022 -d /test/path
```

## Сборка и запуск

### flask

```bash
build.sh flask
```

### zipapp

```bash
build.sh zipapp run
```

### pyinstaller

```bash
build.sh pyinst_docker run
```