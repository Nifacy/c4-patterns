package com.patterns.syntax;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class PatternCallParser {
    private String pluginName;
    private Map<String, String> pluginParameters;

    public PatternCallParser() {
        this.pluginName = null;
        this.pluginParameters = new HashMap<>();
    }

    public void parseHeader(List<String> tokens) {
        this.pluginName = tokens.get(1);
    }

    public void parseBlockLine(List<String> tokens) {
        this.pluginParameters.put(tokens.get(0), tokens.get(1));
    }

    public PatternCallInfo getPatternCallInfo() {
        return new PatternCallInfo(pluginName, pluginParameters);
    }
}
