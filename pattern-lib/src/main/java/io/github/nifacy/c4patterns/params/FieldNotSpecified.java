package io.github.nifacy.c4patterns.params;

public class FieldNotSpecified extends ParseError {

    public FieldNotSpecified(String dictKey, String field) {
        super("Required field '" + field + "' for '" + dictKey + "' not specified");
    }
}
