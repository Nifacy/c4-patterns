import com.structurizr.dsl.IdentifiersRegister;
import com.structurizr.dsl.StructurizrDslParser;
import com.structurizr.dsl.StructurizrDslPluginContext;
import com.structurizr.model.*;
import io.github.nifacy.c4patterns.lib.Pattern;
import io.github.nifacy.c4patterns.lib.params.Schema;

import java.lang.reflect.Method;
import java.util.Optional;

public class ReverseProxy extends Pattern<ReverseProxy.Arguments> {

    public static Optional<String> getDocumentation() {

        String builder = "### Reverse Proxy pattern\n" +
                "Основное назначение данного паттерна состоит в том, чтобы скрыть систему от клиента за одним IP адресом.\n" +
                "Reverse Proxy получает запросы от клиента и определяет, кому переадресовать этот запрос.\n" +
                "\n" +
                "Reverse Proxy может выполнять следующие задачи:\n" +
                "- **кеширование.** Proxy сервис может кешировать результаты и не делать обращений к сервисам, если этого не требуется.\n" +
                "- **балансировка.** Proxy может выполнять задачу, схожую с Load Balancer - балансировать нагрузку на сервисы.\n" +
                "- **шифрование.** Proxy может быть использован в целях безопасности для шифрования трафика, приходящего на сервисы.\n";

        return Optional.of(builder);
    }

    @Override
    public void apply(StructurizrDslPluginContext context, Arguments arguments) {
        try {
            StructurizrDslParser dslParser = context.getDslParser();
            IdentifiersRegister identifiersRegister = dslParser.getIdentifiersRegister();

            // parameters
            String target = arguments.target;
            Container targetContainer = (Container) identifiersRegister.getElement(target);

            System.out.println("[log] Apply Proxy Server pattern to " + targetContainer.toString() + " ...");

            // create proxy server container in same software system
            SoftwareSystem targetSoftwareSystem = targetContainer.getSoftwareSystem();
            Container proxyContainer = targetSoftwareSystem.addContainer("Reverse Proxy");
            System.out.println("[log] Created proxy server container " + proxyContainer);

            // change destination of incoming relationships
            Model targetModel = context.getWorkspace().getModel();

            System.out.println("[log] Change destination of incoming relationships...");

            for (Relationship relationship : targetModel.getRelationships()) {
                if (relationship.getDestination() == targetContainer) {
                    System.out.println("[log] Change destination for " + relationship + " from " + targetContainer + " to " + proxyContainer);

                    Method method = Relationship.class.getDeclaredMethod("setDestination", Element.class);
                    method.setAccessible(true);
                    method.invoke(relationship, proxyContainer);
                }
            }

            // join containers in group
            String proxyGroupName = targetContainer.getName() + " with Reverse Proxy";
            targetContainer.setGroup(proxyGroupName);
            proxyContainer.setGroup(proxyGroupName);

            // add relationship
            Relationship proxyRelationship = proxyContainer.uses(targetContainer, "Resends Requests");
            System.out.println("[log] Created relationship " + proxyRelationship.toString());

            System.out.println("[log] Proxy Server pattern applied");
        } catch (Exception e) {
            throw new java.lang.RuntimeException(e.toString());
        }
    }

    public static class Arguments implements Schema {

        public String target;
    }
}
