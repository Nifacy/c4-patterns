package io.github.nifacy.c4patterns;

import java.lang.reflect.ParameterizedType;
import java.lang.reflect.Type;
import java.util.Optional;

import io.github.nifacy.c4patterns.params.ParseError;
import io.github.nifacy.c4patterns.params.Parser;
import io.github.nifacy.c4patterns.params.ParserFactory;
import io.github.nifacy.c4patterns.params.Schema;
import com.structurizr.dsl.StructurizrDslPlugin;
import com.structurizr.dsl.StructurizrDslPluginContext;

public abstract class Pattern<T extends Schema> implements StructurizrDslPlugin {

    @Override
    public void run(StructurizrDslPluginContext context) {
        Class<?> childClass = this.getClass();

        System.out.println("[" + childClass.getName() + "] running pattern with schema ...");

        try {
            ParameterizedType superclass = (ParameterizedType) childClass.getGenericSuperclass();
            Type schemaType = superclass.getActualTypeArguments()[0];
            Parser<T> schemaParser = new ParserFactory().fromSchema((Class<T>) schemaType);
            T parsedArgs = schemaParser.parse("", name -> context.getParameter(name));
            apply(context, parsedArgs);
        } catch (ParseError e) {
            throw new RuntimeException("[" + childClass.getName() + "] Error during arguments parse:\n" + e);
        }
    }

    public static Optional<String> getDocumentation() {
        return Optional.empty();
    }

    protected abstract void apply(StructurizrDslPluginContext context, T arguments);
}
