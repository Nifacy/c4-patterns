package com.patterns;

import java.lang.instrument.ClassFileTransformer;
import java.lang.instrument.IllegalClassFormatException;
import java.lang.instrument.Instrumentation;
import java.security.ProtectionDomain;

import javassist.*;


public class PatternSyntaxPlugin {
    public static void premain(String args, Instrumentation inst) {
        inst.addTransformer(new StructurizrTransformer());
    }

    static class StructurizrTransformer implements ClassFileTransformer {

        @Override
        public byte[] transform(
                Module module,
                ClassLoader loader,
                String className,
                Class<?> classBeingRedefined,
                ProtectionDomain protectionDomain,
                byte[] classfileBuffer
        ) throws IllegalClassFormatException {

            if (className.equals("com/structurizr/dsl/ScriptParser")) {
                try {
                    ClassPool cp = ClassPool.getDefault();
                    CtClass ctClass = cp.makeClass(new java.io.ByteArrayInputStream(classfileBuffer));

                    CtClass tokensType = cp.get("com.structurizr.dsl.Tokens");
                    CtMethod method = ctClass.getDeclaredMethod("isInlineScript", new CtClass[] { tokensType });

                    method.insertBefore("""
                        if (
                            com.structurizr.dsl.DslContext.CONTEXT_START_TOKEN.equalsIgnoreCase(tokens.get(tokens.size()-1)) &&
                            tokens.includes(LANGUAGE_INDEX) &&
                            com.patterns.PatternParser.isPatternLanguageSpecified(tokens.get(LANGUAGE_INDEX))
                        ) {
                            System.out.println("[ScriptParser] pattern usage detected");
                            com.patterns.PatternParser.setLangName(tokens.get(LANGUAGE_INDEX));
                            return true;
                        }
                    """);

                    System.out.println("[StructurizrAgent] class '" + className + "' patched");
                    return ctClass.toBytecode();

                } catch (Exception e) {
                    e.printStackTrace();
                    throw new RuntimeException("Failed to transform ScriptParser", e);
                }
            }

            if (className.equals("com/structurizr/dsl/ScriptDslContext")) {
                try {
                    ClassPool cp = ClassPool.getDefault();
                    CtClass ctClass = cp.makeClass(new java.io.ByteArrayInputStream(classfileBuffer));
                    CtField parserField = ctClass.getDeclaredField("dslParser");

                    int updatedModifiers = (parserField.getModifiers() & ~Modifier.PRIVATE) | Modifier.PROTECTED;
                    parserField.setModifiers(updatedModifiers);

                    System.out.println("[StructurizrAgent] class '" + className + "' patched");
                    return ctClass.toBytecode();

                } catch (Exception e) {
                    e.printStackTrace();
                    throw new RuntimeException("Failed to transform InlineScriptDslContext", e);
                }
            }

            if (className.equals("com/structurizr/dsl/InlineScriptDslContext")) {
                try {
                    ClassPool cp = ClassPool.getDefault();
                    CtClass ctClass = cp.makeClass(new java.io.ByteArrayInputStream(classfileBuffer));
                    CtMethod method = ctClass.getDeclaredMethod("end");

                    method.insertBefore("""
                        if(com.patterns.PatternParser.isPatternLanguageSpecified(language)) {
                            com.patterns.PatternParser.run(
                                new com.patterns.PatternParserContext(
                                    com.patterns.PatternParser.getDslParser(this),
                                    dslFile,
                                    getWorkspace()
                                ),
                                language,
                                com.patterns.PatternParser.tokenize(lines, new com.structurizr.dsl.Tokenizer())
                            );
                            System.out.println("[InlineScriptDslContext] parse pattern ...");
                            return;
                        }
                    """);

                    System.out.println("[StructurizrAgent] class '" + className + "' patched");
                    return ctClass.toBytecode();

                } catch (Exception e) {
                    e.printStackTrace();
                    throw new RuntimeException("Failed to transform InlineScriptDslContext", e);
                }
            }

            return null;
        }
    }
}
