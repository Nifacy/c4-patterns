workspace "Layered architecture" {
    model {
        user = person "User"
        system = softwareSystem OnlineShop {
            consumerFrontend = container "App for Consumer"
            sellerFrontend = container "App for Seller"

            orderService = container "Order Processing Service"
            inventoryService = container "Inventory Management Service"

            databaseMain = container "Main Database"
            databaseArchive = container "Archive Database"
        }

        user -> consumerFrontend "Uses through web-browser"
        user -> sellerFrontend "Uses through web-browser"

        consumerFrontend -> orderService "Sends order requests"
        consumerFrontend -> inventoryService "Queries product information"
        sellerFrontend -> inventoryService "Updates product inventory"

        orderService -> databaseMain "Read & write order data"
        inventoryService -> databaseMain "Read & write inventory data"
        inventoryService -> databaseArchive "Archive older records"

        // consumerFrontend -> databaseMain "Bad relationship"

        $pattern com.patterns.Layered {
            layer.0.name "Frontend Layer"
            layer.0.elements consumerFrontend,sellerFrontend

            layer.1.name "Backend Layer"
            layer.1.elements orderService,inventoryService
            // layer.1.elements orderService,inventoryService,consumerFrontend

            layer.2.name "Database Layer"
            layer.2.elements databaseMain,databaseArchive
        }
    }
}