# fhir2neo

## 1. Introduction

**fhir2neo** is a project that aims to seamlessly connect FHIR healthcare data files with Neo4j graph databases. 
The goal is to automatically read FHIR JSON-format files, extract essential information from these files, and transform 
the extracted data into a graph structure through the creation of nodes and edges. This forms a representation method 
capable of capturing inherent relationships within medical information. The program then reads user-defined mapping 
rules to generate corresponding Cypher query language [link](https://neo4j.com/developer/cypher/). Finally, 
the program automatically connects to the user's local Neo4j database, seamlessly integrating the transformed data into 
the Neo4j graph database. This achieves the automatic extraction and integration of healthcare information. Subsequently, 
visualization of FHIR data in Neo4j will be implemented to provide a more intuitive representation of the intricate 
relationships within medical information.

## 2. Using fhir2neo

### Usage Prerequisites
- Python 3.8
- Prepare FHIR Sample Data (e.g., patient bundle [link](https://github.com/smart-on-fhir/generated-sample-data/tree/master/DSTU-2/SYNTHEA)), and save files in the project's "FHIR Data/FHIR JSON" directory.
- Download Neo4j Desktop ([link](https://neo4j.com/download))
- Run `pip install neo4j` in your shell

### How to use fhir2neo

1. Open Neo4j Desktop and connect to your local database.
2. Before running the program, modify `neo4j_config.txt` in the program directory according to your own Neo4j database information. 
   For example:
   ```
   uri = bolt://localhost:7689
   user = neo4j
   password = 123456789
   ```
3. Run `main.py`. The program will read the JSON files in "FHIR Data/FHIR JSON," extract key information, and generate Cypher statements. The statements will be saved in "FHIR Data/FHIR Cypher." The program will then automatically connect to the Neo4j database using "neo4j_config.txt." Visualized results can be observed in your Neo4j database (Neo4j Browser).
4. Tips: You can edit the `cnt` on line 63 of `main.py` to determine how many JSON files the program processes. For example:
   ```
   if cnt >= 3: 
   break
   ```
   This means the program processes the first 2 JSON files, saving time for testing. The estimated processing time for each JSON file, including reading, conversion, and uploading to Neo4j, is less than a minute.

