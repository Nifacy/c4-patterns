# Pattern Examples

Примеры архитектурных паттернов и рабочих пространств Structurizr DSL,
предназначенные для демонстрации и повторного использования в
проектировании программных систем.

## Содержимое

В репозитории представлены следующие архитектурные паттерны, реализованные в виде Java-плагинов:

- [Saga](./pattern-plugins/src/main/java/Saga.java)
- [Database per Service](./pattern-plugins/src/main/java/DatabasePerService.java)
- [Layered Architecture](./pattern-plugins/src/main/java/Layered.java)
- [Reverse Proxy](./pattern-plugins/src/main/java/ReverseProxy.java)
- [Service Registry](./pattern-plugins/src/main/java/ServiceRegistry.java)

Каждый паттерн сопровождается демонстрационной моделью на языке Structurizr DSL,
показывающей пример использования в контексте архитектуры программной системы.

## Требования

- Java 17
- Gradle 8
- Structurizr DSL (опционально, для визуализации моделей)

## Сборка и запуск

Перед использованием убедитесь, что библиотека [`pattern-lib`](../pattern-lib/README.md)
собрана и опубликована локально.

Соберите проект с помощью команды:

```bash
./gradlew build
```

После успешной сборки:

- Все демонстрационные паттерны будут собраны в директории `build/workspaces/plugins`
- Демонстрационные модели Structurizr DSL появятся в `build/workspaces`

### Структура проекта

```
pattern-examples/
└── build/                         # Сгенерированные DSL-модели и плагины после сборки
    └── workspaces/
        ├── plugins/              # Скомпилированные паттерны
        └── *.dsl                 # Демонстрационные модели Structurizr DSL
```

## Использование

Вы можете импортировать демонстрационные DSL-модели в Structurizr Lite или Structurizr DSL editor и визуализировать применение каждого паттерна в архитектуре системы.
