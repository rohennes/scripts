"""
Run this script to convert a link from docs.redhat.com to an xref format for AsciiDoc files in the OpenShift documentation repository.
To run this script, you need to have Python installed on your system.
You can run the script from the command line as follows:
python create-xref-from-drh.py
Make sure to replace <enter_full_path_to_openshift-docs_repo_here> with the actual path to your OpenShift documentation repository.
"""
import os
import re
import sys
from pathlib import Path

def find_adoc_file_with_id(root_dir, anchor_id):
    """Search for the .adoc file that contains the given anchor ID."""
    anchor_pattern = f'[id="{anchor_id}"]'
    
    for adoc_file in Path(root_dir).rglob("*.adoc"):
        with open(adoc_file, "r", encoding="utf-8") as f:
            content = f.read()
            if anchor_pattern in content:
                return adoc_file
    return None

def extract_title(adoc_file):
    """Extract the document title from an AsciiDoc file."""
    with open(adoc_file, "r", encoding="utf-8") as f:
        for line in f:
            match = re.match(r'^=\s+(.+)', line)
            if match:
                return match.group(1)
    return "Unknown Title"

def get_relative_path(file_path, root_dir):
    """Returns the relative path from the root directory to the file."""
    return Path(file_path).relative_to(Path(root_dir))

def check_link_format(link):
    """Check if the link format is assembly/assembly or assembly/module."""
    assembly_link_pattern = re.match(r'.+html/([^/]+)/([^/]+)#([^_/]+)$', link)  # assembly/assembly
    module_link_pattern = re.match(r'.+html/([^/]+)/([^_/]+)$', link)  # assembly/module
    module_with_context_link_pattern = re.match(r'.+html/([^/]+)/([^/]+)#([^/]+)_(.+)', link)  # assembly/module_context

    if assembly_link_pattern:
        print("Valid assembly/assembly link format")
        return "assembly/assembly", assembly_link_pattern.groups()
    elif module_link_pattern:
        print("Valid assembly/module link format")
        return "assembly/module", module_link_pattern.groups()
    elif module_with_context_link_pattern:
        print("Valid assembly/module_context link format")
        return "assembly/module_context", module_with_context_link_pattern.groups()
    else:
        print("Invalid link format")
        return "invalid", None

def convert_link_to_xref(link, root_dir):
    """Convert a documentation URL to an xref format based on its structure."""
    link_format, match_groups = check_link_format(link)

    if link_format == "invalid":
        return None
    
    folder_name, first_slug = match_groups[0], match_groups[1]

    if link_format == "assembly/assembly":
        # Assembly/Assembly format
        anchor_id = match_groups[2]
        second_adoc_file = find_adoc_file_with_id(root_dir, anchor_id)
        if not second_adoc_file:
            print(f"Could not find .adoc file for anchor ID: {anchor_id}")
            return None
        else:
            print(f"Found .adoc file: {second_adoc_file}")
            relative_path = get_relative_path(second_adoc_file, root_dir)
            return f"xref:../{relative_path}#{anchor_id}[]"
    elif link_format == "assembly/module":
        # Assembly/Module format
        first_adoc_file = find_adoc_file_with_id(root_dir, first_slug)
        if first_adoc_file:
            print(f"Found .adoc file: {first_adoc_file}")
            relative_path = get_relative_path(first_adoc_file, root_dir)
            return f"xref:../{relative_path}#{first_slug}[]"
        else:
            print(f"Could not find .adoc file for first slug: {first_slug}. This is probably a slug created from the title and doesn't correspond to any assembly ID... I'm afraid you'll have to go on without my help... :(")
            return None
    elif link_format == "assembly/module_context":
        # Assembly/Module Context format
        context_assembly_id = match_groups[3]
        #print(f"Context assembly ID: {context_assembly_id}")
        first_adoc_file = find_adoc_file_with_id(root_dir, first_slug)
        if first_adoc_file:
            print(f"Found .adoc file: {first_adoc_file}")
            relative_path = get_relative_path(first_adoc_file, root_dir)
            return f"xref:../{relative_path}#{match_groups[2]}_{context_assembly_id}[]"
        else:
            print(f"Could not find .adoc file for first slug: {first_slug}")
            return None

if __name__ == "__main__":
    # Ask the user for the link and repo root directory
    url = input("Please enter the full link of the page from docs.redhat.com (e.g. https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html/edge_computing/cnf-talm-for-cluster-updates): ")
    repo_root = "<enter_full_path_to_openshift-docs_repo_here>"  # e.g. /home/user/openshift-docs/

    # Ensure the root directory exists
    if not os.path.isdir(repo_root):
        print(f"The provided root directory '{repo_root}' does not exist.")
        sys.exit(1)

    xref = convert_link_to_xref(url, repo_root)
    if xref:
        print ("**Xref generated successfully:**")
        print("--------------------------------------------------")
        print(xref)
        print("--------------------------------------------------")
        print("Please double-check the xref before publishing.")
        print("Also, the climbing path ../ is not accouted for in the generated xref so you may need to change that according to the depth of the file in the repo.")
        print("Oh, and one last thing, you'll have to enter in the human-readable label yourself.")
