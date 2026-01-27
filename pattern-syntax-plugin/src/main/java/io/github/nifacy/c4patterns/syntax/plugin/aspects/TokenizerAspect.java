package io.github.nifacy.c4patterns.syntax.plugin.aspects;

import io.github.nifacy.c4patterns.syntax.plugin.PatternCallWrapper;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;

import java.util.List;

@Aspect
public class TokenizerAspect {
    @Around(
        """
                execution(* com.structurizr.dsl.Tokenizer.tokenize(String))
                && args(input)
            """
    )
    public Object aroundTokenizeMethod(ProceedingJoinPoint pjp, String input) throws Throwable {
        List<String> result = (List<String>) pjp.proceed();

        if (result != null && PatternCallWrapper.isPatternHeader(result)) {
            System.err.println("[PatternSyntaxPlugin] found pattern header: " + result);
            result = PatternCallWrapper.wrapPatternHeader(result);
            System.err.println("[PatternSyntaxPlugin] wrapped pattern header: " + result);
        }

        return result;
    }
}
