package io.github.nifacy.c4patterns.syntax.plugin;

import java.lang.instrument.Instrumentation;

public class PatternSyntaxPlugin {

    public static void premain(String agentArgs, Instrumentation inst) {
        try {
            Class<?> aspectjAgent = Class.forName("org.aspectj.weaver.loadtime.Agent");
            java.lang.reflect.Method premainMethod = aspectjAgent
                .getMethod(
                    "premain",
                    String.class,
                    Instrumentation.class
                );
            premainMethod.invoke(null, agentArgs, inst);
        } catch (Exception e) {
            System.err.println("Failed to initialize AspectJ weaver: " + e.getMessage());
            e.printStackTrace();
        }
    }

    public static void agentmain(String agentArgs, Instrumentation inst) {
        premain(agentArgs, inst);
    }
}
