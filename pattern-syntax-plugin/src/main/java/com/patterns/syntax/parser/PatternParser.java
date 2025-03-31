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

        logMessage("Initialized");
    }

    public void parseHeader(List<String> tokens) {
        logMessage("parse header...");
        logMessage("header tokens: " + tokens);

        if (!checkHeaderTokens(tokens)) {
            throw new IllegalArgumentException("Expected: $pattern <pattern-name>");
        }
        this.pluginName = tokens.get(0);

        logMessage("parse header... ok");
        logMessage("pluginName: " + this.pluginName);
    }

    public void parseBlockLine(List<String> tokens) {
        logMessage("parse block line...");
        logMessage("line tokens: " + tokens);

        if (tokens.size() != 2) {
            throw  new IllegalArgumentException("Expected: <name> <value>");
        }
        this.pluginParameters.put(tokens.get(0), tokens.get(1));

        logMessage("parse block line... ok");
    }

    public PluginCallInfo getPluginCallInfo() {
        PluginCallInfo info = new PluginCallInfo(pluginName, pluginParameters);

        logMessage("pattern call info:");
        logMessage("- name: '" + info.getName() + "'");
        logMessage("- parameters: {");
        for (Map.Entry<String, String> entry : info.getParameters().entrySet()) {
            logMessage("    '" + entry.getKey() + "': '" + entry.getValue() + "',");
        }
        logMessage("}");

        return info;
    }

    private static boolean checkHeaderTokens(List<String> tokens) {
        return tokens.size() == 1;
    }

    private String getLogPrefix() {
        int objectId = hashCode();
        String typeName =  this.getClass().getName();

        return "[" + typeName + "@" + objectId + "] ";
    }

    private void logMessage(String message) {
        System.err.println(getLogPrefix() + message);
    }
}
