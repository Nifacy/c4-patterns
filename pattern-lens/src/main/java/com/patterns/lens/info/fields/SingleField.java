package com.patterns.lens.info.fields;

public class SingleField implements SchemaField {

    private final String name;
    private final boolean isOptional;

    public SingleField(String name, boolean isOptional) {
        this.name = name;
        this.isOptional = isOptional;
    }

    public String getName() {
        return this.name;
    }

    public boolean isOptional() {
        return this.isOptional;
    }
}
