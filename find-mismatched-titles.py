import os
import re

# Function to strip AsciiDoc markup from a string
def strip_markup(text):
    """
    Strips AsciiDoc markup such as backticks, bold/italic markers, and other inline markup.
    """
    return re.sub(r"(`|_|\*|\.)", "", text)

# Function to recursively search for headings in .adoc files
def search_for_heading_in_directory(title, search_dir):
    """
    Searches for a heading matching the given title in all .adoc files within the specified directory.
    """
    title_stripped = strip_markup(title)
    found = False

    for root, _, files in os.walk(search_dir):
        for file in files:
            if file.endswith(".adoc"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if re.match(r"^\={1,6} ", line):  # Match AsciiDoc headings
                            heading_stripped = strip_markup(line.strip())
                            if title_stripped in heading_stripped:
                                print(f"Match found in file: {file_path}")
                                print(f"Heading: {line.strip()}")
                                found = True
    return found

# Function to process a single file for hardcoded titles
def process_file(file_path, search_dir, exclude_patterns, unmatched_titles):
    """
    Processes a file to extract hardcoded titles and search for them as headings in the directory.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            # Match "For more information," lines with quoted titles
            if re.match(r"^For (more |further )?information", line) and '"' in line:
                if not any(re.search(pattern, line) for pattern in exclude_patterns):
                    # Extract the title inside quotes
                    match = re.search(r'"([^"]+)"', line)
                    if match:
                        title = match.group(1)
                        print(f"File: {file_path}")
                        print(f"Title: {title}")
                        print(f"Line: {line.strip()}")
                        print("---")
                        
                        # Search for the heading in the directory
                        heading_found = search_for_heading_in_directory(title, search_dir)
                        
                        # If no heading found, add to unmatched titles
                        if not heading_found:
                            unmatched_titles.append((file_path, title))

# Main script logic
def main(search_dir):
    """
    Main function to recursively process .adoc files for hardcoded titles and search for matching headings.
    """
    exclude_patterns = [r"xref:", r"link:", r"Additional resources"]
    unmatched_titles = []  # List to keep track of titles without matches

    for root, _, files in os.walk(search_dir):
        for file in files:
            if file.endswith(".adoc"):
                file_path = os.path.join(root, file)
                process_file(file_path, search_dir, exclude_patterns, unmatched_titles)

    # After processing all files, report unmatched titles
    if unmatched_titles:
        print("\n=== Titles with no matches found ===")
        for file_path, title in unmatched_titles:
            print(f"File: {file_path}")
            print(f"Title: {title}")
            print("---")
    else:
        print("\nAll hardcoded titles found a matching heading.")

if __name__ == "__main__":
    import sys

    # Get the search directory from command-line arguments or default to the current directory
    search_directory = sys.argv[1] if len(sys.argv) > 1 else "."

    main(search_directory)
