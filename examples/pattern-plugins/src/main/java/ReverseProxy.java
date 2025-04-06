import java.lang.reflect.Method;
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
import com.structurizr.model.SoftwareSystem;

public class ReverseProxy extends Pattern<ReverseProxy.Arguments> {

    public static class Arguments implements Schema {

        public String target;
    }

    public static Optional<String> getDocumentation() {
        StringBuilder builder = new StringBuilder();

        builder.append("### Reverse Proxy pattern\n");
        builder.append("Основное назначение данного паттерна состоит в том, чтобы скрыть систему от клиента за одним IP адресом.\n");
        builder.append("Reverse Proxy получает запросы от клиента и определяет, кому переадресовать этот запрос.\n");
        builder.append("\n");
        builder.append("Reverse Proxy может выполнять следующие задачи:\n");
        builder.append("- **кеширование.** Proxy сервис может кешировать результаты и не делать обращений к сервисам, если этого не требуется.\n");
        builder.append("- **балансировка.** Proxy может выполнять задачу, схожую с Load Balancer - балансировать нагрузку на сервисы.\n");
        builder.append("- **шифрование.** Proxy может быть использован в целях безопасности для шифрования трафика, приходящего на сервисы.\n");

        return Optional.of(builder.toString());
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
            System.out.println("[log] Created proxy server container " + proxyContainer.toString());

            // change destination of incoming relationships
            Model targetModel = context.getWorkspace().getModel();

            System.out.println("[log] Change destination of incoming relationships...");

            for (Relationship relationship : targetModel.getRelationships()) {
                if (relationship.getDestination() == targetContainer) {
                    System.out.println("[log] Change destination for " + relationship.toString() + " from " + targetContainer.toString() + " to " + proxyContainer.toString());

                    Method method = Relationship.class.getDeclaredMethod("setDestination", Element.class);
                    method.setAccessible(true);
                    method.invoke(relationship, proxyContainer);
                }
            }

            // join containers in group
            String proxyGroupName = targetContainer.getName() + " with Reverse Proxy";
            targetContainer.setGroup(proxyGroupName);
            proxyContainer.setGroup(proxyGroupName);

            // add relation ship
            Relationship proxyRelationship = proxyContainer.uses(targetContainer, "Resends Requests");
            System.out.println("[log] Created relationship " + proxyRelationship.toString());

            System.out.println("[log] Proxy Server pattern applied");
        } catch (Exception e) {
            throw new java.lang.RuntimeException(e.toString());
        }
    }
}
