workspace {
    !plugin com.patterns.PatternSyntaxPlugin

    model {
        user = person "User"

        system = softwareSystem "Order Application" {
            orderDatabase = container "Order Service"
            orderApp = container "Order Application"

            paymentDatabase = container "Payment Service"
            paymentApp = container "Payment Application"
        }

        user -> orderApp "Creates order"
        orderApp -> paymentApp "Sends payment request"

        $pattern com.patterns.DatabasePerService {
            service          orderApp
            database         paymentDatabase
            dataDescription  "order data"
        }

        $pattern com.patterns.DatabasePerService {
            service          paymentApp
            database         paymentDatabase
            dataDescription  "payment data"
        }
    }

    views {
        container system {
            include *
            autoLayout
        }
    }
}
