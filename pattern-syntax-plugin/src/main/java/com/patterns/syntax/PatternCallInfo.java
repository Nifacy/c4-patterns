package com.patterns.syntax;

import java.util.Map;

public class PatternCallInfo {
    private final String pluginName;
    private final Map<String, String> pluginParameters;

    public PatternCallInfo(String pluginName, Map<String, String> pluginParameters) {
        this.pluginName = pluginName;
        this.pluginParameters = pluginParameters;
    }

    public String getPluginName() {
        return pluginName;
    }

    public Map<String, String> getPluginParameters() {
        return pluginParameters;
    }
}
