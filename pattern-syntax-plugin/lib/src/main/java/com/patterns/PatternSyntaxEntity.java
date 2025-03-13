package com.patterns;

import com.structurizr.dsl.CustomSyntaxEntity;
import com.structurizr.dsl.CustomSyntaxEntityParser;
import com.structurizr.dsl.CustomSyntaxEntityParserContext;


class PatternSyntaxEntity implements CustomSyntaxEntity {
    @Override
    public String getKeyword() {
        return "pattern";
    }

    @Override
    public CustomSyntaxEntityParser getParser(CustomSyntaxEntityParserContext context) {
        System.out.println("[MyActionSyntaxEntity] Context:");
        System.out.println(context.getWorkspace());
        System.out.println(context.getDslFile());
        System.out.println(context.getDslParser());

        return new PatternParser(context);
    }
}
