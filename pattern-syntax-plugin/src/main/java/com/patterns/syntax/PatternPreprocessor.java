package com.patterns.syntax;

import java.util.ArrayList;
import java.util.List;

public class PatternPreprocessor {
    public static List<String> preProcessTokens(List<String> tokens) {
        System.out.println("[PatternPreprocessor] preproces ...");

        List<String> result = new ArrayList<>();

        for (int index = 0; index < tokens.size(); index++) {
            String token = tokens.get(index);
            if (index == 0 && token.equals("$pattern")) {
                token = "!plugin";
            }
            result.add(token);
        }

        return result;
    }
}
