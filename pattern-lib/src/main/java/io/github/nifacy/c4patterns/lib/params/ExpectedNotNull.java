package io.github.nifacy.c4patterns.lib.params;

public class ExpectedNotNull extends ParseError {

    public ExpectedNotNull(String key) {
        super("Required field '" + key + "' not specified");
    }
}
