#!/bin/bash

filename=$1  # Replace with your input file name

# Create a temporary file to store the modified contents
tempfile=tmp

# Use paste and awk to modify the columns and store the result in the temporary file
paste -d ' ' <(awk '{ print $2 }' "$filename") <(awk '{ print $1 }' "$filename") | awk '{ print $1 "-" $2 " " $1 }' > "$tempfile"

# Replace the original file with the modified contents
mv "$tempfile" "$filename"

echo "Modification complete."
