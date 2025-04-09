package io.github.nifacy.c4patterns.lens.info;

import java.util.List;
import java.util.Optional;

import io.github.nifacy.c4patterns.lens.info.fields.SchemaField;

public class PatternInfo {

    private final String pluginName;
    private final List<SchemaField> fields;
    private final Optional<String> documentation;

    public PatternInfo(String pluginName, List<SchemaField> fields, Optional<String> documentation) {
        this.pluginName = pluginName;
        this.fields = fields;
        this.documentation = documentation;
    }

    public List<SchemaField> getFields() {
        return this.fields;
    }

    public Optional<String> getDocumentation() {
        return this.documentation;
    }

    public String getPluginName() {
        return this.pluginName;
    }
}
