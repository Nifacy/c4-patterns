package io.github.nifacy.c4patterns.syntax.plugin;

import java.security.ProtectionDomain;

interface ClassPatcher {
    byte[] patchClass(
        Module module,
        ClassLoader loader,
        String className,
        Class<?> classBeingRedefined,
        ProtectionDomain protectionDomain,
        byte[] classfileBuffer
    )
        throws Exception;

    String getTargetClassName();
}
