# Description: Main file for the project
import graph_helper
import cypher_generator
import neo4j_driver
import os


# Return a list with cypher statements strings
def convert_one_json_to_cypher(json_file_path):
    graph = graph_helper.convert_json_to_graph(json_file_path)
    graph_helper.build_property_nodes_for_each_node(graph)
    cypher_nodes_statements = cypher_generator.convert_all_nodes_to_cypher(graph)
    cypher_edges_statements = cypher_generator.convert_all_edges_to_cypher(graph)
    all_cypher_statements = cypher_nodes_statements + cypher_edges_statements
    return all_cypher_statements


def read_all_json_files(json_folder_path):
    json_path_list = []
    for json_file in os.listdir(json_folder_path):
        if json_file.endswith(".json"):
            json_path = json_folder_path + "/" + json_file
            json_path_list.append(json_path)
    return json_path_list


if __name__ == '__main__':
    neo4j_config_file = 'neo4j_config.txt'
    json_folder_path = 'FHIR Data/FHIR JSON'
    cypher_folder_path = 'FHIR Data/FHIR Cypher'
    json_path_list = read_all_json_files(json_folder_path)

    driver = neo4j_driver.Neo4jDriver(neo4j_config_file)
    driver.connect()

    cnt = 1
    total_json_files = len(json_path_list)
    processed_json_files = 0
    for json_path in json_path_list:
        processed_json_files += 1
        print(f"Processing {processed_json_files}/{total_json_files} json file")
        json_file_name = os.path.basename(json_path)
        json_file_name = os.path.splitext(json_file_name)[0]
        cypher_file_name = f'Cypher_{json_file_name}.txt'
        cypher_file_path = f'{cypher_folder_path}/Cypher_{json_file_name}.txt'

        print("Converting " + json_path + " to Cypher statements")
        cypher_statements = convert_one_json_to_cypher(json_path)
        print("Cypher statements have been generated")

        cypher_generator.save_cypher_statements_to_file(cypher_statements, cypher_file_path)
        print(cypher_file_name + " has been saved at " + cypher_folder_path)

        print("Uploading Cypher statements in " + cypher_file_name + " to Neo4j database")
        driver.run_cypher_queries(cypher_statements)
        print("Cypher statements in " + cypher_file_name + " has been uploaded to Neo4j database")


        print(f"{processed_json_files}/{total_json_files} files have been processed")
        print("----------------------------------------------------")

        cnt += 1
        if cnt >= 2:
            break

    driver.close()
