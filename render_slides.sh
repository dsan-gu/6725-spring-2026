#!/bin/bash

# Array of week files with their descriptive names
week_files=(
  "week-01-introduction"
  "week-02-icl"
  "week-03-rag"
  "week-04-mcp"
  "week-05-agents-part1"
  "week-06-agents-part2"
  "week-07-observability"
  "week-08-guardrails-evaluation"
  "week-09-benchmarking"
  "week-10-embeddings"
  "week-11-optimization"
  "week-12-finetuning"
  "week-13-platforms"
)

for week_file in "${week_files[@]}"; do
  input_file="docs/lectures/slides/${week_file}.qmd"
  if [ -f "$input_file" ]; then
    # Extract week number for output filename
    week_num=$(echo "$week_file" | grep -oP 'week-\K\d+')
    output_file="week${week_num}.html"

    echo "Rendering ${week_file}..."
    quarto render "$input_file" --output "$output_file" --output-dir ../../assets/html/
  else
    echo "Warning: ${input_file} does not exist, skipping..."
  fi
done

echo "Slide rendering complete!"
