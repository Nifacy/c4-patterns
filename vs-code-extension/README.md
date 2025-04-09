# C4 DSL Patterns VS Code Extension

**C4 DSL Patterns VS Code Extension** - это расширение для Visual Studio Code,
предназначенное для удобной работы с архитектурными шаблонами в языке [Structurizr DSL](https://structurizr.org/dsl). 
Расширение предоставляет поддержку новой конструкции `$pattern`, а также инструменты для автодополнения, валидации и 
интерактивного взаимодействия с шаблонами.

## Сборка

1. Установите зависимости:

```bash
npm install
```

2. Соберите расширение:

```bash
npm run build-extension
```

В результате сборки будет создан `.vsix` файл, который можно установить в VS Code через команду:

```bash
code --install-extension path/to/extension.vsix
```

## Подробнее

Дополнительные сведения, инструкции по установке и скриншоты доступны в [Wiki проекта](https://github.com/Nifacy/c4-patterns/wiki/VS-Code-Extension).
