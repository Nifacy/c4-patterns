package plugin;

import org.aspectj.lang.annotation.*;
import org.aspectj.lang.JoinPoint;

@Aspect
public class MyAspect {

    @After("execution(int app.App.Foo(int))")
    public void beforeTokenize() {
        System.out.println("Hello world");
    }
}
