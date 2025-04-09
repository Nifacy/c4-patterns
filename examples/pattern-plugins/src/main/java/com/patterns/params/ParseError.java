package com.patterns.params;

public class ParseError extends Exception {

    public ParseError(String message) {
        super("Error raised during parse:\n" + message);
    }
}
