package com.patterns.params;

import java.lang.reflect.Field;
import java.lang.reflect.ParameterizedType;
import java.lang.reflect.Type;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public class ParserFactory {

    public <T extends Schema> SchemaParser<T> fromSchema(Class<T> schema) {
        return (SchemaParser<T>) fromType(schema);
    }

    Parser<?> fromType(Type type) {
        if (type == String.class) {
            return new StringParser();
        }

        if (type == Integer.class) {
            return new IntegerParser();
        }

        if (type instanceof ParameterizedType) {
            ParameterizedType parameterizedType = (ParameterizedType) type;
            Type[] typeArguments = parameterizedType.getActualTypeArguments();
            Type rawType = parameterizedType.getRawType();

            if (rawType == Optional.class) {
                Type elementType = typeArguments[0];
                Parser<?> elementParser = fromType(elementType);
                return new OptionalParser(elementParser);
            }

            if (rawType == List.class) {
                Type elementType = typeArguments[0];
                Parser<?> elementParser = fromType(elementType);
                return new ListParser(elementParser);
            }
        }

        if (type instanceof Class<?>) {
            Class<?> classType = (Class<?>) type;
            if (Schema.class.isAssignableFrom(classType)) {
                Map<String, Parser<?>> fieldParsers = new HashMap();

                for (Field field : classType.getDeclaredFields()) {
                    Parser<?> fieldParser = fromType(field.getGenericType());
                    fieldParsers.put(field.getName(), fieldParser);
                }

                return new SchemaParser(classType, fieldParsers);
            }
        }

        throw new IllegalArgumentException("Unknown type: " + type);
    }
}
