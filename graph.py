
class Node:
    # name: condition1, condition2, patient, etc.
    # node_type: Condition, Patient, etc.
    # properties: information of one resource.
    # fullUrl: the id of one resource(node).
    def __init__(self, name, node_type, properties={}, fullUrl='', isPropertyNode=False):
        self.name = name
        self.node_type = node_type
        self.properties = properties
        self.fullUrl = fullUrl
        self.child_nodes = []
        self.parent_nodes = []
        self.isPropertyNode = isPropertyNode
        self.id = 0

    def __repr__(self):
        return f"{self.name}"

    def add_child_node(self, child_node):
        self.child_nodes.append(child_node)

    def add_parent_node(self, parent_node):
        self.parent_nodes.append(parent_node)

    def add_node_property(self, property_dict):
        self.properties.update(property_dict)

    def remove_node_property(self, property_key):
        self.properties.pop(property_key, None)

    def clear_node_all_properties(self):
        self.properties.clear()

    # Getters for name, node_type, properties={}, fullUrl
    def get_name(self):
        return self.name

    def get_node_type(self):
        return self.node_type

    def get_properties(self):
        return self.properties

    def get_isPropertyNode(self):
        return self.isPropertyNode

    def get_fullUrl(self):
        return self.fullUrl

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id


class Edge:
    def __init__(self, source_node, target_node, edge_type=''):
        self.edge_type = edge_type
        self.source_node = source_node
        self.target_node = target_node
        self.source_node.add_child_node(target_node)
        self.target_node.add_parent_node(source_node)

    def __repr__(self):
        return f"({self.source_node.get_id()}, {self.target_node.get_id()})"

    def set_edge_type(self, rules):
        key = tuple([self.source_node.node_type, self.target_node.node_type])
        if key in rules:
            self.edge_type = rules.get(key)

    def set_property_edge_type(self, type_name):
        self.edge_type = type_name

    # Getters for edge_type, source_node, target_node
    def get_edge_type(self):
        return self.edge_type

    def get_source_node(self):
        return self.source_node

    def get_target_node(self):
        return self.target_node


class Graph:
    def __init__(self, graph_id=''):
        self.graph_id = graph_id
        self.nodes_properties_nested = {}
        self.nodes_url_as_key = {}
        self.nodes_properties_unnested = {}
        self.edges = set()

    def add_node_properties_nested(self, node):
        id = self.get_graph_id() + str(len(self.get_nodes_properties_nested()) + 1)
        node.set_id(id)
        self.nodes_properties_nested[id] = node
        self.nodes_url_as_key[node.get_fullUrl()] = node.get_id()

    def add_node_properties_unnested(self, node):
        id = self.get_graph_id() + "_" + str(len(self.get_nodes_properties_unnested()) + 1)
        node.set_id(id)
        self.nodes_properties_unnested[id] = node

    def add_edge(self, edge):
        self.edges.add(edge)

    def set_graph_id(self, graph_id):
        # Get rid of "urn:uuid:"
        graph_id = graph_id[len("urn:uuid:"):]
        # Replace "-" with "_"
        graph_id = graph_id.replace("-", "_")
        self.graph_id = graph_id

    # Find one node by its name and return
    def find_node_by_name(self, name):
        return self.nodes_properties_nested.get(name)

    # Find one node by its fullUrl and return
    def find_node_by_fullUrl(self, fullUrl):
        name = self.nodes_url_as_key.get(fullUrl)
        return self.nodes_properties_nested.get(name)

    # Getters for graph_id, nodes, edges
    def get_graph_id(self):
        return self.graph_id

    def get_nodes_properties_nested(self):
        return self.nodes_properties_nested

    def get_nodes_properties_unnested(self):
        return self.nodes_properties_unnested

    def get_edges(self):
        return self.edges

    def get_edges_with_type(self):
        return [(edge.get_source_node().get_name(), edge.get_target_node().get_name(), edge.get_edge_type()) for edge in self.edges]

    def get_nodes_url_as_key(self):
        return self.nodes_url_as_key
