package io.github.nifacy.c4patterns.params;

import java.util.ArrayList;
import java.util.List;
import java.util.function.Function;

public class ListParser<T> implements Parser<List<T>> {

    private final Parser<T> elementParser;

    public ListParser(Parser<T> elementParser) {
        if (elementParser instanceof OptionalParser) {
            throw new IllegalArgumentException("Elements of ListParser can't be optional");
        }

        this.elementParser = elementParser;
    }

    @Override
    public List<T> parse(String prefix, Function<String, String> parameterGetter) throws ParseError {
        List<T> items = new ArrayList<>();
        int index = 0;

        try {
            while (true) {
                String elementPrefix = prefix + "." + index;
                T item = this.elementParser.parse(elementPrefix, parameterGetter);

                items.add(item);
                index++;
            }
        } catch (ExpectedNotNull e) {
        }

        return items;
    }
}
