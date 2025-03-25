package com.patterns.syntax;

import java.util.ArrayList;
import java.util.List;

public class PatternPreprocessor {
    public static List<String> preProcessLines(List<String> lines) {
        List<String> result = new ArrayList<>();

        for (String line : lines) {
            result.add(line.replace("$pattern", "!plugin"));
        }

        return result;
    }
}
