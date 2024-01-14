# Convert the graph to cypher statements.

# Example of cypher statements:
# CREATE (alice:Person {id: '1', name: 'Alice', age: 30, city: 'New York'})
# CREATE (bob:Person {id: '2', name: 'Bob', age: 35, city: 'San Francisco'})
# CREATE (charlie:Person {id: '3', name: 'Charlie', age: 25, city: 'Los Angeles'})
# CREATE (dave:Person {id: '4', name: 'Dave', age: 28, city: 'Chicago'})
# CREATE (eva:Person {id: '5', name: 'Eva', age: 32, city: 'Miami'})
# CREATE (frank:Person {id: '6', name: 'Frank', age: 40, city: 'Seattle'})
# CREATE (grace:Person {id: '7', name: 'Grace', age: 22, city: 'Boston'})
# CREATE (hank:Person {id: '8', name: 'Hank', age: 37, city: 'Denver'})
# CREATE (irene:Person {id: '9', name: 'Irene', age: 29, city: 'Austin'})
# CREATE (jack:Person {id: '10', name: 'Jack', age: 33, city: 'Portland'})
# WITH 1 AS dummy
# CREATE (n)-[:KNOWS]->(m)
# WITH 1 AS dummy
# MATCH (n), (m) WHERE n.id = "3" AND m.id = "5" CREATE (n)-[:KNOWS]->(m)
# WITH 1 AS dummy
# MATCH (n), (m) WHERE n.id = "6" AND m.id = "7" CREATE (n)-[:KNOWS]->(m)


# Cypher statement create node
def convert_one_node_to_cypher(node):
    node_type = node.get_node_type()
    node_name = node.get_name()
    node_properties = node.get_properties()
    node_fullUrl = node.get_fullUrl()
    node_id = node.get_id()  # Each node has a unique id. The id is used to create a relationship between two nodes.

    # Escape single quotes in property values
    escaped_properties = {}
    for key, value in node_properties.items():
        # Some values could be boolean, int, float, etc. We only need to escape string values.
        if isinstance(value, str):
            escaped_properties[key] = value.replace("'", "\\'")
        else:
            escaped_properties[key] = value

    # Build Cypher statement
    properties_str = ', '.join([f"{key}: '{value}'" for key, value in escaped_properties.items()])
    properties_part = f", {properties_str}" if properties_str else ""

    node_label = f"n_{node_id}"

    cypher_statement = "CREATE ({}:{} {{node_name: '{}'{} , id: '{}', fullUrl: '{}'}})".format(node_label,
                                                                                               node_type, node_name,
                                                                                               properties_part, node_id,
                                                                                               node_fullUrl)
    return cypher_statement


# Cypher statement create edge
def convert_one_edge_to_cypher(edge):
    edge_type = edge.get_edge_type() if edge.get_edge_type() else "UNDEFINED"
    source_node_id = edge.get_source_node().get_id()
    target_node_id = edge.get_target_node().get_id()
    source_node_name = edge.get_source_node().get_name()
    target_node_name = edge.get_target_node().get_name()
    source_node_type = edge.get_source_node().get_node_type()
    target_node_type = edge.get_target_node().get_node_type()

    source_node_label = f"n_{source_node_id}"
    target_node_label = f"n_{target_node_id}"

    # Escape single quotes in property values
    escaped_source_node_name = source_node_name.replace("'", "\\'")
    escaped_target_node_name = target_node_name.replace("'", "\\'")
    escaped_source_node_type = source_node_type.replace("'", "\\'")
    escaped_target_node_type = target_node_type.replace("'", "\\'")

    cypher_statement = ("MATCH (n), (m) "
                        "WHERE n.id = '{}' AND m.id = '{}' "
                        "CREATE (n)-[:{} {"
                        "{source_node_name: '{}', "
                        "target_node_name: '{}', "
                        "source_node_type: '{}', "
                        "target_node_type: '{}'}}]->(m);").format(
        source_node_id, target_node_id, edge_type,
        escaped_source_node_name, escaped_target_node_name,
        escaped_source_node_type, escaped_target_node_type,)

    return cypher_statement


# This will return a list of cypher statements line by line, creating all nodes.
def convert_all_nodes_to_cypher(graph):
    cypher_statements = []
    for node in graph.get_nodes_properties_unnested().values():
        cypher_statements.append(convert_one_node_to_cypher(node))
    return cypher_statements


# This will return a list of cypher statements line by line, creating all edges.
def convert_all_edges_to_cypher(graph):
    cypher_statements = []
    for edge in graph.get_edges():
        cypher_statements.append(convert_one_edge_to_cypher(edge))
    return cypher_statements


def save_cypher_statements_to_file(cypher_statements, file_path):
    # Save cypher statements to a txt file line by line
    with open(file_path, 'w') as f:
        for item in cypher_statements:
            f.write("%s\n" % item)
