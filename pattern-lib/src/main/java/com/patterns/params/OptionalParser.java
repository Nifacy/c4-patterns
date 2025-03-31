package com.patterns.params;

import java.util.Optional;
import java.util.function.Function;

public class OptionalParser<T> implements Parser<Optional<T>> {

    private final Parser<T> elementParser;

    public OptionalParser(Parser<T> elementParser) {
        this.elementParser = elementParser;
    }

    @Override
    public Optional<T> parse(String prefix, Function<String, String> parameterGetter) throws ParseError {
        try {
            T value = this.elementParser.parse(prefix, parameterGetter);
            return Optional.of(value);
        } catch (ExpectedNotNull e) {
            return Optional.empty();
        }
    }
}
