package com.patterns.syntax;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class PatternPreprocessor {
    private static final String PATTERN_KEYWORD = "$pattern";
    private static final String PLUGIN_KEYWORD = "!plugin";

    private static List<String> lastTokens = null;
    private static PatternCallParser currentParser = null;

    public static List<String> preProcessTokens(List<String> tokens) {
        List<String> result = new ArrayList<>();
        boolean madeChanged = false;

        for (int index = 0; index < tokens.size(); index++) {
            String token = tokens.get(index);
            if (index == 0 && token.equals(PATTERN_KEYWORD)) {
                token = PLUGIN_KEYWORD;
                madeChanged = true;
            }
            result.add(token);
        }

        lastTokens = result;

        if (madeChanged) {
            startPatternDefinition();
        }

        return result;
    }

    public static List<String> getLastTokens() {
        return lastTokens;
    }

    public static void startPatternDefinition() {
        System.err.println("[PatternPreprocessor] start pattern definition");

        if (inPatternDefinition()) {
            throw new RuntimeException("[PatternPreprocessor] pattern definition already started");
        }

        currentParser = new PatternCallParser();
    }

    public static void endPatternDefinition() {
        System.err.println("[PatternPreprocessor] end pattern definition");

        if (!inPatternDefinition()) {
            throw new RuntimeException("[PatternPreprocessor] pattern definition not started");
        }

        PatternCallInfo info = currentParser.getPatternCallInfo();
        System.err.println("[PatternPreprocessor] pattern call info:");
        System.err.println("[PatternPreprocessor] - pluginName: " + info.getPluginName());
        System.err.println("[PatternPreprocessor] - parameters: ");

        for (Map.Entry<String, String> entry : info.getPluginParameters().entrySet()) {
            System.err.println("[PatternPreprocessor]  - " + entry.getKey() + ": " + entry.getValue());
        }

        currentParser = null;
    }

    public static boolean inPatternDefinition() {
        return currentParser != null;
    }

    public static void parseHeader(List<String> t) {
        System.err.println("[PatternPreprocessor] parse header ...");

        if (!inPatternDefinition()) {
            throw new RuntimeException("[PatternPreprocessor] not in pattern definition");
        }

        currentParser.parseHeader(List.copyOf(t));
    }

    public static void parseBlockLine(List<String> t) {
        System.err.println("[PatternPreprocessor] parse block line ...");

        if (!inPatternDefinition()) {
            throw new RuntimeException("[PatternPreprocessor] not in pattern definition");
        }

        currentParser.parseBlockLine(List.copyOf(t));
    }
}
