#!/usr/bin/env python3
"""
Author : Damion Dooley
Date   : 2025-08-26
Purpose: Fill in menu items of animals.tsv template 

run: ./menu.py -t animal_parts.tsv -i animals.tsv -o animals_test.tsv -m menus.tsv

"""

import argparse
import sys
import csv
import datetime
from collections import namedtuple
from collections import OrderedDict


# --------------------------------------------------
def get_args():
    """get command-line arguments"""
    parser = argparse.ArgumentParser(
        description='Argparse Python script',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        '-t',
        '--template',
        help='input template (e.g. animal_parts.tsv tsv file',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-i',
        '--input',
        help='input species list tsv file (e.g. animals.tsv)',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-o',
        '--output',
        help='output file path',
        metavar='str',
        type=str,
        default='')

    parser.add_argument(
        '-m',
        '--menu',
        help='input tsv file for menu lookup table',
        metavar='str',
        type=str,
        default='')

    return parser.parse_args()

# --------------------------------------------------
def main():
    """Create robot template from list of input species and generic template"""
    args = get_args()
    template_arg = args.template
    template_list = []
    species_list = []
    input_menus = OrderedDict();

    # Load template file (e.g. animal_parts.tsv) as list of OrderedDict
    with open(template_arg, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            template_list.append(row)

    # Load input species file as list of OrderedDict
    with open(args.input, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            species_list.append(row)

    # Load menu lookup table as list of OrderedDict

    with open(args.menu, mode='r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter='\t')
        for row in reader:
            if row['group'] == 'animal':
                input_menus[row['meaning']] = {
                    'menu': row['name'],
                    'title': row['title']
                }

    # write out robot template tsv file
    with open("animals_test.tsv", 'w', newline='', encoding='utf-8') as csv_file:
        # In order to slip mutiple value items into Google sheets, we only quote picklist items that have commas in them.
        writer = csv.writer(csv_file, delimiter='\t', quoting=csv.QUOTE_NONE, quotechar=None);

        header_1 = 'Compiled,animal_material_parent,species,Alternative_name,taxon,ID,template,product_category,GeneralAnimalMenu,AnimalAnatomyMenu,ButcheryMenu,AnimalOrganMenu,PieceOfAnimalMenu,Curation Notes,Requested by,Date when species was added,Version Tracking'.split(',');
        writer.writerow(header_1)

        for s in species_list:
            template = s['template'];

            # Filling in: GeneralAnimalMenu, AnimalAnatomyMenu, ButcheryMenu, AnimalOrganMenu, PieceOfAnimalMenu
            s['GeneralAnimalMenu'] = [];
            s['AnimalAnatomyMenu'] = [];
            s['ButcheryMenu'] = [];
            s['AnimalOrganMenu'] = [];      
            s['PieceOfAnimalMenu'] = [];               

            for index, item in enumerate(template_list):
                keep = '';
                if template == 'top': # Only 1 row for this, the species=="animal" row.
                    keep = 'animal' #args.organism; # The organism itself, so guaranteed match
                else:
                    # The animal_parts.csv column group of genus etc level animals to search within.
                    keep = item[str(template)]; 

                if keep != '': # and s['Compiled'] == 'TRUE': # 
                    filter_species = keep.split("|")
                    filter_species = [i for i in filter_species if i]
                    filter_species = [i.strip() for i in filter_species]
                    if s['species'] in filter_species or s['Alternative_name'] in filter_species or 'ALL' in filter_species:
                        if item['DISABLED'] != 'TRUE':
                            # We have a match to this animal_parts.csv row, so now calculate which menu to add this to.
                            menu = input_menus[item['ID']];
                            #print(s['species'], menu['menu'], menu['title']);
                            if ',' in menu['title']:
                                s[menu['menu']].append('"' + menu['title'] + '"');
                            else:
                                s[menu['menu']].append(menu['title']);


            #get printout of array without the leading and trailing brackets.
            #s['GeneralAnimalMenu']  = str(s['GeneralAnimalMenu'])[1:-1]; 
            #s['AnimalAnatomyMenu']  = str(s['AnimalAnatomyMenu'])[1:-1]; 
            #s['ButcheryMenu']       = str(s['ButcheryMenu'])[1:-1]; 
            #s['AnimalOrganMenu']    = str(s['AnimalOrganMenu'])[1:-1]; 
            #s['PieceOfAnimalMenu']  = str(s['PieceOfAnimalMenu'])[1:-1];  
            

            s['GeneralAnimalMenu']  = ','.join(s['GeneralAnimalMenu']);
            s['AnimalAnatomyMenu']  = ','.join(s['AnimalAnatomyMenu']);
            s['ButcheryMenu']       = ','.join(s['ButcheryMenu']);
            s['AnimalOrganMenu']    = ','.join(s['AnimalOrganMenu']);   
            s['PieceOfAnimalMenu']  = ','.join(s['PieceOfAnimalMenu']);    

            writer.writerow([s[f] for f in header_1]);

# --------------------------------------------------
if __name__ == '__main__':
    main()
