import json
from graph import Graph, Node, Edge
from rule import Rule


# Read one json file and save as object. Report error if the file is not found.
def read_one_json(path):
    data = {}
    try:
        with open(path) as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        print("File not found")
    return data


# Find all the references in each resource(node).
# It can find the relationship between two nodes, which would help to find the child nodes.
def find_references(data):
    references = []
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "reference":
                references.append(value)
            else:
                references.extend(find_references(value))
    elif isinstance(data, list):
        for item in data:
            references.extend(find_references(item))
    return references


# Convert the json file to a graph.
def convert_json_to_graph(json_path):
    data = read_one_json(json_path)
    resource_list = data.get("entry", [])
    # Each item in resource_list is a dictionary.
    # Retrival the resource_list to get the resourceType.
    # And save the information in a dict, key is resourceType, value is a list of resource.
    resource_dict = {}
    for resource in resource_list:
        # The structure of 'resource' is like: {'resource': {'resourceType': 'Condition', 'clinicalStatus': {'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/condition-clinical', 'code': 'active'}]}, 'verificationStatus': {'coding': [{'system': 'http://terminology.hl7.org/CodeSystem/condition-ver-status', 'code': 'confirmed'}]}, 'code': {'coding': [{'system': 'http://snomed.info/sct', 'code': '195967001', 'display': 'Traumatic brain injury (disorder)'}]}, 'subject': {'reference': 'Patient/patient1'}, 'onsetDateTime': '2019-04-04T00:00:00+00:00', 'recordedDate': '2019-04-04T00:00:00+00:00', 'recorder': {'reference': 'Practitioner/Practitioner1'}, 'evidence': [{'detail': [{'reference': 'Observation/observation1'}]}]}}
        resource_type = resource.get('resource').get('resourceType', '')
        if resource_type:
            if resource_type not in resource_dict:
                resource_dict.update({resource_type: []})
            resource_dict[resource_type].append(resource)

    # Convert each item from resource_dict to node, and save in node_dict.
    node_dict = {}
    for resource_type in resource_dict.keys():
        type_list = resource_dict.get(resource_type)
        node_dict.update({resource_type: []})
        # There is only one resource of this type.
        if len(type_list) == 1:
            node = Node(name=resource_type.lower(),
                        node_type=resource_type,
                        properties=type_list[0].get('resource'),
                        fullUrl=type_list[0].get('fullUrl'))
            node_dict[resource_type].append(node)
        # There are more than one resource of this resource type. So we call them condition1, condition2, etc.
        else:
            cnt = 1
            for resource in type_list:
                # Name is resourceType + number, e.g. condition1, condition2, etc.
                node = Node(name=resource_type.lower() + str(cnt),
                            node_type=resource_type,
                            properties=resource.get('resource'),
                            fullUrl=resource.get('fullUrl'))
                cnt += 1
                node_dict[resource_type].append(node)


    # Create a graph
    graph = Graph()
    # Get the fullUrl of first resource in this json file. It would be used as the id of the graph.
    # Each node id would be fullUrl + number, e.g. urn:uuid:2e27c71e-30c8-4ceb-8c1c-5641e066c0a4_1
    graph.set_graph_id(data.get("entry")[0].get("fullUrl"))
    for resource_type in node_dict.keys():
        for node in node_dict[resource_type]:
            graph.add_node_properties_nested(node)

    # Read the rules from file.
    rule = Rule("rules.txt")
    rules = rule.get_rules()

    # Add edges to the graph.
    for node in graph.get_nodes_properties_nested().values():
        # Find all child nodes of this node.
        references = find_references(node.get_properties())
        for reference in references:
            # Find the child node in the graph.
            child_node = graph.find_node_by_fullUrl(reference)
            if child_node:
                # Add an edge between this node and its child node.
                edge = Edge(node, child_node)
                # Set the edge type based on the rules.
                edge.set_edge_type(rules)
                graph.add_edge(edge)

    return graph


def unnest_one_node_properties_to_simple_nodes(nested_properties_dict, parent_node, graph):
    def process_dict(nested_properties_dict, parent_node=None, parent_node_value_isList=False):
        current_node = parent_node
        for key, value in nested_properties_dict.items():
            if isinstance(value, dict):
                child_node_name = f"{parent_node.get_name()}_{key}" if parent_node else key
                child_node = Node(name=child_node_name, node_type="Property", properties={}, isPropertyNode=True)
                graph.add_node_properties_unnested(child_node)
                if parent_node:
                    edge = Edge(parent_node, child_node)
                    edge.set_property_edge_type(key)
                    graph.add_edge(edge)
                process_dict(value, child_node)
            elif isinstance(value, list):
                child_node_name = f"{parent_node.get_name()}_{key}" if parent_node else key
                child_node = Node(name=child_node_name, node_type="Property", properties={}, isPropertyNode=True)
                graph.add_node_properties_unnested(child_node)
                if parent_node:
                    edge = Edge(parent_node, child_node)
                    edge.set_property_edge_type(key)
                    graph.add_edge(edge)
                # Add number to the name of the child node, if there are more child nodes have the same name in the same list.
                # e.g. children1, children2, etc.
                for item in value:
                    if (not isinstance(item, dict)) and (not isinstance(item, list)):
                        # In case of 'family': ['Bode', 'Jackie', '69'],
                        # The properties names of node 'family' would be value1:Bode, value2:Jackie, value3:69.
                        cnt_property = len(child_node.get_properties())
                        child_node.add_node_property({"property"+str(cnt_property+1): item})
                    else:
                        process_dict(item, child_node, parent_node_value_isList=True)
            else:
                if current_node.get_isPropertyNode() and (not parent_node_value_isList):
                    current_node.add_node_property({key: value})
                # If the value of parent node is an Array, then we need to create a new node for each dict in the Array.
                elif current_node.get_isPropertyNode() and parent_node_value_isList:
                    child_node_name = f"{parent_node.get_name()}_{key}" if parent_node else key
                    child_node = Node(name=child_node_name, node_type="Property", properties={}, isPropertyNode=True)
                    graph.add_node_properties_unnested(child_node)
                    if parent_node:
                        edge = Edge(parent_node, child_node)
                        edge.set_property_edge_type(key)
                        graph.add_edge(edge)
                    process_dict(nested_properties_dict, child_node)
                    break

    process_dict(nested_properties_dict, parent_node)


def build_property_nodes_for_each_node(graph):
    nodes_properties_nested = graph.get_nodes_properties_nested()
    edges = graph.get_edges()

    for node_key, node in nodes_properties_nested.items():
        nested_properties_dict = {}
        simple_properties_dict = {}
        for key, value in node.get_properties().items():
            if isinstance(value, dict) or isinstance(value, list):
                nested_properties_dict.update({key: value})
            else:
                simple_properties_dict.update({key: value})
        node.clear_node_all_properties()
        node.add_node_property(simple_properties_dict)
        graph.add_node_properties_unnested(node)

        unnest_one_node_properties_to_simple_nodes(nested_properties_dict, node, graph)
