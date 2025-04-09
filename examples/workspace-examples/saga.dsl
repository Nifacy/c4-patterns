workspace {
    model {
        user = person "User"

        orderSystem = softwareSystem "Order System" {
            api = container "API"
            orchestrator = container "Saga Orchestrator"
            orderService = container "Order Service"
            balanceService = container "Balance Service"

            user -> api "Creates Order"
            api -> orchestrator "Sends request to create order transaction"

            $pattern Saga {
                orchestrator    orchestrator

                item.0.service  orderService
                item.0.command  "Set order status PENDING"
                item.0.onError  "Set order status CANCELED"

                item.1.service  balanceService
                item.1.command  "Reserve funds"
                item.1.onError  "Refund"

                item.2.service  orderService
                item.2.command  "Set order status APPROVE"
                item.2.onError  "Set order status CANCELED"
            }
        }
    }

    views {
        container orderSystem {
            include *
            autolayout lr
        }

        theme default
    }
}