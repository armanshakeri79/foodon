# List Ingredients from FoodOn Ontology

This directory contains tools to extract and list ingredients from the FoodOn food ontology.

## Usage

### Python Script

The main script `list_ingredients.py` can be used to extract all ingredients from the FoodOn ontology:

```bash
# Show summary statistics
python3 list_ingredients.py --summary

# List all ingredients in text format (default)
python3 list_ingredients.py

# Export as CSV
python3 list_ingredients.py --format csv > ingredients.csv

# Export as JSON
python3 list_ingredients.py --format json > ingredients.json

# Use a different OWL file
python3 list_ingredients.py --owl-file /path/to/foodon.owl
```

### SPARQL Query

A SPARQL query is also available in `src/sparql/list_ingredients.sparql` that can be used with SPARQL engines that support OWL/RDF.

## What it Does

The script identifies ingredients by finding OWL class restrictions where:
- A food class has a restriction on the "has ingredient" property (FOODON_00002420)
- The restriction specifies that the food has some values from an ingredient class

## Output

The script provides:
- **Ingredient name**: Human-readable label for the ingredient
- **Ingredient URI**: Unique identifier in the ontology
- **Foods containing it**: List of food products that contain this ingredient

## Requirements

- Python 3.6+
- FoodOn ontology file (foodon-full.owl recommended)

## Example Output

```
INGREDIENTS FOUND IN FOODON ONTOLOGY
==================================================

Ingredient: salt
URI: http://purl.obolibrary.org/obo/CHEBI_26710
Found in 16 food(s):
  - beef bouillon (granulated)
  - bouillon cube
  - curing pickle poultry
  - ham cure
  ...
```