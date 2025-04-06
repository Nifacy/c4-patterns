import java.util.Optional;

import io.github.nifacy.c4patterns.lib.params.Schema;
import io.github.nifacy.c4patterns.lib.Pattern;
import com.structurizr.dsl.IdentifiersRegister;
import com.structurizr.dsl.StructurizrDslParser;
import com.structurizr.dsl.StructurizrDslPluginContext;
import com.structurizr.model.Container;
import com.structurizr.model.Element;
import com.structurizr.model.Model;
import com.structurizr.model.Relationship;

public class DatabasePerService extends Pattern<DatabasePerService.Arguments> {

    public static class Arguments implements Schema {

        public String service;
        public String database;
        public Optional<String> dataDescription;
    }

    public static Optional<String> getDocumentation() {
        StringBuilder builder = new StringBuilder();

        builder.append("### Database per service\n");
        builder.append("Паттерн используется в контексте микросервисной архитектуры.\n");
        builder.append("Согласно этому паттерну, каждый сервис имеет свою базу данных.\n");
        builder.append("Такой подход позволяет горизонтально масштабировать сервисы независимо друг от друга,\n");
        builder.append("делать сами базы данных независимыми (например, каждый сервис может использую такую базу данных,\n");
        builder.append("которая будет более подходящей для его задачи).\n");

        return Optional.of(builder.toString());
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
}
