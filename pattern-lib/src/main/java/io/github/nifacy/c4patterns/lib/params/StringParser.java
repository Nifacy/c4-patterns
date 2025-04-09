package io.github.nifacy.c4patterns.lib.params;

import java.util.function.Function;

public class StringParser implements Parser<String> {

    @Override
    public String parse(String prefix, Function<String, String> parameterGetter) throws ParseError {
        String value = parameterGetter.apply(prefix);

        if (value == null) {
            throw new ExpectedNotNull(prefix);
        }

        return value;
    }
}
