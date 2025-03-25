package com.patterns.syntax;

import javassist.ClassPool;
import javassist.CtClass;
import javassist.CtMethod;

import java.security.ProtectionDomain;

class StructurizrDslParserPatcher implements ClassPatcher {
    private static final String TARGET_CLASS_NAME = "com/structurizr/dsl/StructurizrDslParser";

    @Override
    public byte[] patchClass(Module module, ClassLoader loader, String className, Class<?> classBeingRedefined, ProtectionDomain protectionDomain, byte[] classfileBuffer) throws Exception {
        ClassPool cp = ClassPool.getDefault();
        CtClass ctClass = cp.makeClass(new java.io.ByteArrayInputStream(classfileBuffer));
        CtClass tokensType = cp.get("java.util.List");
        CtMethod method = ctClass.getDeclaredMethod("preProcessLines", new CtClass[] { tokensType });

        method.insertBefore("""
            lines = com.patterns.syntax.PatternPreprocessor.preProcessLines(lines);
        """);

        return ctClass.toBytecode();
    }

    @Override
    public String getTargetClassName() {
        return TARGET_CLASS_NAME;
    }
}
