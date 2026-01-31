package io.github.nifacy.c4patterns.syntax.plugin.aspects;

import io.github.nifacy.c4patterns.syntax.parser.PatternParser;
import io.github.nifacy.c4patterns.syntax.plugin.PatchUtils;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;

@Aspect
public class PluginParserAspect {
    @Around(
        """
                execution(
                    * com.structurizr.dsl.PluginParser.parseParameter(
                        com.structurizr.dsl.PluginDslContext,
                        com.structurizr.dsl.Tokens
                    )
                )
                && args(context, tokens)
            """
    )
    public void aroundParseParameter(
        ProceedingJoinPoint pjp,
        Object context,
        Object tokens
    )
        throws Throwable {
        PatternParser patternParser = ((PatternParserHolder) context).getPatternParser();
        if (patternParser != null) {
            patternParser.parseBlockLine(PatchUtils.toTokenList(tokens));
        } else {
            pjp.proceed();
        }
    }

}
