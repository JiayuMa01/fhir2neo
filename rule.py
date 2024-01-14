
class Rule:
    def __init__(self, rule_file_path):
        self.rules = self.read_rules_from_file(rule_file_path)

    def read_rules_from_file(self, file_path):
        rules = {}
        with open(file_path, 'r') as file:
            for line in file:
                # Split the line into tokens based on whitespace
                tokens = line.strip().split()
                # Check if the line has at least three tokens and ends with a semicolon
                if len(tokens) >= 3:
                    # Extract the first, second, and third tokens
                    node1, edge_type, node2 = tokens[:3]
                    # Add an entry to the type_rules dictionary
                    rules[(node1, node2)] = edge_type
        return rules

    def get_rules(self):
        return self.rules
