package io.github.nifacy.c4patterns.params;

import java.util.function.Function;

public interface Parser<T> {

    T parse(
            String prefix,
            Function<String, String> parameterGetter
    ) throws ParseError;
}
