package com.patterns.syntax;

import javassist.*;

import java.security.ProtectionDomain;

public class StructurizrDslParserPatcher implements ClassPatcher {

    @Override
    public byte[] patchClass(
            Module module,
            ClassLoader loader,
            String className,
            Class<?> classBeingRedefined,
            ProtectionDomain protectionDomain,
            byte[] classfileBuffer
    ) throws Exception {
        ClassPool cp = ClassPool.getDefault();
        CtClass ctClass = cp.makeClass(new java.io.ByteArrayInputStream(classfileBuffer));

        CtClass listType = cp.get("java.util.List");
        CtClass fileType = cp.get("java.io.File");
        CtClass boolType = cp.get("boolean");
        CtClass patternParserType = cp.get("com.patterns.syntax.parser.PatternParser");

        CtField parserField = new CtField(patternParserType, "patternParser", ctClass);
        parserField.setModifiers(Modifier.PUBLIC);
        ctClass.addField(parserField);

        CtMethod parseMethod = ctClass.getDeclaredMethod("parse", new CtClass[]{ listType, fileType, boolType, boolType });
        // void parse(List<String> lines, File dslFile, boolean fragment, boolean includeInDslSourceLines)

        parseMethod.insertBefore("""
            System.out.println("[GRISHIN] parse ...");
            System.out.println(patternParser);
        """);

        return ctClass.toBytecode();
    }

    @Override
    public String getTargetClassName() {
        return "com/structurizr/dsl/StructurizrDslParser";
    }
}
