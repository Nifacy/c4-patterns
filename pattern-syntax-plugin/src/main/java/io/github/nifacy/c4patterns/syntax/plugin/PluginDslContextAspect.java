package io.github.nifacy.c4patterns.syntax.plugin;

import io.github.nifacy.c4patterns.syntax.parser.PatternParser;
import io.github.nifacy.c4patterns.syntax.parser.PluginCallInfo;
import org.aspectj.lang.annotation.After;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Before;
import org.aspectj.lang.annotation.DeclareParents;

import java.lang.reflect.Field;

@Aspect
public class PluginDslContextAspect {
    public interface PatternParserField {
        PatternParser getPatternParser();

        void setPatternParser(PatternParser parser);
    }

    public static class PatternParserFieldImpl implements PatternParserField {
        private PatternParser patternParser;

        @Override
        public PatternParser getPatternParser() {
            return patternParser;
        }

        @Override
        public void setPatternParser(PatternParser patternParser) {
            this.patternParser = patternParser;
        }
    }

    @DeclareParents(
        value = "com.structurizr.dsl.PluginDslContext+", defaultImpl = PatternParserFieldImpl.class
    )
    public static PatternParserField patternParser;

    @After(
        """
                execution(com.structurizr.dsl.PluginDslContext.new(..))
                && this(ctx)
                && execution(*.new(..))
            """
    )
    public void afterConstructor(Object ctx) throws Throwable {
        PatternParser parser = ((PatternParserField) ctx).getPatternParser();

        Field fqnField = ctx.getClass().getDeclaredField("fullyQualifiedClassName");
        fqnField.setAccessible(true);
        String fullyQualifiedClassName = (String) fqnField.get(ctx);

        if (parser == null && PatternCallWrapper.isWrappedPluginName(fullyQualifiedClassName)) {
            PatternParser newParser = new PatternParser();
            newParser.parseHeader(PatternCallWrapper.unwrapFromPluginName(fullyQualifiedClassName));
            ((PatternParserField) ctx).setPatternParser(newParser);
        }
    }

    @Before(
        """
                execution(* com.structurizr.dsl.PluginDslContext.end(..))
                && this(ctx)
            """
    )
    public void beforeEnd(Object ctx) throws Throwable {
        PatternParser parser = ((PatternParserField) ctx).getPatternParser();

        if (parser == null) {
            return;
        }

        PluginCallInfo info = parser.getPluginCallInfo();

        Field fqnField = ctx.getClass().getDeclaredField("fullyQualifiedClassName");
        fqnField.setAccessible(true);
        fqnField.set(ctx, info.getName());

        Field paramsField = ctx.getClass().getDeclaredField("parameters");
        paramsField.setAccessible(true);
        paramsField.set(ctx, info.getParameters());
    }
}
