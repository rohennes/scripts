#!/bin/bash

# Extract headers
HEADER=$(head -n 1 communication-matrix-aws.csv)

# Sort the files while excluding the header
tail -n +2 communication-matrix-aws.csv | sort > communication-matrix-aws_sorted.csv
tail -n +2 communication-matrix-aws-sno.csv | sort > communication-matrix-aws-sno_sorted.csv
tail -n +2 communication-matrix-bm.csv | sort > communication-matrix-bm_sorted.csv
tail -n +2 communication-matrix-bm-sno.csv | sort > communication-matrix-bm-sno_sorted.csv

# Find common rows iteratively (excluding headers)
comm -12 communication-matrix-aws_sorted.csv communication-matrix-aws-sno_sorted.csv > temp_common1.csv
comm -12 temp_common1.csv communication-matrix-bm_sorted.csv > temp_common2.csv
comm -12 temp_common2.csv communication-matrix-bm-sno_sorted.csv > common_rows_data.csv

# Add the header back to the common rows
{ echo "$HEADER"; cat common_rows_data.csv; } > communication-matrix-common.csv

# Remove common rows from each file and reattach the header
comm -23 communication-matrix-aws_sorted.csv common_rows_data.csv > temp_unique.csv
{ echo "$HEADER"; cat temp_unique.csv; } > communication-matrix-aws_unique.csv

comm -23 communication-matrix-aws-sno_sorted.csv common_rows_data.csv > temp_unique.csv
{ echo "$HEADER"; cat temp_unique.csv; } > communication-matrix-aws-sno_unique.csv

comm -23 communication-matrix-bm_sorted.csv common_rows_data.csv > temp_unique.csv
{ echo "$HEADER"; cat temp_unique.csv; } > communication-matrix-bm_unique.csv

comm -23 communication-matrix-bm-sno_sorted.csv common_rows_data.csv > temp_unique.csv
{ echo "$HEADER"; cat temp_unique.csv; } > communication-matrix-bm-sno_unique.csv

# Clean up temporary files
rm temp_common1.csv temp_common2.csv common_rows_data.csv temp_unique.csv
rm communication-matrix-aws_sorted.csv communication-matrix-aws-sno_sorted.csv
rm communication-matrix-bm_sorted.csv communication-matrix-bm-sno_sorted.csv

# Define the CSV files to sort
FILES=(
  "communication-matrix-common.csv"
  "communication-matrix-aws_unique.csv"
  "communication-matrix-aws-sno_unique.csv"
  "communication-matrix-bm_unique.csv"
  "communication-matrix-bm-sno_unique.csv"
)

# Sort each file while preserving the header
for FILE in "${FILES[@]}"; do
  if [ -f "$FILE" ]; then
    { head -n 1 "$FILE"; tail -n +2 "$FILE" | sort -t"," -k8,8 -k2,2 -k3,3n; } > "$FILE.sorted"
    echo "Processed $FILE and saved sorted output as $FILE.sorted"
  else
    echo "File $FILE not found!"
  fi
done