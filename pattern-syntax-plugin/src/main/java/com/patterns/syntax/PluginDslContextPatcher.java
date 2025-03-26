package com.patterns.syntax;

import javassist.ClassPool;
import javassist.CtClass;
import javassist.CtMethod;

import java.security.ProtectionDomain;

public class PluginDslContextPatcher implements ClassPatcher {

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

        CtMethod parseMethod = ctClass.getDeclaredMethod("end");
        parseMethod.insertBefore("""
            if (com.patterns.syntax.PatternPreprocessor.inPatternDefinition()) {
                System.out.println("[PluginDslContextPatcher] pattern definition end");
                com.patterns.syntax.PatternPreprocessor.endPatternDefinition();
            }
        """);

        return ctClass.toBytecode();
    }

    @Override
    public String getTargetClassName() {
        return "com/structurizr/dsl/PluginDslContext";
    }
}
