package com.patterns.lens.info;

import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.ParameterizedType;
import java.lang.reflect.Type;
import java.util.Optional;

class DocumentationGetter {

    public Optional<String> getDocumentation(Class<?> pluginClass) {
        try {
            Method method = pluginClass.getMethod("getDocumentation");
            Type returnType = method.getGenericReturnType();

            if (returnType instanceof ParameterizedType) {
                ParameterizedType parameterizedType = (ParameterizedType) returnType;
                Type rawType = parameterizedType.getRawType();
                Type elementType = parameterizedType.getActualTypeArguments()[0];

                if (rawType == Optional.class && elementType == String.class) {
                    return (Optional<String>) method.invoke(null);
                }
            }

            throw new IllegalArgumentException(
                    "Plugin class " + pluginClass.getName() + " broken: "
                    + "method 'getDocumentation' has invalid signature"
            );
        } catch (NoSuchMethodException | IllegalAccessException | InvocationTargetException e) {
            throw new IllegalArgumentException(
                    "Plugin class " + pluginClass.getName() + " broken: "
                    + e.getMessage()
            );
        }
    }
}
