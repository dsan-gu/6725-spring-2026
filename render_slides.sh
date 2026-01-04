for i in {1..14}; do
  input_file="docs/lectures/slides/week${i}.qmd"
  if [ -f "$input_file" ]; then
    echo "Rendering week ${i}..."
    quarto render "$input_file" --self-contained --output-dir ../../assets/html/
  else
    echo "Warning: ${input_file} does not exist, skipping..."
  fi
done
