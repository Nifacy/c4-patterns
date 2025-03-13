package com.patterns.lens.info;

import java.lang.reflect.ParameterizedType;
import java.lang.reflect.Type;
import java.util.List;
import java.util.Optional;

import com.patterns.lens.info.fields.FieldParser;
import com.patterns.lens.info.fields.SchemaField;

public class PatternInfoGetter {

    private final DocumentationGetter docGetter;
    private final FieldParser fieldParser;

    public PatternInfoGetter(Class<?> schemaTagClass) {
        this.docGetter = new DocumentationGetter();
        this.fieldParser = new FieldParser(schemaTagClass);
    }

    public PatternInfo getInfo(Class<?> patternClass) {
        Optional<String> documentation = docGetter.getDocumentation(patternClass);

        ParameterizedType superclass = (ParameterizedType) patternClass.getGenericSuperclass();
        Type schemaType = superclass.getActualTypeArguments()[0];
        List<SchemaField> fields = this.fieldParser.fromSchema(schemaType);

        return new PatternInfo(patternClass.getTypeName(), fields, documentation);
    }
}
