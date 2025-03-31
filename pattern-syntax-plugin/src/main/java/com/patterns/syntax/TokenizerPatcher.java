package com.patterns.syntax;

import javassist.ClassPool;
import javassist.CtClass;
import javassist.CtMethod;

import java.security.ProtectionDomain;

class TokenizerPatcher implements ClassPatcher {
    private static final String TARGET_CLASS_NAME = "com/structurizr/dsl/Tokenizer";

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
        CtClass stringType = cp.get("java.lang.String");
        CtMethod method = ctClass.getDeclaredMethod("tokenize", new CtClass[] { stringType });

        method.insertAfter("""
            if (com.patterns.syntax.PatternCallWrapper.isPatternHeader($_)) {
                System.err.println("[PatternSyntaxPlugin] found pattern header: " + $_);
                $_ = com.patterns.syntax.PatternCallWrapper.wrapPatternHeader($_);
                System.err.println("[PatternSyntaxPlugin] wrapped pattern header: " + $_);
            }
        """);

        return ctClass.toBytecode();
    }

    @Override
    public String getTargetClassName() {
        return TARGET_CLASS_NAME;
    }
}
