package io.github.nifacy.c4patterns.lib.params;

public class ParseError extends Exception {

    public ParseError(String message) {
        super("Error raised during parse:\n" + message);
    }
}
