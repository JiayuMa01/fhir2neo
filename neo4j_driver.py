from neo4j import GraphDatabase


class Neo4jDriver:
    def __init__(self, config_file_path='neo4j_config.txt'):
        config = self.read_database_info(config_file_path)
        self.uri = config.get("uri")
        self.user = config.get("user")
        self.password = config.get("password")
        self.driver = None

    def connect(self):
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")

    def close(self):
        if self.driver:
            self.driver.close()
            print("Connection closed.")

    def run_cypher_query(self, query):
        with self.driver.session() as session:
            result = session.run(query)
            return result

    def run_cypher_queries(self, queries):
        results = []
        with self.driver.session() as session:
            for query in queries:
                result = session.run(query)
                results.append(result)
        return results

    def read_database_info(self, file_path):
        database_info = {}
        try:
            with open(file_path, "r") as file:
                for line in file:
                    key, value = line.strip().split("=")
                    database_info[key.strip()] = value.strip()
            return database_info
        except Exception as e:
            print(f"Failed to read database info from file: {e}")
            return None
