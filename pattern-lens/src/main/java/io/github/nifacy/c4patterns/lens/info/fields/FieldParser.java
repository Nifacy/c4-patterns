package io.github.nifacy.c4patterns.lens.info.fields;

import java.lang.reflect.Field;
import java.lang.reflect.ParameterizedType;
import java.lang.reflect.Type;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

public class FieldParser {

    private final Class<?> schemaTagClass;

    public FieldParser(Class<?> schemaTagClass) {
        this.schemaTagClass = schemaTagClass;
    }

    public List<SchemaField> fromSchema(Type type) {
        if (type instanceof Class<?>) {
            Class<?> classType = (Class<?>) type;

            if (isSchemaClass(classType)) {
                List<SchemaField> schemaFields = new ArrayList<>();

                for (Field field : classType.getDeclaredFields()) {
                    schemaFields.add(parseSchemaField(field));
                }

                return schemaFields;
            }
        }

        throw new IllegalArgumentException(type + " is not a schema");
    }

    private SchemaField parseSchemaField(Field field) {
        Type fieldType = field.getGenericType();

        if (fieldType instanceof ParameterizedType) {
            ParameterizedType parameterizedType = (ParameterizedType) fieldType;
            Type[] typeArguments = parameterizedType.getActualTypeArguments();
            Type rawType = parameterizedType.getRawType();

            if (rawType == Optional.class) {
                return new SingleField(field.getName(), true);
            }

            if (rawType == List.class) {
                Type elementType = typeArguments[0];
                return new FieldArray(field.getName(), fromSchema(elementType));
            }
        }

        return new SingleField(field.getName(), false);
    }

    private boolean isSchemaClass(Class<?> clazz) {
        return this.schemaTagClass.isAssignableFrom(clazz);
    }
}
