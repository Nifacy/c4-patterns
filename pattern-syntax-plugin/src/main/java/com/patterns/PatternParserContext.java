package com.patterns;

import com.structurizr.Workspace;
import com.structurizr.dsl.StructurizrDslParser;

import java.io.File;

public class PatternParserContext {
    private final StructurizrDslParser dslParser;
    private final File dslFile;
    private final Workspace dslWorkspace;

    public PatternParserContext(
        StructurizrDslParser dslParser,
        File dslFile,
        Workspace dslWorkspace
    ) {
        this.dslParser = dslParser;
        this.dslFile = dslFile;
        this.dslWorkspace = dslWorkspace;
    }

    public StructurizrDslParser getDslParser() {
        return this.dslParser;
    }

    public File getDslFile() {
        return this.dslFile;
    }

    public Workspace getDslWorkspace() {
        return this.dslWorkspace;
    }
}
