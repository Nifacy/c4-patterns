import com.structurizr.dsl.IdentifiersRegister;
import com.structurizr.dsl.StructurizrDslParser;
import com.structurizr.dsl.StructurizrDslPluginContext;
import com.structurizr.model.Container;
import com.structurizr.model.Element;
import com.structurizr.model.Relationship;
import io.github.nifacy.c4patterns.lib.Pattern;
import io.github.nifacy.c4patterns.lib.params.Schema;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Optional;

public class Layered extends Pattern<Layered.Arguments> {

    public static Optional<String> getDocumentation() {

        String builder = "### Многозвенная архитектура\n" +
            "Один из самых простых паттернов. Идея состоит в том, чтобы разбить всю систему на несколько слоев.\n" +
            "Каждый из слоев имеет следующие особенности и ограничения:\n" +
            "- Каждый слой может обращаться только к слою на уровень ниже, и не более\n" +
            "- Все слои образуют порядок. То есть, мы можем сказать, какой слой за каким стоит\n" +
            "\n" +
            "В модели C4 слои можно представить в виде групп, так как их физического разграничения нет (если убрать разделение по слоям, то это будет просто набор контейнеров, которые общаются по определенному протоколу).\n";

        return Optional.of(builder);
    }

    @Override
    protected void apply(StructurizrDslPluginContext context, Arguments arguments) {
        System.out.println("[log] [layered] Script started");

        StructurizrDslParser dslParser = context.getDslParser();
        IdentifiersRegister identifiersRegister = dslParser.getIdentifiersRegister();

        int index = 0;
        List<LayerGroup> layerGroups = new ArrayList<>();

        // build list of groups
        for (LayerArgument layerArgument : arguments.layer) {
            String layerName = layerArgument.name;
            String layerElementIds = layerArgument.elements;

            List<Container> layerElements = new ArrayList<>();
            for (String containerName : layerElementIds.split(",")) {
                layerElements.add((Container) identifiersRegister.getElement(containerName));
            }

            layerGroups.add(new LayerGroup(layerName, layerElements));

            System.out.println("[log] [layered] Layer " + index + ":");
            System.out.println("[log] [layered]     - name: " + layerName);
            System.out.println("[log] [layered]     - elements: " + layerElements);

            index++;
        }

        // validate elements are unique
        validateElementsAreUnique(layerGroups);

        // validate elements relationships
        for (int i = 0; i < layerGroups.size(); i++) {
            LayerGroup currentGroup = layerGroups.get(i);

            for (Container element : currentGroup.elements) {
                for (Relationship relationship : element.getRelationships()) {
                    Element relatedElement = relationship.getDestination();
                    int layerIndex = getLayerIdByElements(layerGroups, relatedElement);

                    if (layerIndex == i || layerIndex == i + 1 || layerIndex == -1) {
                        continue;
                    }

                    throw new java.lang.RuntimeException(
                        "Invalid relationship " + element
                            + " (layer " + i + ") -> " + relatedElement + " (layer " + layerIndex + ")"
                    );
                }
            }
        }

        // group elements of layers
        for (LayerGroup group : layerGroups) {
            for (Container element : group.elements) {
                element.setGroup(group.name);
            }
        }

        System.out.println("[log] [layered] Script end");

    }

    private int getLayerIdByElements(List<LayerGroup> layers, Element element) {
        for (int index = 0; index < layers.size(); index++) {
            LayerGroup layer = layers.get(index);

            for (Container layerElement : layer.elements) {
                if (layerElement == element) {
                    return index;
                }
            }
        }

        return -1;
    }

    private void validateElementsAreUnique(List<LayerGroup> layers) {
        HashMap<Container, Integer> elementsMap = new HashMap<>();

        for (int index = 0; index < layers.size(); index++) {
            LayerGroup layer = layers.get(index);

            for (Container element : layer.elements) {
                if (elementsMap.containsKey(element)) {
                    throw new java.lang.RuntimeException(
                        "Element '" + element.toString() + "' "
                            + "exists in both layers: " + elementsMap.get(element).toString() + " "
                            + "and " + index + "."
                    );
                }

                elementsMap.put(element, index);
            }
        }
    }

    public static class LayerArgument implements Schema {

        public String name;
        public String elements;
    }

    public static class Arguments implements Schema {

        public List<LayerArgument> layer;
    }

    private class LayerGroup {

        public String name;
        public List<Container> elements;

        public LayerGroup(
            String name,
            List<Container> elements
        ) {
            this.name = name;
            this.elements = elements;
        }
    }

}
