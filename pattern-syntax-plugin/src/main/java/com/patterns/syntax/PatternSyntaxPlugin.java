package com.patterns.syntax;

import java.lang.instrument.ClassFileTransformer;
import java.lang.instrument.Instrumentation;
import java.security.ProtectionDomain;
import java.util.List;


public class PatternSyntaxPlugin {
    public static void premain(String args, Instrumentation inst) {
        inst.addTransformer(new StructurizrTransformer());
    }

    static class StructurizrTransformer implements ClassFileTransformer {

        private static final List<ClassPatcher> patchers = List.of(
                new TokenizerPatcher()
        );

        @Override
        public byte[] transform(
                Module module,
                ClassLoader loader,
                String className,
                Class<?> classBeingRedefined,
                ProtectionDomain protectionDomain,
                byte[] classfileBuffer
        ) {
            try {
                for (ClassPatcher patcher : patchers) {
                    if (className.equals(patcher.getTargetClassName())) {
                        byte[] result = patcher.patchClass(
                                module,
                                loader,
                                className,
                                classBeingRedefined,
                                protectionDomain,
                                classfileBuffer
                        );

                        System.err.println("[PatternSyntaxPlugin] class '" + className + "' patched");
                        return result;
                    }
                }
            } catch(Exception e) {
                e.printStackTrace();
                throw new RuntimeException("Failed to patch '" + className + "'", e);
            }

            return null;
        }
    }
}
