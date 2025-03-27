package com.patterns.syntax.parser;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class PatternParser {
    private String pluginName;
    private final Map<String, String> pluginParameters;

    public PatternParser() {
        this.pluginName = null;
        this.pluginParameters = new HashMap<>();
    }

    public void parseHeader(List<String> tokens) {
        if (!checkHeaderTokens(tokens)) {
            throw new IllegalArgumentException("Expected: $pattern <pattern-name>");
        }
        this.pluginName = tokens.get(0);
    }

    public void parseBlockLine(List<String> tokens) {
        if (tokens.size() != 2) {
            throw  new IllegalArgumentException("Expected: <name> <value>");
        }
        this.pluginParameters.put(tokens.get(0), tokens.get(1));
    }

    public PluginCallInfo getPluginCallInfo() {
        return new PluginCallInfo(pluginName, pluginParameters);
    }

    private static boolean checkHeaderTokens(List<String> tokens) {
        return tokens.size() == 1;
    }

    public void printCallInfo() {
        System.out.println("- name: " + this.pluginName);
        System.out.println("- params: {");
        for (Map.Entry<String, String> entry: pluginParameters.entrySet()) {
            System.out.println("    '" + entry.getKey() + "': '" + entry.getValue() + "',");
        }
        System.out.println("  }");
    }
}
