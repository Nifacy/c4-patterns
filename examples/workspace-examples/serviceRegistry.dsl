workspace {
    model {
        user = person "User"

        system = softwareSystem "Orders Application" {
            serviceRegistry = container "Service Registry" {
                technology "Eureka"
                description "Manages services registration and discovery"
            }

            orderService = container "Order Service"
            paymentService = container "Payment Service"
            inventoryService = container "Inventory Service"

            user -> orderService "Creates order" 
            orderService -> paymentService "Sends payment request"
            orderService -> inventoryService "Checks items availability"

            $pattern com.patterns.ServiceRegistry {
                registry             serviceRegistry
                connectedServices    paymentService,inventoryService

                query.0.source       orderService
                query.0.destination  paymentService

                query.1.source       orderService
                query.1.destination  inventoryService
            }
        }
    }
}
