package com.patterns.syntax;

import java.util.ArrayList;
import java.util.List;

public class PatternCallWrapper {
    private static final String PATTERN_KEYWORD = "$pattern";
    private static final String PLUGIN_KEYWORD = "!plugin";
    private static final String PATTERN_NAME_PREFIX = "pattern:";
    private static final String PATTERN_HEADER_TOKENS_SEPARATOR = ";";

    public static boolean isPatternHeader(List<String> tokens) {
        return !tokens.isEmpty() && tokens.get(0).equals(PATTERN_KEYWORD);
    }

    public static List<String> wrapPatternHeader(List<String> tokens) {
        int lastIndex = tokens.size();
        boolean lastTokenIsBracket = tokens.get(tokens.size() - 1).equals("{");

        if (lastTokenIsBracket) {
            lastIndex--;
        }

        List<String> patternTokens = tokens.subList(1, lastIndex);
        String pluginName = wrapInPluginName(patternTokens);

        List<String> pluginHeader = new ArrayList<>(List.of(PLUGIN_KEYWORD, pluginName));
        if (lastTokenIsBracket) {
            pluginHeader.add("{");
        }

        return pluginHeader;
    }

    private static String wrapInPluginName(List<String> patternHeaderTokens) {
        StringBuilder pluginName = new StringBuilder(PATTERN_NAME_PREFIX);

        for (String token : patternHeaderTokens) {
            pluginName.append(token);
            pluginName.append(PATTERN_HEADER_TOKENS_SEPARATOR);
        }

        return pluginName.toString();
    }

    public static boolean isWrappedPluginName(String pluginName) {
        return pluginName.startsWith(PATTERN_NAME_PREFIX);
    }

    public static List<String> unwrapFromPluginName(String pluginName) {
        String patternTokens = pluginName.replaceFirst("^" + PATTERN_NAME_PREFIX, "");
        return List.of(patternTokens.split(PATTERN_HEADER_TOKENS_SEPARATOR));
    }
}
