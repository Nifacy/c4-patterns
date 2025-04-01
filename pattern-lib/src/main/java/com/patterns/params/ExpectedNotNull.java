package com.patterns.params;

public class ExpectedNotNull extends ParseError {

    public ExpectedNotNull(String key) {
        super("Required field '" + key + "' not specified");
    }
}
