package com.patterns;

import com.structurizr.dsl.StructurizrDslPlugin;
import com.structurizr.dsl.StructurizrDslPluginContext;


public class PatternSyntaxPlugin implements StructurizrDslPlugin {
    @Override
    public void run(StructurizrDslPluginContext context) {
        PatternSyntaxEntity entity = new PatternSyntaxEntity();
        context.getDslParser().addSyntaxEntity(entity);
    }
}
