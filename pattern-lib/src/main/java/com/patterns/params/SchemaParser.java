package com.patterns.params;

import java.lang.reflect.Field;
import java.util.Map;
import java.util.function.Function;

public class SchemaParser<T extends Schema> implements Parser<T> {

    private final Map<String, Parser<?>> fieldParsers;
    private final Class<T> targetClass;

    public SchemaParser(Class<T> targetClass, Map<String, Parser<?>> fieldParsers) {
        this.fieldParsers = fieldParsers;
        this.targetClass = targetClass;
    }

    @Override
    public T parse(String prefix, Function<String, String> parameterGetter) throws ParseError {
        try {
            T instance = this.targetClass.getDeclaredConstructor().newInstance();
            boolean isPartlySpecified = false;

            for (Field field : this.targetClass.getDeclaredFields()) {
                String fieldPrefix;

                if ("".equals(prefix)) {
                    fieldPrefix = field.getName(); 
                }else {
                    fieldPrefix = prefix + "." + field.getName();
                }

                Parser<?> fieldParser = this.fieldParsers.get(field.getName());

                try {
                    Object value = fieldParser.parse(fieldPrefix, parameterGetter);
                    field.setAccessible(true);
                    field.set(instance, value);
                    isPartlySpecified = true;
                } catch (ExpectedNotNull e) {
                    if (prefix.isEmpty()) {
                        throw e;
                    }

                    if (isPartlySpecified) {
                        throw new FieldNotSpecified(prefix, field.getName());
                    }
                    throw new ExpectedNotNull(prefix);
                }
            }

            return instance;

        } catch (ParseError e) {
            throw e;
        } catch (Exception e) {
            throw new ParseError(e.toString());
        }
    }
}
