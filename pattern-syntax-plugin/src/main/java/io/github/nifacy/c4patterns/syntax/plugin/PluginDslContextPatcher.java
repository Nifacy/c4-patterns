package io.github.nifacy.c4patterns.syntax.plugin;

import javassist.*;

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
    )
        throws Exception {
        ClassPool cp = ClassPool.getDefault();
        CtClass ctClass = cp.makeClass(new java.io.ByteArrayInputStream(classfileBuffer));

        CtClass parserType = cp.get("io.github.nifacy.c4patterns.syntax.parser.PatternParser");
        CtField parserField = new CtField(parserType, "patternParser", ctClass);
        parserField.setModifiers(Modifier.PUBLIC);
        ctClass.addField(parserField);

        CtField classNameField = ctClass.getField("fullyQualifiedClassName");
        classNameField.setModifiers(Modifier.clear(classNameField.getModifiers(), Modifier.FINAL));

        CtField paramsField = ctClass.getField("parameters");
        paramsField.setModifiers(Modifier.clear(paramsField.getModifiers(), Modifier.FINAL));

        CtMethod parseMethod = ctClass.getDeclaredMethod("end");
        parseMethod.insertBefore("""
                if (patternParser != null) {
                    io.github.nifacy.c4patterns.syntax.parser.PluginCallInfo info = patternParser.getPluginCallInfo();

                    fullyQualifiedClassName = info.getName();
                    parameters = info.getParameters();
                }
            """);

        for (CtConstructor constructor : ctClass.getConstructors()) {
            constructor
                .insertAfter(
                    """
                            if (patternParser == null && io.github.nifacy.c4patterns.syntax.plugin.PatternCallWrapper.isWrappedPluginName(fullyQualifiedClassName)) {
                                patternParser = new io.github.nifacy.c4patterns.syntax.parser.PatternParser();
                                patternParser.parseHeader(io.github.nifacy.c4patterns.syntax.plugin.PatternCallWrapper.unwrapFromPluginName(fullyQualifiedClassName));
                            }
                        """
                );
        }

        return ctClass.toBytecode();
    }

    @Override
    public String getTargetClassName() {
        return "com/structurizr/dsl/PluginDslContext";
    }
}
