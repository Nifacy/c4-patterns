package com.patterns;

import java.io.File;
import java.lang.reflect.InvocationTargetException;
import java.net.URL;
import java.net.URLClassLoader;
import java.util.HashMap;
import java.util.Map;

import com.structurizr.Workspace;
import com.structurizr.dsl.StructurizrDslParser;
import com.structurizr.dsl.StructurizrDslPlugin;
import com.structurizr.dsl.StructurizrDslPluginContext;


class PluginIsNotPattern extends Exception {
    PluginIsNotPattern(String patternName) {
        super("class '" + patternName + "' is not a pattern");
    }
}


class PatternNotFound extends Exception {
    PatternNotFound(String patternName) {
        super("pattern by name '" + patternName + "' not found");
    }
}


class PatternsNotSupported extends Exception {
    PatternsNotSupported() {
        super("patterns not supported");
    }
}


class PatternBuilder {

    private static final String PLUGINS_DIRECTORY_NAME = "plugins";

    private final String patternName;
    private final File dslFile;
    private final StructurizrDslParser dslParser;
    private final Workspace dslWorkspace;
    private final Map<String, String> parameters;

    PatternBuilder(String patternName, File dslFile, StructurizrDslParser dslParser, Workspace dslWorkspace) {
        this.patternName = patternName;
        this.dslFile = dslFile;
        this.dslParser = dslParser;
        this.dslWorkspace = dslWorkspace;
        this.parameters = new HashMap<>();

        System.err.println("[PatternContext] [log] initialized");
    }

    public void addParameter(String name, String value) {
        parameters.put(name, value);
        System.err.println("[PatternContext] [log] (" + this.patternName + ") added parameter:");
        System.err.println("[PatternContext] [log] (" + this.patternName + ") - name: " + name);
        System.err.println("[PatternContext] [log] (" + this.patternName + ") - value: " + value);
    }

    public void run() {
        try {
            URLClassLoader loader = getClassLoader(dslFile);
            Class patternClass = loadPatternClass(loader);
            runPattern(patternClass);
        } catch (PluginIsNotPattern e) {
            throw new RuntimeException("[patterns] " + e.getMessage());
        } catch (Exception e) {
            e.printStackTrace();
            throw new RuntimeException("[patterns] Error running pattern " + patternName + ", caused by " + e.getClass().getName() + ": " + e.getMessage());
        }
    }

    protected URLClassLoader getClassLoader(File dslFile) throws Exception {
        File pluginsDirectory = new File(dslFile.getParent(), PLUGINS_DIRECTORY_NAME);
        URL[] urls = new URL[0];

        if (pluginsDirectory.exists()) {
            File[] jarFiles = pluginsDirectory.listFiles((dir, name) -> name.endsWith(".jar"));
            if (jarFiles != null) {
                urls = new URL[jarFiles.length];
                for (int i = 0; i < jarFiles.length; i++) {
                    urls[i] = jarFiles[i].toURI().toURL();
                }
            }
        }

        return new URLClassLoader(urls, getClass().getClassLoader());
    }

    private boolean isPattern(Class patternClass, Class patternBaseClass) {
        return patternBaseClass.isAssignableFrom(patternClass);
    }

    private Class loadBasePatternClass(URLClassLoader loader) throws PatternsNotSupported {
        try {
            return loader.loadClass("com.patterns.Pattern");
        } catch (ClassNotFoundException e) {
            throw new PatternsNotSupported();
        }
    }

    private Class loadPatternClass(URLClassLoader loader) throws PatternsNotSupported, PluginIsNotPattern, PatternNotFound {
        try {
            Class patternClass = loader.loadClass(patternName);
            Class basePatternClass = loadBasePatternClass(loader);

            if (!isPattern(patternClass, basePatternClass)) {
                throw new PluginIsNotPattern(patternName);
            }

            return patternClass;

        } catch (ClassNotFoundException e) {
            throw new PatternNotFound(patternName);
        }
    }

    private void runPattern(Class patternClass) throws NoSuchMethodException, InstantiationException, IllegalAccessException, InvocationTargetException {
        StructurizrDslPlugin patternInstance = (StructurizrDslPlugin) patternClass.getDeclaredConstructor().newInstance();
        StructurizrDslPluginContext pluginContext = new StructurizrDslPluginContext(
            dslParser,
            dslFile,
            dslWorkspace,
            parameters
        );

        patternInstance.run(pluginContext);
    }

}
