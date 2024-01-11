#!/bin/bash

# repos=(
#     
#     # Add more repositories as needed
# )

file_to_check=".vale.ini"

# Check if the repo list file exists
if [ ! -f "repo_list.txt" ]; then
    echo "Error: repo_list.txt not found. Please create the file with a list of repository URLs."
    exit 1
fi

# Read repository URLs from the repo list file
mapfile -t repos < "repo_list.txt"

# Create or truncate the found.txt file
> found.txt

for repo in "${repos[@]}"; do
    temp_dir=$(mktemp -d)
    
    # Use sed to remove anything after a space following the branch name
    default_branch=$(git ls-remote --symref "$repo" HEAD | grep -oP 'refs/heads/\K[^\s]+')
    
    if [ -z "$default_branch" ]; then
        echo "Error extracting default branch for $repo"
        continue
    fi

    echo "Default branch for $repo is: $default_branch"

    git clone --branch "$default_branch" --depth 1 "$repo" "$temp_dir" &> /dev/null

    if [ -e "$temp_dir/$file_to_check" ]; then
        echo "File '${file_to_check}' found in $repo on default branch ($default_branch)"
        echo "$repo" >> found.txt
    else
        echo "File '${file_to_check}' not found in $repo on default branch ($default_branch)"
    fi

    rm -rf "$temp_dir"
done
