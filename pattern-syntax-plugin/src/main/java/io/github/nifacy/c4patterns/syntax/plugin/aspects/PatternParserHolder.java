package io.github.nifacy.c4patterns.syntax.plugin.aspects;

import io.github.nifacy.c4patterns.syntax.parser.PatternParser;

public interface PatternParserHolder {
    PatternParser getPatternParser();

    void setPatternParser(PatternParser parser);
}
