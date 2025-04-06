package io.github.nifacy.c4patterns.lens.info.fields;

import java.util.List;

public class FieldArray implements SchemaField {

    private final String name;
    private final List<SchemaField> elementFields;

    public FieldArray(String name, List<SchemaField> elementFields) {
        this.name = name;
        this.elementFields = elementFields;
    }

    public String getName() {
        return this.name;
    }

    public List<SchemaField> getElementFields() {
        return this.elementFields;
    }
}
