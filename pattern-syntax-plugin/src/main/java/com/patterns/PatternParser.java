package com.patterns;

import com.structurizr.dsl.StructurizrDslParser;

import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;

public class PatternParser {
    private final static String PATTERN_LANGUAGE_NAME_PREFIX = "pattern:";
    private static String langName = null;

    public static boolean isPatternLanguageSpecified(String language) {
        return language.startsWith(PATTERN_LANGUAGE_NAME_PREFIX);
    }

    public static void setLangName(String name) {
        langName = name;
    }

    public static void run(PatternParserContext context, String language, List<List<String>> tokens) {
        System.out.println("[PatternParser] running pattern:");
        System.out.println("- name: " + langName);
        System.out.println("- context:");
        System.out.println("  - parser:" + context.getDslParser());
        System.out.println("  - workspace:" + context.getDslWorkspace());
        System.out.println("  - dsl file:" + context.getDslFile());
        System.out.println("- tokens: ");
        for (List<String> lineTokens : tokens) {
            System.out.print("[");
            for (String token : lineTokens) {
                System.out.print(token + ", ");
            }
            System.out.println("]");
        }

        PatternBuilder builder = new PatternBuilder(
                getPatternName(langName),
                context.getDslFile(),
                context.getDslParser(),
                context.getDslWorkspace()
        );

        for (List<String> pair : tokens) {
            builder.addParameter(pair.get(0), pair.get(1));
        }

        builder.run();
    }

    public static StructurizrDslParser getDslParser(Object scriptContext) throws Exception {
        Class<?> scriptContextClass = scriptContext.getClass();
        Field dslParserField = findField(scriptContextClass, "dslParser");

        dslParserField.setAccessible(true);
        return (StructurizrDslParser) dslParserField.get(scriptContext);
    }

    private static String getPatternName(String languageName) {
        if (!isPatternLanguageSpecified(languageName)) {
            throw new IllegalArgumentException("'" + languageName + "' is not a pattern call");
        }

        return languageName.replaceFirst("^" + PATTERN_LANGUAGE_NAME_PREFIX, "");
    }

    private static Field findField(Class<?> clazz, String fieldName) {
        Class<?> current = clazz;

        while (current != null) {
            try {
                return current.getDeclaredField(fieldName);
            } catch (NoSuchFieldException e) {
                current = current.getSuperclass();
            }
        }

        throw new RuntimeException("Can't find field " + fieldName);
    }

    public static List<List<String>> tokenize(List<String> lines, Object tokenizer) throws Exception {
        Method tokenizeMethod = tokenizer.getClass().getDeclaredMethod("tokenize", String.class);
        tokenizeMethod.setAccessible(true);
        List<List<String>> tokens = new ArrayList<>();

        for (String line : lines) {
            tokens.add((List<String>) tokenizeMethod.invoke(tokenizer, line));
        }

        return tokens;
    }
}
