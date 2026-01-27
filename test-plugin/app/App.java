package app;


public class App {
    public static int Foo(int x) {
        return x + 1;
    }

    public static void main(String[] args) {
        int x = Foo(2);

        System.out.println("x = " + x);
        System.out.println("end of program");
    }
}
