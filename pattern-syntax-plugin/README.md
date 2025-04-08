# Pattern Syntax Plugin

**Pattern Syntax Plugin** - это расширение для языка [Structurizr DSL](https://structurizr.org/dsl),
добавляющее поддержку новой синтаксической конструкции `$pattern`.
Эта конструкция позволяет напрямую подключать архитектурные шаблоны в модели DSL,
делая их более выразительными и повторно используемыми.

## Сборка

Перед сборкой убедитесь, что опубликованы локально следующие библиотеки:

- [`pattern-lib`](../pattern-lib/README.md)
- [`pattern-syntax-parser`](../pattern-syntax-parser/README.md)

Затем выполните:

```bash
./gradlew build
```

Сборка создаст `pattern-syntax-plugin.jar` в `build/libs/`.

## Использование

Для подключения расширения к Structurizr DSL используйте Java Agent при запуске вашего приложения:

```bash
java -javaagent:/path/to/pattern-syntax-plugin.jar \
     -jar /path/to/your-app.jar \
     arg1 arg2 ...
```

Это добавит поддержку конструкции `$pattern` без необходимости модифицировать основную реализацию DSL.

## Подробнее

Полное описание синтаксиса `$pattern`, примеры и сценарии использования доступны в
[Wiki проекта](https://github.com/Nifacy/c4-patterns/wiki/Pattern-Syntax-Plugin).
