#!/usr/bin/env python3
"""
List ingredients from FoodOn ontology.

This script extracts all ingredients mentioned in the FoodOn food ontology
by parsing the OWL file and finding relationships where foods have ingredients.
"""

import sys
import re
import argparse
from collections import defaultdict


def extract_ingredients_from_owl(owl_file_path):
    """
    Extract ingredients from OWL file by parsing 'has ingredient' relationships.
    
    Args:
        owl_file_path: Path to the FoodOn OWL file
        
    Returns:
        Dictionary mapping ingredient URIs to their labels and the foods that contain them
    """
    ingredients_data = defaultdict(lambda: {"label": None, "foods": []})
    
    try:
        with open(owl_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find all 'has ingredient' relationships (FOODON_00002420) in OWL restrictions
        # Pattern: <owl:Class rdf:about="FOOD_URI">...<owl:onProperty rdf:resource="FOODON_00002420"/>
        #          <owl:someValuesFrom rdf:resource="INGREDIENT_URI"/>
        
        # Split content into class definitions
        class_pattern = r'<owl:Class rdf:about="([^"]+)"[^>]*>(.*?)</owl:Class>'
        class_matches = re.findall(class_pattern, content, re.DOTALL)
        
        # Find all labels
        label_pattern = r'<rdfs:label[^>]*xml:lang="en"[^>]*>([^<]+)</rdfs:label>'
        label_matches = re.findall(label_pattern, content)
        
        # Also find labels in the alternative format
        label_pattern2 = r'<([^>]+)>\s+<http://www.w3.org/2000/01/rdf-schema#label>\s+"([^"]*)"(?:@en)?'
        label_matches2 = re.findall(label_pattern2, content)
        
        # Create a mapping of URIs to labels
        uri_to_label = {}
        
        # Process labels from pattern 1
        for class_uri, class_content in class_matches:
            label_match = re.search(r'<rdfs:label[^>]*xml:lang="en"[^>]*>([^<]+)</rdfs:label>', class_content)
            if label_match:
                uri_to_label[class_uri] = label_match.group(1)
        
        # Process labels from pattern 2
        for uri, label in label_matches2:
            uri_to_label[uri] = label
        
        # Process each class to find ingredient relationships
        for food_uri, class_content in class_matches:
            # Look for ingredient restrictions in this class
            restriction_pattern = r'<owl:onProperty rdf:resource="http://purl\.obolibrary\.org/obo/FOODON_00002420"/>\s*<owl:someValuesFrom rdf:resource="([^"]+)"/>'
            ingredient_matches = re.findall(restriction_pattern, class_content)
            
            for ingredient_uri in ingredient_matches:
                ingredient_label = uri_to_label.get(ingredient_uri, ingredient_uri.split('/')[-1])
                food_label = uri_to_label.get(food_uri, food_uri.split('/')[-1])
                
                # Skip if this is a deprecated class
                if 'owl:deprecated' in class_content and 'true' in class_content:
                    continue
                
                if ingredients_data[ingredient_uri]["label"] is None:
                    ingredients_data[ingredient_uri]["label"] = ingredient_label
                
                ingredients_data[ingredient_uri]["foods"].append({
                    "uri": food_uri,
                    "label": food_label
                })
    
    except FileNotFoundError:
        print(f"Error: Could not find file {owl_file_path}")
        return {}
    except Exception as e:
        print(f"Error processing file: {e}")
        return {}
    
    return dict(ingredients_data)


def format_ingredients_output(ingredients_data, output_format="text"):
    """
    Format the ingredients data for output.
    
    Args:
        ingredients_data: Dictionary of ingredient data
        output_format: Output format ("text", "csv", "json")
    """
    if not ingredients_data:
        print("No ingredients found in the ontology.")
        return
    
    if output_format == "text":
        print("INGREDIENTS FOUND IN FOODON ONTOLOGY")
        print("=" * 50)
        print()
        
        for ingredient_uri, data in sorted(ingredients_data.items(), 
                                         key=lambda x: x[1]["label"] or ""):
            ingredient_label = data["label"] or ingredient_uri.split('/')[-1]
            foods_count = len(data["foods"])
            
            print(f"Ingredient: {ingredient_label}")
            print(f"URI: {ingredient_uri}")
            print(f"Found in {foods_count} food(s):")
            
            for food in sorted(data["foods"], key=lambda x: x["label"]):
                print(f"  - {food['label']}")
            print()
    
    elif output_format == "csv":
        print("ingredient_label,ingredient_uri,food_label,food_uri")
        for ingredient_uri, data in ingredients_data.items():
            ingredient_label = data["label"] or ingredient_uri.split('/')[-1]
            for food in data["foods"]:
                print(f'"{ingredient_label}","{ingredient_uri}","{food["label"]}","{food["uri"]}"')
    
    elif output_format == "json":
        import json
        print(json.dumps(ingredients_data, indent=2))


def main():
    parser = argparse.ArgumentParser(description="List ingredients from FoodOn ontology")
    parser.add_argument("--owl-file", 
                       default="/home/runner/work/foodon/foodon/foodon-full.owl",
                       help="Path to FoodOn OWL file (default: foodon-full.owl)")
    parser.add_argument("--format", 
                       choices=["text", "csv", "json"],
                       default="text",
                       help="Output format (default: text)")
    parser.add_argument("--summary", 
                       action="store_true",
                       help="Show only summary statistics")
    
    args = parser.parse_args()
    
    print("Extracting ingredients from FoodOn ontology...")
    ingredients_data = extract_ingredients_from_owl(args.owl_file)
    
    if args.summary:
        total_ingredients = len(ingredients_data)
        total_relationships = sum(len(data["foods"]) for data in ingredients_data.values())
        print(f"Summary:")
        print(f"Total unique ingredients: {total_ingredients}")
        print(f"Total ingredient relationships: {total_relationships}")
    else:
        format_ingredients_output(ingredients_data, args.format)


if __name__ == "__main__":
    main()