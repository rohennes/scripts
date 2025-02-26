import os
import yaml

def parse_yaml(file_path, debug=False):
    """Load and parse the topic map file."""
    if debug:
        print(f"Parsing YAML file: {file_path}")
    try:
        with open(file_path, 'r') as f:
            documents = list(yaml.safe_load_all(f))
        if debug:
            print(f"Successfully parsed {len(documents)} YAML documents.")
        return documents
    except Exception as e:
        print(f"Error parsing YAML file: {e}")
        return []

def extract_name_and_file(data, debug=False):
    """Recursively extract Name and File values."""
    name_file_pairs = []
    if isinstance(data, list):
        for item in data:
            name_file_pairs.extend(extract_name_and_file(item, debug))
    elif isinstance(data, dict):
        if 'Name' in data and 'File' in data:
            name_file_pairs.append((data['Name'], data['File']))
            if debug:
                print(f"Extracted pair: Name='{data['Name']}', File='{data['File']}'")
        if 'Topics' in data:
            name_file_pairs.extend(extract_name_and_file(data['Topics'], debug))
    return name_file_pairs

def find_adoc_file(root_dir, file_name, debug=False):
    """Recursively search for an .adoc file."""
    if debug:
        print(f"Searching for '{file_name}.adoc' in directory: {root_dir}")
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename == f"{file_name}.adoc":
                adoc_path = os.path.join(dirpath, filename)
                if debug:
                    print(f"Found .adoc file: {adoc_path}")
                return adoc_path
    if debug:
        print(f"File '{file_name}.adoc' not found.")
    return None

def check_heading(file_path, expected_heading, debug=False):
    """Check if the first-level heading in the .adoc file matches the expected heading."""
    if debug:
        print(f"Checking first-level heading in: {file_path}")
    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith("="):  # First-level heading in AsciiDoc
                    actual_heading = line[2:].strip()
                    if debug:
                        print(f"Found heading: '{actual_heading}'")
                    return actual_heading == expected_heading, actual_heading
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
    return False, None

def main(topic_map_path, adoc_root_dir, debug=False):
    # Check if the topic map file exists
    if not os.path.isfile(topic_map_path):
        print(f"Topic map file not found: {topic_map_path}")
        return

    # Check if the AsciiDoc root directory exists
    if not os.path.isdir(adoc_root_dir):
        print(f"AsciiDoc root directory not found: {adoc_root_dir}")
        return

    # Parse the topic map
    documents = parse_yaml(topic_map_path, debug)
    if not documents:
        print("No YAML documents found. Exiting.")
        return
    
    # Extract Name and File values
    name_file_pairs = []
    for doc in documents:
        name_file_pairs.extend(extract_name_and_file(doc, debug))
    
    if not name_file_pairs:
        print("No Name-File pairs found in the topic map. Exiting.")
        return

    discrepancies = []

    # Process each Name-File pair
    for name, file in name_file_pairs:
        adoc_path = find_adoc_file(adoc_root_dir, file, debug)
        if adoc_path:
            matches, actual_heading = check_heading(adoc_path, name, debug)
            if not matches:
                discrepancies.append({
                    "Expected Heading": name,
                    "File": file,
                    "Actual Heading": actual_heading,
                    "Path": adoc_path
                })
        else:
            discrepancies.append({
                "Expected Heading": name,
                "File": file,
                "Actual Heading": None,
                "Path": "File not found"
            })
    
    # Output results
    if discrepancies:
        print("\nDiscrepancies found:")
        for discrepancy in discrepancies:
            print(f"  Expected Heading: {discrepancy['Expected Heading']}\n"
                  f"  File: {discrepancy['File']}\n"
                  f"  Actual Heading: {discrepancy['Actual Heading']}\n"
                  f"  Path: {discrepancy['Path']}\n")
    else:
        print("\nNo discrepancies found. All headings match.")

# Run the script
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        print("Usage: python script.py <topic_map.yml> <adoc_root_dir> <debug (true/false)>")
    else:
        topic_map_path = sys.argv[1]
        adoc_root_dir = sys.argv[2]
        debug_mode = sys.argv[3].lower() == "true"
        main(topic_map_path, adoc_root_dir, debug_mode)
