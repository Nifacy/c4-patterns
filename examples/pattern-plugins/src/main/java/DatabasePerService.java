import com.structurizr.dsl.IdentifiersRegister;
import com.structurizr.dsl.StructurizrDslParser;
import com.structurizr.dsl.StructurizrDslPluginContext;
import com.structurizr.model.Container;
import com.structurizr.model.Element;
import com.structurizr.model.Model;
import com.structurizr.model.Relationship;
import io.github.nifacy.c4patterns.lib.Pattern;
import io.github.nifacy.c4patterns.lib.params.Schema;

import java.util.Optional;

public class DatabasePerService extends Pattern<DatabasePerService.Arguments> {

    public static Optional<String> getDocumentation() {

        String builder = "### Database per service\n" +
                "Паттерн используется в контексте микросервисной архитектуры.\n" +
                "Согласно этому паттерну, каждый сервис имеет свою базу данных.\n" +
                "Такой подход позволяет горизонтально масштабировать сервисы независимо друг от друга,\n" +
                "делать сами базы данных независимыми (например, каждый сервис может использую такую базу данных,\n" +
                "которая будет более подходящей для его задачи).\n";

        return Optional.of(builder);
    }

    @Override
    protected void apply(StructurizrDslPluginContext context, Arguments arguments) {
        System.out.println("[log] [db per service] Script started");

        StructurizrDslParser dslParser = context.getDslParser();
        IdentifiersRegister identifiersRegister = dslParser.getIdentifiersRegister();

        /* Main */
        String serviceId = arguments.service;
        Container serviceContainer = (Container) findElement(identifiersRegister, serviceId);

        String databaseId = arguments.database;
        Container databaseContainer = (Container) findElement(identifiersRegister, databaseId);

        Optional<String> dataDescriptionValue = arguments.dataDescription;
        String dataDescription = dataDescriptionValue.orElse("data");

        Model model = serviceContainer.getModel();

        for (Relationship relationship : model.getRelationships()) {
            if (relationship.getDestination() == databaseContainer) {
                if (relationship.getSource() != serviceContainer) {
                    String sourceName = relationship.getSource().getName();
                    String dbName = databaseContainer.getName();

                    throw new java.lang.RuntimeException(
                            "[error] [db per service] Database '" + dbName
                                    + "' is already used by '" + sourceName + "'"
                    );
                }
            }
        }

        // Add relationship
        serviceContainer.uses(databaseContainer, "Reads & writes " + dataDescription);

        // Add in group
        String groupName = serviceContainer.getName() + " with database";
        serviceContainer.setGroup(groupName);
        databaseContainer.setGroup(groupName);
    }

    private Element findElement(IdentifiersRegister identifiersRegister, String elementId) {
        Element foundElement = identifiersRegister.getElement(elementId);
        if (foundElement == null) {
            throw new java.lang.RuntimeException("[error] [db per service] element with id '" + elementId + "' not found");
        }
        return foundElement;
    }

    public static class Arguments implements Schema {

        public String service;
        public String database;
        public Optional<String> dataDescription;
    }
}
