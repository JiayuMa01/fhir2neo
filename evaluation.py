# Description: Main file for the project
import json

import cypher_generator
import neo4j_driver
import os
import time
import matplotlib.pyplot as plt
from main import read_all_json_files, convert_one_json_to_cypher


def evaluate(time_info_dict):
    # Measure the execution time of the first 20 JSON files.
    num_file = 20
    file_sizes = []
    analysis_times_avg = []
    upload_times_avg = []
    total_times_avg = []

    # For each file, calculate the average of three measurements.
    for key, value in time_info_dict.items():
        file_sizes.append(value[0])
        analysis_times_avg.append(sum(value[1]) / len(value[1]))
        upload_times_avg.append(sum(value[2]) / len(value[2]))
        total_times_avg.append(sum(value[3]) / len(value[3]))

    sorted_indices = sorted(range(len(file_sizes)), key=lambda i: file_sizes[i])
    file_sizes_sorted_kb_avg = [file_sizes[i] / 1024 for i in sorted_indices[:num_file]]
    analysis_times_sorted_avg = [analysis_times_avg[i] for i in sorted_indices[:num_file]]
    upload_times_sorted_avg = [upload_times_avg[i] for i in sorted_indices[:num_file]]
    total_times_sorted_avg = [total_times_avg[i] for i in sorted_indices[:num_file]]

    # analysis time chart
    plt.figure(figsize=(10, 6))
    plt.plot(file_sizes_sorted_kb_avg, analysis_times_sorted_avg, label='Analysis Time', color='blue')
    plt.xlabel('File Size in KBytes')
    plt.ylabel('Average Time in Seconds')
    plt.title('Average Analysis Time vs. File Size')
    plt.legend()
    plt.tight_layout()
    plt.savefig('Evaluation/average_analysis_times_vs_file_size.png')

    # upload time chart
    plt.figure(figsize=(10, 6))
    plt.plot(file_sizes_sorted_kb_avg, upload_times_sorted_avg, label='Upload Time', color='green')
    plt.xlabel('File Size in KBytes')
    plt.ylabel('Average Time in Seconds')
    plt.title('Average Upload Time vs. File Size')
    plt.legend()
    plt.tight_layout()
    plt.savefig('Evaluation/average_upload_times_vs_file_size.png')

    # total time chart
    plt.figure(figsize=(10, 6))
    plt.plot(file_sizes_sorted_kb_avg, total_times_sorted_avg, label='Total Time', color='red')
    plt.xlabel('File Size in KBytes')
    plt.ylabel('Average Time in Seconds')
    plt.title('Average Total Time vs. File Size')
    plt.legend()
    plt.tight_layout()
    plt.savefig('Evaluation/average_total_times_vs_file_size.png')
    # plt.show()

    # return analysis_times_avg, upload_times_avg, total_times_avg

if __name__ == '__main__':
    neo4j_config_file = 'neo4j_config.txt'
    json_folder_path = 'FHIR Data/FHIR JSON'
    cypher_folder_path = 'FHIR Data/FHIR Cypher'
    json_path_list = read_all_json_files(json_folder_path)

    driver = neo4j_driver.Neo4jDriver(neo4j_config_file)
    driver.connect()

    cnt = 1
    total_json_files = len(json_path_list)

    # Structure and content of time_and_size_dict:
    # This dictionary stores results about each processed FHIR JSON file.
    # Key: The file name (e.g., "Abbott_Buena_66").
    # Value:
    #   1. File size in bytes: The size of the JSON file.
    #   2. Analysis time in seconds: A list. Each list contains three elements corresponding to the results of
    #                                        three separate measurements. Time taken to convert the FHIR JSON
    #                                        file into Cypher statements.
    #   3. Upload time in seconds: A list with the structure above. Time taken to upload the Cypher statements
    #                              to the Neo4j database.
    #   4. Total time in seconds: A list with the structure above. Sum of analysis and upload times.
    time_and_size_dict = {}
    processed_json_files = 0

    for json_path in json_path_list:

        file_size = os.path.getsize(json_path)
        analysis_time_measurements = []
        upload_time_measurements = []
        total_time_measurements = []

        processed_json_files += 1
        print(f"Processing {processed_json_files}/{total_json_files} json file")
        json_file_name = os.path.basename(json_path)
        json_file_name = os.path.splitext(json_file_name)[0]

        cypher_file_name = f'Cypher_{json_file_name}.txt'
        cypher_file_path = f'{cypher_folder_path}/Cypher_{json_file_name}.txt'

        for measurement_round in range(3):

            start_time = time.time()
            cypher_statements = convert_one_json_to_cypher(json_path)
            cypher_generator.save_cypher_statements_to_file(cypher_statements, cypher_file_path)
            analysis_time = time.time() - start_time

            upload_start_time = time.time()
            driver.run_cypher_queries(cypher_statements)
            upload_time = time.time() - upload_start_time

            total_time = analysis_time + upload_time

            analysis_time_measurements.append(analysis_time)
            upload_time_measurements.append(upload_time)
            total_time_measurements.append(total_time)

        json_file_name = os.path.splitext(os.path.basename(json_path))[0]
        time_and_size_dict[json_file_name] = [file_size, analysis_time_measurements, upload_time_measurements, total_time_measurements]

        print(f"{processed_json_files}/{total_json_files} files have been processed")
        print("----------------------------------------------------")

        cnt += 1
        if cnt >= 21:
            break

    driver.close()

    # with open("Evaluation/processing_times_and_sizes.txt", 'w') as f:
    #     json.dump(time_and_size_dict, f, indent=4)
    # with open("Evaluation/processing_times_and_sizes.txt", 'r') as f:
    #     time_and_size_dict = json.load(f)

    evaluate(time_and_size_dict)
