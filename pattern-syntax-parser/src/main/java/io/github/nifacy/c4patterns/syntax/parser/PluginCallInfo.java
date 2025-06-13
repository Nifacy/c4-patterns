package io.github.nifacy.c4patterns.syntax.parser;

import java.util.Map;

public class PluginCallInfo {
    private final String name;
    private final Map<String, String> parameters;

    public PluginCallInfo(
        String name,
        Map<String, String> parameters
    ) {
        this.name = name;
        this.parameters = parameters;
    }

    public String getName() {
        return name;
    }

    public Map<String, String> getParameters() {
        return parameters;
    }
}
