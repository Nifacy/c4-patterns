import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;

import io.github.nifacy.c4patterns.lib.params.Schema;
import io.github.nifacy.c4patterns.lib.Pattern;
import com.structurizr.dsl.IdentifiersRegister;
import com.structurizr.dsl.StructurizrDslParser;
import com.structurizr.dsl.StructurizrDslPluginContext;
import com.structurizr.model.Container;
import com.structurizr.model.Element;

public class ServiceRegistry extends Pattern<ServiceRegistry.Arguments> {

    public static class ArgumentQueryItem implements Schema {

        public String source;
        public String destination;
    }

    public static class Arguments implements Schema {

        public String registry;
        public String connectedServices;
        public List<ArgumentQueryItem> query;
    }

    private class RegistryQuery {

        public String sourceId;
        public String destinationId;

        public RegistryQuery(String sourceId, String destinationId) {
            this.sourceId = sourceId;
            this.destinationId = destinationId;
        }
    }

    public static Optional<String> getDocumentation() {
        StringBuilder builder = new StringBuilder();

        builder.append("### Saga\n");
        builder.append("\n");
        builder.append("#### Проблема\n");
        builder.append("Микросервисной архитектуре свойствена работа с огромным количеством сервисов и их реплик.\n");
        builder.append("При использовании таких протоколов, как HTTP, необходимо знать \"местоположение\" сервиса\n");
        builder.append("(в данном случае это IP и порт), которому необходимо отправлять запрос.\n");
        builder.append("\n");
        builder.append("Однако, в микросервисной архитектуре сервисы постоянно создаются, удаляются, могут упасть и т. д. То есть, набор сервисов динамичный и изменяется с течением времени.\n");
        builder.append("\n");
        builder.append("#### Решение\n");
        builder.append("Данный паттерн предлагает сделать отдельную сущность - Service Registry,\n");
        builder.append("которая будет играть роль хранилища информации об активных сервисах.\n");
        builder.append("При старте работы сервисы отправляют запрос в Service Registry на добавление.\n");
        builder.append("После чего, Service Registry может отправлять запросы на проверку работоспособности сервисов,\n");
        builder.append("например, используя паттерн Healtcheck API.\n");
        builder.append("Либо же сервисы сами могут отсылать запрос, чтобы уведомить Registry о том, что они работоспособны.\n");

        return Optional.of(builder.toString());
    }

    @Override
    protected void apply(StructurizrDslPluginContext context, Arguments arguments) {
        System.out.println("[log] [service registry] Script started");

        StructurizrDslParser dslParser = context.getDslParser();
        IdentifiersRegister identifiersRegister = dslParser.getIdentifiersRegister();

        /* Parse Parameters */
        String registryId = arguments.registry;
        String connectedServicesIds = arguments.connectedServices;

        List<RegistryQuery> queries = new ArrayList<>();
        for (ArgumentQueryItem queryArg : arguments.query) {
            queries.add(new RegistryQuery(queryArg.source, queryArg.destination));
        }

        /* Find Elements */
        HashMap<String, Container> _connectedServices = new HashMap<>();
        Container _registryService = (Container) findElement(identifiersRegister, registryId);

        for (String connectedServiceId : connectedServicesIds.split(",")) {
            Container connectedService = (Container) findElement(identifiersRegister, connectedServiceId);
            if (_connectedServices.containsKey(connectedServiceId)) {
                throw new java.lang.RuntimeException("Id '" + connectedServiceId + "' is not unique");
            }

            _connectedServices.put(connectedServiceId, connectedService);
        }

        /* Add Relationships */
        for (RegistryQuery query : queries) {
            Container sourceService = (Container) findElement(identifiersRegister, query.sourceId);

            Container destinationService = _connectedServices.get(query.destinationId);
            if (destinationService == null) {
                throw new java.lang.RuntimeException("Element with id '" + query.destinationId + "' not found");
            }

            sourceService.uses(
                    _registryService,
                    "Requests location of ${destinationService.getName()}"
            );
        }

        for (Container connectedService : _connectedServices.values()) {
            connectedService.uses(_registryService, "Registers itself in registry");
        }

        /* Print parsed data */
        System.out.println("[log] [service registry] Connected services: " + _connectedServices);
        System.out.println("[log] [service registry] Script ended");
    }

    private Element findElement(IdentifiersRegister identifiersRegister, String elementId) {
        Element foundElement = identifiersRegister.getElement(elementId);
        if (foundElement == null) {
            throw new java.lang.RuntimeException("[error] [db per service] element with id '" + elementId + "' not found");
        }
        return foundElement;
    }
}
