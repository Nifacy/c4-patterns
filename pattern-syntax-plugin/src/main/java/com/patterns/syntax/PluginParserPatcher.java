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

        CtClass pluginDslContextType = cp.get("com.structurizr.dsl.PluginDslContext");
        CtClass tokensType = cp.get("com.structurizr.dsl.Tokens");
        CtMethod parseParamsMethod = ctClass.getDeclaredMethod("parseParameter", new CtClass[] { pluginDslContextType, tokensType });

        parseParamsMethod.insertBefore("""
            if (context.patternParser != null) {
                context.patternParser.parseBlockLine(com.patterns.syntax.PatchUtils.toTokenList(tokens));
                return;
            }
        """);

        return ctClass.toBytecode();
    }

    @Override
    public String getTargetClassName() {
        return "com/structurizr/dsl/PluginParser";
    }
}
