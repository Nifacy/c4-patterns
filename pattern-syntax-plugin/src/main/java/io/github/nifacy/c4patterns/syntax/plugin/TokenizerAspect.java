package io.github.nifacy.c4patterns.syntax.plugin;

import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;
import org.aspectj.lang.annotation.Pointcut;

import java.util.List;

@Aspect
public class TokenizerAspect {
    @Pointcut("execution(* com.structurizr.dsl.Tokenizer.tokenize(String)) && args(input)")
    public void tokenizeMethod(String input) {
    }

    @Around("tokenizeMethod(input)")
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
