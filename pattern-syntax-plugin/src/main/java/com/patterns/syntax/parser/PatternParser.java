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
        this.pluginName = tokens.get(1);
    }

    public void parseBlockLine(List<String> tokens) {
        if (tokens.size() != 2) {
            throw  new IllegalArgumentException("Expected: <name> <value>");
        }
        this.pluginParameters.put(tokens.get(0), tokens.get(1));
    }

    public PluginCallInfo getPatternCallInfo() {
        return new PluginCallInfo(pluginName, pluginParameters);
    }

    private static boolean checkHeaderTokens(List<String> tokens) {
        return (
                tokens.size() == 2 ||
                tokens.size() == 3 && tokens.get(tokens.size() - 1).equals("{")
        );
    }
}
