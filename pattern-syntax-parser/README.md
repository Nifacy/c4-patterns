# Pattern Syntax Parser

**Pattern Syntax Parser** - это библиотека для разбора объявлений архитектурных
паттернов в расширении языка Structurizr DSL. Может использоваться как
самостоятельный модуль в сторонних инструментах, требующих синтаксического
анализа паттернов.

## Сборка

Для сборки библиотеки выполните:

```bash
./gradlew build
```

## Публикация в локальный Maven

### Опубликовать debug-версию

```bash
./gradlew publishDebugPublicationToMavenLocal
```

### Опубликовать релизную версию

```bash
./gradlew publishReleasePublicationToMavenLocal
```

После публикации библиотека будет доступна другим модулям в рамках локального Maven-репозитория
