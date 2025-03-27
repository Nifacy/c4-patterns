package com.patterns.syntax;

import javassist.ClassPool;
import javassist.CtClass;
import javassist.CtMethod;

import java.security.ProtectionDomain;

public class PluginParserPatcher implements ClassPatcher {

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

        CtClass dslContextType = cp.get("com.structurizr.dsl.DslContext");
        CtClass pluginDslContextType = cp.get("com.structurizr.dsl.PluginDslContext");
        CtClass tokensType = cp.get("com.structurizr.dsl.Tokens");

        CtMethod parseMethod = ctClass.getDeclaredMethod("parse", new CtClass[] { dslContextType, tokensType });
        parseMethod.insertBefore("""
            System.out.println("[PluginParserPatcher] parsed tokens: " + com.patterns.syntax.PatternPreprocessor.getLastTokens());
            System.out.println("[PluginParserPatcher] in pattern definition: " + com.patterns.syntax.PatternPreprocessor.inPatternDefinition());
            if (com.patterns.syntax.PatternPreprocessor.inPatternDefinition()) {
                com.patterns.syntax.PatternPreprocessor.parseHeader(com.patterns.syntax.PatternPreprocessor.getLastTokens());
            }
        """);

        CtMethod parseParamsMethod = ctClass.getDeclaredMethod("parseParameter", new CtClass[] { pluginDslContextType, tokensType });
        parseParamsMethod.insertBefore("""
            if (context.patternParser != null) {
                System.out.println("[GRISHIN] Test");
                context.patternParser.parseBlockLine(com.patterns.syntax.PatchUtils.toTokenList(tokens));
            }

            if (com.patterns.syntax.PatternPreprocessor.inPatternDefinition()) {
                System.out.println("[PluginParserPatcher] parsed tokens: " + com.patterns.syntax.PatternPreprocessor.getLastTokens());
                com.patterns.syntax.PatternPreprocessor.parseBlockLine(com.patterns.syntax.PatternPreprocessor.getLastTokens());
            }
        """);

        return ctClass.toBytecode();
    }

    @Override
    public String getTargetClassName() {
        return "com/structurizr/dsl/PluginParser";
    }
}
