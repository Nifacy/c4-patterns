package io.github.nifacy.c4patterns.params;

import java.util.function.Function;

public class IntegerParser implements Parser<Integer> {

    @Override
    public Integer parse(String prefix, Function<String, String> parameterGetter) throws ParseError {
        String value = parameterGetter.apply(prefix);

        if (value == null) {
            throw new ExpectedNotNull(prefix);
        }

        return Integer.valueOf(value);
    }
}
