Run from console:
---
1. Choose sites with sale offer (avito.ru, upn.ru, youla.ru)

    `python flat_parser avtio|upn|jula custom_output.csv(optional)`

2. Get addtional info about house (domaekb.ru)

    `python flat_parser domaekb custom_input.csv custom_output.csv(optional)`

3. Get addtional info about location (google.com/maps)

    `python flat_parser google_maps custom_input.csv custom_output.csv(optional)`

4. Convert multi value variables into binary varaibles

    `python flat_parser binarized custom_input.csv custom_output.csv(optional)`

Task output file is input file for next process