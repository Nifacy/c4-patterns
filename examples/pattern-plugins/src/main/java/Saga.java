import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import io.github.nifacy.c4patterns.lib.params.Schema;
import io.github.nifacy.c4patterns.lib.Pattern;
import com.structurizr.dsl.IdentifiersRegister;
import com.structurizr.dsl.StructurizrDslParser;
import com.structurizr.dsl.StructurizrDslPluginContext;
import com.structurizr.model.Container;
import com.structurizr.model.Element;
import com.structurizr.view.AutomaticLayout;
import com.structurizr.view.DynamicView;
import com.structurizr.view.ViewSet;

public class Saga extends Pattern<Saga.Arguments> {

    public static class ArgumentActionItem implements Schema {

        public String service;
        public String command;
        public String onError;
    }

    public static class Arguments implements Schema {

        public String orchestrator;
        public List<ArgumentActionItem> item;
    }

    private class SagaItem {

        public Container container;
        public String description;

        public SagaItem(Container container, String description) {
            this.container = container;
            this.description = description;
        }
    }

    public static Optional<String> getDocumentation() {
        StringBuilder builder = new StringBuilder();

        builder.append("### Saga\n");
        builder.append("Суть паттерна заключается в организации транзакций, при этом придерживаясь концепции микросервисов.\n");
        builder.append("\n");
        builder.append("#### Проблема\n");
        builder.append("У нас есть много отдельных сервисов, каждый из которых ответственен за часть функциональности.\n");
        builder.append("Однако, в некоторых случаях требуется реализовать цепочку вызовов, затрагивающую несколько сервисов,\n");
        builder.append("при этом обеспечив согласованность - если на каком-то этапе произошла ошибка,\n");
        builder.append("то система должна вернуться к состоянию, в котором она была до выполнения транзакции.\n");
        builder.append("\n");
        builder.append("#### Решение\n");
        builder.append("Паттерн описывает вариацию Orchestration-based saga.\n");
        builder.append("При таком подходе мы добавляем еще один сервис, отвечающий за транзакцию.\n");
        builder.append("Его называют saga оркестратором.\n");
        builder.append("\n");
        builder.append("Его работа заключается в отправке команд другим сервисам в определенном порядке и\n");
        builder.append("отправке обратных команд при возникновении ошибки. Вариант более приоритетный,\n");
        builder.append("так как нет мешанины, нет размазывания логики, все находится в отдельном сервисе.\n");

        return Optional.of(builder.toString());
    }

    @Override
    protected void apply(StructurizrDslPluginContext context, Arguments arguments) {
        System.out.println("[log] [saga] Script started");

        StructurizrDslParser dslParser = context.getDslParser();
        IdentifiersRegister identifiersRegister = dslParser.getIdentifiersRegister();

        /* Main */
        String orchestratorId = arguments.orchestrator;
        Container orchestratorContainer = (Container) findElement(identifiersRegister, orchestratorId);

        List<SagaItem> transactionSteps = new ArrayList<>();
        List<SagaItem> rollbackSteps = new ArrayList<>();
        int index = 0;

        for (ArgumentActionItem item : arguments.item) {
            String serviceId = item.service;
            String stepDescription = item.command;
            String rollbackStepDescription = item.onError;

            System.out.println("[log] [saga] item (" + index + "): service=" + serviceId + ", step=" + stepDescription + ", onError=" + rollbackStepDescription);

            Container itemService = (Container) findElement(identifiersRegister, serviceId);

            if (itemService.getSoftwareSystem() != orchestratorContainer.getSoftwareSystem()) {
                throw new java.lang.RuntimeException("[error] [saga] services '" + orchestratorId + "' and '" + serviceId + "' must be in same software system");
            }

            transactionSteps.add(new SagaItem(itemService, stepDescription));
            rollbackSteps.add(0, new SagaItem(itemService, rollbackStepDescription));

            index++;
        }

        /* Build relationships */
        ViewSet views = context.getWorkspace().getViews();
        DynamicView transactionView = views.createDynamicView(
                orchestratorContainer.getSoftwareSystem(),
                "TransactionView",
                "View of transaction"
        );

        System.out.println("[log] [saga] autolayout set as applied");

        for (SagaItem step : transactionSteps) {
            orchestratorContainer.uses(step.container, step.description);
            transactionView.add(orchestratorContainer, step.description, step.container);
            System.out.println("[log] [saga] relationship '" + step.description + "' added");
        }

        for (SagaItem step : rollbackSteps) {
            orchestratorContainer.uses(step.container, step.description + " on error");
            transactionView.add(orchestratorContainer, step.description + " on error", step.container);
            System.out.println("[log] [saga] relationship '" + step.description + "' added");
        }

        // change implementation on 'Graphvis' instead of 'Dagre'
        transactionView.enableAutomaticLayout(
                AutomaticLayout.RankDirection.LeftRight,
                300,
                500
        );

        System.out.println("[log] [saga] steps amount: " + rollbackSteps.size());
        System.out.println("[log] [saga] Script end");
    }

    private Element findElement(IdentifiersRegister identifiersRegister, String elementId) {
        Element foundElement = identifiersRegister.getElement(elementId);
        if (foundElement == null) {
            throw new java.lang.RuntimeException("[error] [db per service] element with id '" + elementId + "' not found");
        }
        return foundElement;
    }
}
