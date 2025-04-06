package io.github.nifacy.c4patterns.syntax.plugin;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;

public class PatchUtils {
    public static List<String> toTokenList(Object structurizrTokens) {
        List<String> tokens = new ArrayList<>();

        if (structurizrTokens == null) {
            throw new IllegalArgumentException("[PatchUtils] structurizr tokens can't be null");
        }

        try {
            Method sizeMethod = structurizrTokens.getClass().getDeclaredMethod("size");
            sizeMethod.setAccessible(true);

            Method getMethod = structurizrTokens.getClass().getDeclaredMethod("get", int.class);
            getMethod.setAccessible(true);

            int size = (Integer) sizeMethod.invoke(structurizrTokens);

            for (int i = 0; i < size; i++) {
                String token = (String) getMethod.invoke(structurizrTokens, i);
                tokens.add(token);
            }

        } catch (NoSuchMethodException | IllegalAccessException | InvocationTargetException e) {
            e.printStackTrace();
            throw new IllegalArgumentException("[PatchUtils] Invalid token container structure", e);
        }

        return tokens;
    }
}
