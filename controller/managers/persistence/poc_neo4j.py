from neo4j import GraphDatabase

def create_and_return_greeting(tx, message):
    result = tx.run("CREATE (a:Greeting) "
                    "SET a.message = $message "
                    "RETURN a.message + ', from node ' + id(a)", message=message)
    return result.single()[0]


# NOTE: when running this script in a container defined in docker-compose.yml,
#       the url for MongoClient needs to match the database service name
#       --> eg. "bolt://neo4j:7687"
driver = GraphDatabase.driver("bolt://localhost:7687")
with driver.session() as session:
    greeting = session.write_transaction(create_and_return_greeting, "hello, world")
    print(greeting)
