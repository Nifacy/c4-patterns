package com.patterns.syntax;

import java.util.ArrayList;
import java.util.List;

public class PatternPreprocessor {
    private static final String PATTERN_KEYWORD = "$pattern";
    private static final String PLUGIN_KEYWORD = "!plugin";

    public static List<String> preProcessTokens(List<String> tokens) {
        List<String> result = new ArrayList<>();

        for (int index = 0; index < tokens.size(); index++) {
            String token = tokens.get(index);
            if (index == 0 && token.equals(PATTERN_KEYWORD)) {
                token = PLUGIN_KEYWORD;
            }
            result.add(token);
        }

        return result;
    }
}
