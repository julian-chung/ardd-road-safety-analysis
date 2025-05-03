#!/bin/bash

echo "📦 Converting notebooks to HTML (no code cells)..."

# Convert main EDA notebook
jupyter nbconvert --to html --no-input notebooks/0-eda-australian-road-fatalities.ipynb

# Convert VRU sub-analysis notebook
jupyter nbconvert --to html --no-input notebooks/1-vulnerable-road-users.ipynb

echo "✅ Conversion complete. Opening in browser..."

# Open HTML files
open notebooks/0-eda-australian-road-fatalities.html
open notebooks/1-vulnerable-road-users.html
echo "📂 HTML files opened in browser."