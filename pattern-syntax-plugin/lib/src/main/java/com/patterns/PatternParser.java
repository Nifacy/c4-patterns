package com.patterns;

import com.structurizr.dsl.CustomSyntaxEntityParser;
import com.structurizr.dsl.CustomSyntaxEntityParserContext;


class PatternParser implements CustomSyntaxEntityParser {

    private PatternBuilder builder;
    private final CustomSyntaxEntityParserContext context;

    PatternParser(CustomSyntaxEntityParserContext context) {
        // this.builder = new PatternBuilder();
        this.context = context;
        this.builder = null;
    }

    @Override
    public void parseHeader(String[] tokens) {
        if (tokens.length > 2) {
            throw new RuntimeException("Too many tokens, expected: $pattern <pattern-name>");
        }

        if (tokens.length < 2) {
            throw new RuntimeException("Expected: $pattern <pattern-name>");
        }

        this.builder = new PatternBuilder(
            tokens[1],
            this.context.getDslFile(),
            this.context.getDslParser(),
            this.context.getWorkspace()
        );
    }

    @Override
    public void parseBlockLine(String[] tokens) {
        System.err.println("[PatternParser] [log] parse parameter ...");

        if (tokens.length > 2) {
            throw new RuntimeException("Too many tokens, expected: <name> <value>");
        }

        if (tokens.length < 2) {
            throw new RuntimeException("Expected: <name> <value>");
        }

        String name = tokens[0];
        String value = tokens[1];

        this.builder.addParameter(name, value);
    }

    @Override
    public void onEnd() {
        this.builder.run();
    }

    // private static final String GRAMMAR = "pattern <pattern-name>";

    // private static final int PATTERN_NAME_INDEX = 1;

    // private final static int PARAMETER_NAME_INDEX = 0;
    // private final static int PARAMETER_VALUE_INDEX = 1;

    // void parseParameter(PatternDslContext context, Tokens tokens) {
    //     // <name> <value>

    //     System.err.println("[PatternParser] [log] parse parameter ...");

    //     if (tokens.hasMoreThan(PARAMETER_VALUE_INDEX)) {
    //         throw new RuntimeException("Too many tokens, expected: <name> <value>");
    //     }

    //     if (tokens.size() != 2) {
    //         throw new RuntimeException("Expected: <name> <value>");
    //     }

    //     String name = tokens.get(PARAMETER_NAME_INDEX);
    //     String value = tokens.get(PARAMETER_VALUE_INDEX);

    //     context.addParameter(name, value);
    // }

}