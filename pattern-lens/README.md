# Pattern Lens

**Pattern Lens** - это CLI-инструмент, предназначенный для анализа архитектурных паттернов,
реализованных в плагинах Structurizr DSL. Используется расширениями и другими инструментами
для извлечения метаинформации о паттернах: параметрах, описании, аннотациях и т.д.

## Сборка

Для сборки проекта выполните:

```bash
./gradlew build
```

Собранный исполняемый `.jar` файл будет доступен в `build/libs/pattern-lens.jar`.

## Использование

### Проверка, является ли класс паттерном

```bash
java -jar build/libs/pattern-lens.jar is-pattern path/to/workspace.dsl com.example.MyPattern
```

### Получение информации о паттерне

```bash
java -jar build/libs/pattern-lens.jar info path/to/workspace.dsl com.example.MyPattern
```
