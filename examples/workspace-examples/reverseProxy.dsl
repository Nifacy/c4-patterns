workspace "Reverse Proxy" {
    !plugin com.patterns.PatternSyntaxPlugin

    model {
        customer = person "Customer"

        s = softwareSystem OnlineShop {
            app2 = container "Some other container"

            webApp = container "Web App" {
                technology "Java, Spring Boot"
            }

            app3 = container "Container 3"

            db = container "Database" {
                technology "PostgreSQL"
            }

            db2 = container "Database 2" {
                technology "Mongo"
            }
        }

        app2 -> webApp "Some relationship"
        customer -> webApp "Sends Requests"
        webApp -> db "Requests data"
        webApp -> db2 "Requests users"
        app3 -> db2 "ABOBA"

       $pattern com.patterns.ReverseProxy {
           target webApp
       }
    }

    views {
        container s {
            include *
            autoLayout lr
        }

        container s {
            include webApp app2 customer
            autoLayout lr
        }
    }
}
