package io.github.nifacy.c4patterns.lib;

import java.lang.reflect.ParameterizedType;
import java.lang.reflect.Type;
import java.util.Optional;

import io.github.nifacy.c4patterns.lib.params.ParseError;
import io.github.nifacy.c4patterns.lib.params.Parser;
import io.github.nifacy.c4patterns.lib.params.ParserFactory;
import io.github.nifacy.c4patterns.lib.params.Schema;
import com.structurizr.dsl.StructurizrDslPlugin;
import com.structurizr.dsl.StructurizrDslPluginContext;

public abstract class Pattern<T extends Schema> implements StructurizrDslPlugin {

    public static Optional<String> getDocumentation() {
        return Optional.empty();
    }

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

    protected abstract void apply(StructurizrDslPluginContext context, T arguments);
}
