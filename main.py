import csv
import pandas as pd
import os

class Continent:
    instances = {}
    def __init__(self, name):
        self.instances[name] = self
        self.name = name
        self.superregions = []

class Superregion:
    instances = {}
    def __init__(self, continent: Continent, name):
        self.instances[name] = self
        continent.superregions.append(self)
        self.name = name
        self.regions = []
        self.countries = []

class Region:
    instances = {}
    def __init__(self, superregion: Superregion, name):
        self.instances[name] = self
        superregion.regions.append(self)
        self.name = name
        self.areas = []

class Area:
    instances = {}
    def __init__(self, region: Region, name):
        self.instances[name] = self
        region.areas.append(self)
        self.name = name
        self.provinces = []

class Province:
    instances = {}
    prov_num_dict = {}
    def __init__(self, area: Area, name, prov_num):
        self.instances[name] = self
        area.provinces.append(self)
        self.name = name
        self.prov_num_dict[prov_num] = self
        self.locations = []

class Location:
    instances = {}
    prov_num_dict = {}
    def __init__(self, province: Province, name, prov_num, hexcode):
        self.instances[name] = self
        province.locations.append(self)
        self.name = name
        self.prov_num_dict[prov_num] = self
        self.hexcode = hexcode
        self.owner = None
        self.cores = []

    def __repr__(self):
        return self.name

# Load transition data from csv files
def load_transition_data(csv_file, key_field, delimiter=','):
    transition_data = {}
    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file, delimiter=delimiter)
        for row in reader:
            key = row[key_field]  # Use the specified field as the key
            transition_data[key] = row
    return transition_data


# Applying tag relevant tag conversions.
tag_conversion_data = load_transition_data(csv_file='anbennar_eu5_transition_data_tag_conversion.csv',
                                           key_field='old_tag')

tag_conversion_dict = {}

for old_tag, values in tag_conversion_data.items():
    new_tag = values.get('new_tag', old_tag)
    tag_conversion_dict[old_tag] = new_tag

# Open locations.csv and apply tag conversions to owner and core fields
# Furthermore, append suffix to province and location_name fields if there are duplicates.
with open('anbennar_eu5_transition_data_locations.csv', 'r', encoding='utf-8-sig') as infile, \
    open('anbennar_eu5_transition_data_locations_converted.csv', 'w', encoding='utf-8-sig', newline='') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    seen_provinces = {}
    seen_locations = {}
    for row in reader:
        # Convert owner tag
        owner_tag = row.get('owner', '')
        if owner_tag in tag_conversion_dict:
            row['owner'] = tag_conversion_dict[owner_tag]
        
        # Convert core tags
        core_tags = row.get('cores', '').split(',')
        converted_core_tags = []
        for core_tag in core_tags:
            core_tag = core_tag.strip()
            if core_tag in tag_conversion_dict:
                converted_core_tags.append(tag_conversion_dict[core_tag])
            else:
                converted_core_tags.append(core_tag)
        row['cores'] = ','.join(converted_core_tags)

        # Append suffix to province if duplicate
        province_name = row.get('province', '')
        if province_name in seen_provinces:
            seen_provinces[province_name] += 1
            row['province'] = f"{province_name}_{seen_provinces[province_name]}"
        else:
            seen_provinces[province_name] = 1

        # Append suffix to location_name if duplicate
        location_name = row.get('location_name', '')
        if location_name in seen_locations:
            seen_locations[location_name] += 1
            row['location_name'] = f"{location_name}_{seen_locations[location_name]}"
        else:
            seen_locations[location_name] = 1

        writer.writerow(row)

# Open countries.csv and apply tag conversions to tag field
with open('anbennar_eu5_transition_data_countries.csv', 'r', encoding='utf-8-sig') as infile, \
    open('anbennar_eu5_transition_data_countries_converted.csv', 'w', encoding='utf-8-sig', newline='') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        # Convert country tag
        country_tag = row.get('tag', '')
        if country_tag in tag_conversion_dict:
            row['tag'] = tag_conversion_dict[country_tag]

        # Changing "not found" culture entries to "anbennarian"
        if row.get('culture_definition', '') == 'not found':
            row['culture_definition'] = 'anbennarian'

        writer.writerow(row)

# Open rulers.csv and apply tag conversions to tag field and the first 3 characters of character_tag field
with open('anbennar_eu5_transition_data_rulers.csv', 'r', encoding='utf-8-sig') as infile, \
    open('anbennar_eu5_transition_data_rulers_converted.csv', 'w', encoding='utf-8-sig', newline='') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    for row in reader:
        # Convert country tag
        country_tag = row.get('tag', '')
        if country_tag in tag_conversion_dict:
            row['tag'] = tag_conversion_dict[country_tag]
        
        # Convert first 3 characters of character_tag
        character_tag = row.get('character_tag', '')
        if len(character_tag) >= 3:
            char_country_tag = character_tag[:3]
            if char_country_tag in tag_conversion_dict:
                new_char_country_tag = tag_conversion_dict[char_country_tag]
                row['character_tag'] = new_char_country_tag + character_tag[3:]

        # Changing "not found" culture entries to "anbennarian"
        if row.get('culture', '') == 'not found':
            row['culture'] = 'anbennarian'

        writer.writerow(row)

data = load_transition_data(csv_file='anbennar_eu5_transition_data_locations_converted.csv', key_field='location_name')

# Replace - with _ in province and location_name fields
# Need to rebuild the dictionary with updated keys
# Also replace blank entries in superregion, region, and area with placeholders.
updated_data = {}
for key, value in data.items():
    value['province'] = value['province'].replace('-', '_').replace("'", "")
    value['location_name'] = value['location_name'].replace('-', '_').replace("'", "")
    if not value['superregion']:
        value['superregion'] = f'unknown_{value["continent"]}_superregion'

    if not value['region']:
        value['region'] = f'unknown_{value["superregion"]}_region'
    
    if not value['area']:
        value['area'] = f'unknown_{value["region"]}_area'

    # Use the updated location_name as the new key
    updated_data[value['location_name']] = value

data = updated_data

# Sort data by continent, superregion, region, area, and province
data = dict(sorted(data.items(), key=lambda item: (
    item[1].get('continent', ''),
    item[1].get('superregion', ''),
    item[1].get('region', ''),
    item[1].get('area', ''),
    item[1].get('province', '')
)))

# Populate classses.
for key, value in data.items():
    continent_name = value.get('continent')
    superregion_name = value.get('superregion')
    region_name = value.get('region')
    area_name = value.get('area')
    province_name = value.get('province')
    location_name = key
    hexcode = value.get('hexcode', 'unknown_hexcode')
    prov_num = int(value.get('old_province_number'))

    # Create or get Continent
    if continent_name in Continent.instances:
        if continent.name == '':
            continent.name = 'unknown_continent'
        continent = Continent.instances[continent_name]
    else:
        continent = Continent(continent_name)

    # Create or get Superregion
    if superregion_name in Superregion.instances:
        if superregion.name == '':
            superregion.name = f'unknown_{continent_name}_superregion'
        superregion = Superregion.instances[superregion_name]
    else:
        superregion = Superregion(continent, superregion_name)

    # Create or get Region
    if region_name in Region.instances:
        if region.name == '':
            region.name = f'unknown_{superregion_name}_region'
        region = Region.instances[region_name]
    else:
        region = Region(superregion, region_name)

    # Create or get Area
    if area_name in Area.instances:
        if area.name == '':
            area.name = f'unknown_{region_name}_area'
        area = Area.instances[area_name]
    else:
        area = Area(region, area_name) 
    
    # Create or get Province
    if province_name in Province.instances:
        # If province name is already in instances, append a suffix to make it unique.
        province_name += f'_{len(Province.instances)}'
        province = Province(area, province_name, prov_num)
    else:
        province = Province(area, province_name, prov_num)
    
    # Create Location
    if location_name in Location.instances:
        # If location name is already in instances, append a suffix to make it unique.
        location_name += f'_{len(Location.instances)}'
        location = Location(province, location_name, prov_num, hexcode)
    else:
        location = Location(province, location_name, prov_num, hexcode)


with open('output\\game\\in_game\\map_data\\named_locations\\00_default.txt', 'w', encoding='utf-8-sig') as outfile:
    for continent in Continent.instances.values():
        outfile.write('##### ' + continent.name + '\n')
        for superregion in continent.superregions:
            outfile.write('#### ' + superregion.name + '\n')
            for region in superregion.regions:
                outfile.write('### ' + region.name + '\n')
                for area in region.areas:
                    outfile.write('## ' + area.name + '\n')
                    for province in area.provinces:
                        outfile.write('# ' + province.name + '\n')
                        for location in province.locations:
                            outfile.write(f"{location.name} = {location.hexcode}\n")

with open('output\\game\\in_game\\map_data\\definitions.txt', 'w', encoding='utf-8-sig') as def_file:
    for continent in Continent.instances.values():
        def_file.write(f'{continent.name} = {{\n')
        for superregion in continent.superregions:
            def_file.write(f'\t{superregion.name} = {{\n')
            for region in superregion.regions:
                def_file.write(f'\t\t{region.name} = {{\n')
                for area in region.areas:
                    def_file.write(f'\t\t\t{area.name} = {{\n')
                    for province in area.provinces:
                        province_name_string = province.name
                        if not province_name_string.endswith('_province'):
                            province_name_string += '_province'
                        province_string = f'\t\t\t\t{province_name_string} = {{'
                        for location in province.locations:
                            province_string += f' {location.name}'
                        province_string += ' }\n'
                        def_file.write(province_string)
                    def_file.write('\t\t\t}\n')
                def_file.write('\t\t}\n')
            def_file.write('\t}\n')
        def_file.write('}\n')

with open('output\\game\\in_game\\map_data\\location_templates.txt', 'w', encoding='utf-8-sig') as template_file:
    for continent in Continent.instances.values():
        template_file.write(f'##### Continent: {continent.name}\n')
        for superregion in continent.superregions:
            template_file.write(f'#### Superregion: {superregion.name}\n')
            for region in superregion.regions:
                template_file.write(f'### Region: {region.name}\n')
                for area in region.areas:
                    template_file.write(f'## Area: {area.name}\n')
                    for province in area.provinces:
                        template_file.write(f'# Province: {province.name}\n')
                        for location in province.locations:
                            value = data[location.name]
                            name = value.get('location_name', 'unknown_location')
                            topography = value.get('topography', 'unknown_topography')
                            vegetation = value.get('vegetation', 'unknown_vegetation')
                            climate = value.get('climate', 'unknown_climate')
                            religion = value.get('religion', 'unknown_religion')
                            culture = value.get('culture', 'unknown_culture')
                            raw_material = value.get('raw_material', 'unknown_raw_material')
                            natural_harbor_suitability = value.get('natural_harbor_suitability', None)

                            location_template_string = f"{name} = {{ "
                            location_template_string += f"topography = {topography} "
                            if vegetation != '':
                                location_template_string += f"vegetation = {vegetation} "
                            location_template_string += f"climate = {climate} "
                            if religion != '':
                                location_template_string += f"religion = {religion} "
                            if culture != '':
                                if not culture.endswith('_culture'):
                                    culture += '_culture'
                                location_template_string += f"culture = {culture} "
                            if raw_material != '':
                                location_template_string += f"raw_material = {raw_material} "
                            if natural_harbor_suitability != '':
                                location_template_string += f"natural_harbor_suitability = {natural_harbor_suitability} "
                            location_template_string += "}\n"
                            
                            template_file.write(location_template_string)

religious_groups_data = load_transition_data(csv_file='anbennar_eu5_transition_data_religious_groups.csv', 
                                             key_field='religious_group')
religions_data = load_transition_data(csv_file='anbennar_eu5_transition_data_religions.csv',
                                      key_field='religion')

with open('output//game//in_game//common//religion_groups//anb_default.txt', 'w', encoding='utf-8-sig') as religious_groups_file:
    for key, value in religious_groups_data.items():
        color = value.get('color', '255 255 255').strip('(').strip(')').replace(',', '')
        string = f'{key} = {{\n'
        string += f'\tcolor = rgb {{ {color} }}\n'
        string += f'\tconvert_slaves_at_start = {value.get("convert_slaves_at_start", "no")}\n'
        string += '}\n\n'

        religious_groups_file.write(string)

# Load template as base for religion files.
with open('templates/anb_religion_template.txt', 'r', encoding='utf-8') as f:
    religion_placeholder_template = f.read()

class ReligiousGroup:
    instances = {}
    def __init__(self, name):
        self.instances[name] = self
        self.name = name
        self.religions = []

class Religion:
    instances = {}
    def __init__(self, religious_group: ReligiousGroup, name):
        self.instances[name] = self
        religious_group.religions.append(self)
        self.name = name

# Populate classes.
for key, value in religions_data.items():
    religious_group_name = value.get('religious_group', 'unknown_religious_group')
    religion_name = key

    # Create or get ReligiousGroup
    if religious_group_name in ReligiousGroup.instances:
        religious_group = ReligiousGroup.instances[religious_group_name]
    else:
        religious_group = ReligiousGroup(religious_group_name)

    # Create Religion
    religion = Religion(religious_group, religion_name)


for religious_group in ReligiousGroup.instances.values():
    with open('output//game//in_game//common//religions//' + religious_group.name +'.txt', 'w', encoding='utf-8-sig') as group_file:
        for religion in religious_group.religions:            
            # Get the data for THIS specific religion
            religion_data = religions_data[religion.name]
            
            new_string = str(religion_placeholder_template)
            new_string = new_string.replace('PH_RELIGION_NAME', religion.name)
            new_string = new_string.replace('PH_RELIGION_GROUP', religious_group.name)
            
            color = religion_data.get('color', '255 255 255').strip('(').strip(')').replace(',', '')
            new_string = new_string.replace('PH_RELIGION_COLOR', f'rgb {{ {color} }}')
            
            if religion_data.get('enable', '') != '':
                new_string = new_string.replace('PH_ENABLE', f'\n\tenable = {religion_data.get("enable", "no")}\n')
            else:
                new_string = new_string.replace('PH_ENABLE', '')

            group_file.write(new_string)

cultures_data = load_transition_data(csv_file='anbennar_eu5_transition_data_culture.csv',
                                     key_field='culture')

# Load template as base for culture files.
with open('templates/anb_culture_template.txt', 'r', encoding='utf-8') as f:
    culture_placeholder_template = f.read()

# Classes for cultures
class CultureGroup:
    instances = {}
    def __init__(self, name):
        self.instances[name] = self
        self.name = name
        self.cultures = []

class Culture:
    instances = {}
    def __init__(self, culture_group: CultureGroup, name):
        self.instances[name] = self
        culture_group.cultures.append(self)
        self.name = name

# Populate classes.
for key, value in cultures_data.items():
    culture_group_name = value.get('culture_groups', 'unknown_culture_group')
    culture_name = key

    # Create or get CultureGroup
    if culture_group_name in CultureGroup.instances:
        culture_group = CultureGroup.instances[culture_group_name]
    else:
        culture_group = CultureGroup(culture_group_name)

    # Create Culture
    culture = Culture(culture_group, culture_name)

# Generate culture files
with open('output//game//in_game//common//culture_groups//00_culture_groups.txt', 'w', encoding='utf-8-sig') as culture_groups_file:
    for culture_group in CultureGroup.instances.values():
        culture_group_name = culture_group.name
        if culture_group_name.endswith('_group'):
            culture_group_name = culture_group_name[:-6] + '_culture_group'
        elif not culture_group_name.endswith('_culture_group'):
            culture_group_name += '_culture_group'

        culture_groups_file.write(f'{culture_group_name} = {{\n')
        culture_groups_file.write('\t# country_modifier = { }\n')
        culture_groups_file.write('\t# character_modifier = { }\n')
        culture_groups_file.write('\t# location_modifier = { }\n')
        culture_groups_file.write('}\n')
        culture_groups_file.write('\n')
        
        with open('output//game//in_game//common//cultures//' + culture_group.name +'.txt', 'w', encoding='utf-8-sig') as group_file:
            for culture in culture_group.cultures:
                culture_data = cultures_data[culture.name]

                culture_name = culture.name
                if not culture_name.endswith('_culture'):
                    culture_name += '_culture'
                
                new_string = str(culture_placeholder_template)
                new_string = new_string.replace('PH_CULTURE_NAME', culture_name)
                new_string = new_string.replace('PH_CULTURE_GROUP', culture_group_name)
                
                language = culture_data.get('language/dialect', 'unknown_language')
                new_string = new_string.replace('PH_LANGUAGE_NAME', language)
                
                color = culture_data.get('color', '255 255 255').strip('(').strip(')').replace(',', '')
                new_string = new_string.replace('PH_COLOR', f'rgb {{ {color} }}')

                group_file.write(new_string)

# Load languages and dialects.
languages_data = load_transition_data(csv_file='anbennar_eu5_transition_data_language.csv',
                                      key_field='language')
dialects_data = load_transition_data(csv_file='anbennar_eu5_transition_data_dialects.csv',
                                     key_field='dialect')

# Classes
class Language:
    instances = {}
    def __init__(self, name):
        self.instances[name] = self
        self.name = name
        self.dialects = []

class Dialect:
    instances = {}
    def __init__(self, language: Language, name):
        self.instances[name] = self
        language.dialects.append(self)
        self.name = name

# Populate classes
for key, value in languages_data.items():
    language_name = key

    # Create Language
    language = Language(language_name)

for key, value in dialects_data.items():
    language_name = value.get('language', 'unknown_language')
    dialect_name = key

    # Get Language
    if language_name in Language.instances:
        language = Language.instances[language_name]
    else:
        language = Language(language_name)

    # Create Dialect
    dialect = Dialect(language, dialect_name)

# Load templates
with open('templates/anb_language_template.txt', 'r', encoding='utf-8') as f:
    language_placeholder_template = f.read()

with open('templates/anb_dialect_template.txt', 'r', encoding='utf-8') as f:
    dialect_placeholder_template = f.read()

# Generate language and dialect files
for language in Language.instances.values():
    with open('output//game//in_game//common//languages//' + language.name +'.txt', 'w', encoding='utf-8-sig') as lang_file:
        # Language template
        language_data = languages_data.get(language.name, {})
        language_string = str(language_placeholder_template)
        language_string = language_string.replace('PH_LANGUAGE_NAME', language.name)
        
        color = language_data.get('color', '255 255 255').strip('(').strip(')').replace(',', '')
        language_string = language_string.replace('PH_COLOR', f'rgb {{ {color} }}')

        dialects_string = ''

        # Dialects
        for dialect in language.dialects:
            dialect_data = dialects_data.get(dialect.name, {})
            new_dialect_string = str(dialect_placeholder_template)
            new_dialect_string = new_dialect_string.replace('PH_DIALECT', dialect.name)
            
            dialects_string += new_dialect_string
            if dialect != language.dialects[-1]:
                dialects_string += '\n'

        language_string = language_string.replace('PH_DIALECTS', dialects_string)

        lang_file.write(language_string)

# Load countries
countries_data = load_transition_data(csv_file='anbennar_eu5_transition_data_countries_converted.csv',
                                      key_field='tag')

# Generate country setup files
with open('templates/anb_country_setup_template.txt', 'r', encoding='utf-8') as f:
    country_placeholder_template = f.read()

unknown_superregion = Superregion(Continent('unknown_continent'), 'unknown_superregion')

# Generating loc for continents, superregions, regions, areas, provinces, locations
with open ('input\\loc\\continents.yml', 'r', encoding='utf-8-sig') as infile:
    lines = infile.readlines()
    for line in lines:
        line = line.split('#')[0]  # Remove comments
        if len(line.strip()) == 0:
            continue

        if line.startswith('l_english:'):
            continue
        else:
            parts = line.split(':')
            continent_name = parts[0].strip()
            continent_loc = parts[1][1:] # We don't care about the 0 (or in one instance, 2) following the colon
            continent_loc = continent_loc.removesuffix('\n') # Remove newline character, as some lines lose it when comments are removed.

            Continent.instances[continent_name].loc = f'{continent_name}:{continent_loc}'

with open('input\\loc\\anb_regions_l_english.yml', 'r', encoding='utf-8-sig') as infile:
    lines = infile.readlines()
    for line in lines:
        line = line.split('#')[0]  # Remove comments
        if len(line.strip()) == 0:
            continue

        if line.startswith('l_english:'):
            continue
        else:
            parts = line.split(':')
            name = parts[0].strip()
            loc = parts[1][1:] # We don't care about the 0 (or in one instance, 2) following the colon
            loc = loc.removesuffix('\n') # Remove newline character, as some lines lose it when comments are removed.

            if name in Region.instances:
                Region.instances[name].loc = f'{name}:{loc}'
            elif name in Superregion.instances:
                Superregion.instances[name].loc = f'{name}:{loc}'

with open('input\\loc\\anb_areas_l_english.yml', 'r', encoding='utf-8-sig') as infile:
    lines = infile.readlines()
    for line in lines:
        line = line.split('#')[0]  # Remove comments
        if len(line.strip()) == 0:
            continue

        if line.startswith('l_english:'):
            continue
        else:
            parts = line.split(':')
            name = parts[0].strip()

            if name.endswith('_name') or name.endswith('_adj'):
                continue

            loc = parts[1][1:] # We don't care about the 0 (or in one instance, 2) following the colon
            loc = loc.removesuffix('\n') # Remove newline character, as some lines lose it when comments are removed.

            if name in Area.instances:
                Area.instances[name].loc = f'{name}:{loc}'

with open('input\\loc\\prov_names_l_english.yml', 'r', encoding='utf-8-sig') as infile:
    lines = infile.readlines()
    for line in lines:
        line = line.split('#')[0]  # Remove comments
        if len(line.strip()) == 0:
            continue

        if line.startswith('l_english:'):
            continue
        else:
            parts = line.split(':')
            
            prov_num = parts[0].strip().replace("PROV", "")
            # Check that prov_num is a valid integer, if not continue.
            try:
                prov_num = int(prov_num)
            except ValueError:
                continue
            
            if prov_num not in Province.prov_num_dict:
                continue

            prov_name = Province.prov_num_dict[prov_num].name
            prov_loc = parts[1][1:] # We don't care about the 0 (or in one instance, 2) following the colon
            prov_loc = prov_loc.removesuffix('\n') # Remove newline character, as some lines lose it when comments are removed.
            prov_loc = prov_loc.replace('_', ' ')  # Replace underscores with spaces for loc

            Province.prov_num_dict[prov_num].loc = f'{prov_name}_province:{prov_loc}'
            Location.prov_num_dict[prov_num].loc = f'{prov_name}:{prov_loc}'

# Set loc for unknown continents, superregions, regions, and areas
for continent in Continent.instances.values():
    if not hasattr(continent, 'loc'):
        continent.loc = f'{continent.name}: "UNKNOWN CONTINENT"'
    for superregion in continent.superregions:
        if not hasattr(superregion, 'loc'):
            superregion.loc = f'{superregion.name}: "UNKNOWN SUPERREGION"'
        for region in superregion.regions:
            if not hasattr(region, 'loc'):
                region.loc = f'{region.name}: "UNKNOWN REGION"'
            for area in region.areas:
                if not hasattr(area, 'loc'):
                    area.loc = f'{area.name}: "UNKNOWN AREA"'

with open('output\\game\\main_menu\\localization\\english\\province_names_l_english.yml', 'w', encoding='utf-8-sig') as province_loc_file, \
     open('output\\game\\main_menu\\localization\\english\\location_names\\location_names_l_english.yml', 'w', encoding='utf-8-sig') as location_loc_file, \
     open('output\\game\\main_menu\\localization\\english\\area_l_english.yml', 'w', encoding='utf-8-sig') as area_loc_file, \
     open('output\\game\\main_menu\\localization\\english\\region_names_l_english.yml', 'w', encoding='utf-8-sig') as region_loc_file:

    province_loc_file.write('l_english:\n')
    location_loc_file.write('l_english:\n')
    area_loc_file.write('l_english:\n')
    region_loc_file.write('l_english:\n')

    for continent in Continent.instances.values():
        location_loc_file.write(f' ##### Continent: {continent.name}\n')
        province_loc_file.write(f' #### Continent: {continent.name}\n')
        area_loc_file.write(f' ### Continent: {continent.name}\n')
        region_loc_file.write(f' ## Continent: {continent.name}\n')
        region_loc_file.write(' ' + continent.loc + '\n')
        for superregion in continent.superregions:
            location_loc_file.write(f' #### Superregion: {superregion.name}\n')
            province_loc_file.write(f' ### Superregion: {superregion.name}\n')
            area_loc_file.write(f' ## Superregion: {superregion.name}\n')
            region_loc_file.write(f' # Superregion: {superregion.name}\n')
            region_loc_file.write(' ' + superregion.loc + '\n')
            for region in superregion.regions:
                location_loc_file.write(f' ### Region: {region.name}\n')
                province_loc_file.write(f' ## Region: {region.name}\n')
                area_loc_file.write(f' # Region: {region.name}\n')
                region_loc_file.write(' ' + region.loc + '\n')
                for area in region.areas:
                    location_loc_file.write(f' ## Area: {area.name}\n')
                    province_loc_file.write(f' # Area: {area.name}\n')
                    area_loc_file.write(' ' + area.loc + '\n')
                    for province in area.provinces:
                        location_loc_file.write(f' # Province: {province.name}\n')
                        if hasattr(province, 'loc'):
                            province_loc_file.write(' ' + province.loc + '\n')
                        for location in province.locations:
                            if hasattr(location, 'loc'):
                                location_loc_file.write(' ' + location.loc + '\n')

class Country:
    instances = {}
    def __init__(self, superregion, tag):
        superregion.countries.append(self)
        self.instances[tag] = self
        self.tag = tag
        self.owned_non_core_provinces = []
        self.owned_core_provinces = []
        self.unowned_core_provinces = []

for key, value in countries_data.items():
    superregion_name = value.get('capital_superregion', 'unknown_superregion')
    country_tag = key

    # Get Superregion
    if superregion_name in Superregion.instances:
        superregion = Superregion.instances[superregion_name]
    else:
        superregion = unknown_superregion

    # Create Country
    country = Country(superregion, country_tag)

for superregion in Superregion.instances.values():
    with open('output//game//in_game//setup//countries//' + superregion.name +'.txt', 'w', encoding='utf-8-sig') as superregion_file:
        for country in superregion.countries:
            country_tag = country.tag
            country_data = countries_data.get(country_tag, {})

            color = country_data.get('color', '255 255 255').strip('(').strip(')').replace(',', '')
            new_string = str(country_placeholder_template)
            new_string = new_string.replace('PH_COUNTRY_TAG', country_tag)
            new_string = new_string.replace('PH_COLOR', f'rgb {{ {color} }}')
            
            culture = country_data.get('culture_definition', 'unknown_culture')
            if culture == '':
                culture = 'anbennarian_culture' # Placeholder default culture
            if not culture.endswith('_culture'):
                culture += '_culture'
            new_string = new_string.replace('PH_CULTURE', culture)
            
            religion = country_data.get('religion_definition', 'unknown_religion')
            if religion == '':
                religion = 'regent_court' # Placeholder default religion
            new_string = new_string.replace('PH_RELIGION', religion)

            superregion_file.write(new_string)

# Load rulers
rulers = load_transition_data(csv_file='anbennar_eu5_transition_data_rulers_converted.csv',
                              key_field='character_tag')

# Sort by tag_continent, tag_superregion, tag, character_tag
rulers = dict(sorted(rulers.items(), key=lambda item: (
    item[1].get('tag_continent', ''),
    item[1].get('tag_superregion', ''),
    item[1].get('tag', ''),
    item[0]
)))

with open('templates/anb_character_template.txt', 'r', encoding='utf-8') as f:
    character_placeholder_template = f.read()

with open('output\\game\\main_menu\\setup\\start\\05_anb_characters.txt', 'w', encoding='utf-8-sig') as rulers_file:
    for key, value in rulers.items():
        new_string = str(character_placeholder_template)
        new_string = new_string.replace('PH_CHARACTER_TAG', key)
        new_string = new_string.replace('PH_FIRST_NAME', value.get('first_name', '???'))
        if value.get('nickname', '') != '':
            nickname_string = f'\t\tnickname = {{ {value.get("nickname")} }}'
            nickname_string = nickname_string.replace("'", "")
            new_string = new_string.replace('PH_NICKNAME', nickname_string)
        else:
            new_string = new_string.replace('PH_NICKNAME\n', '')

        culture_string = value.get('culture', '???')
        if not culture_string.endswith('_culture'):
            culture_string += '_culture'
        new_string = new_string.replace('PH_CULTURE', culture_string)
        
        new_string = new_string.replace('PH_RELIGION', value.get('religion', '???'))
        if value.get('female', 'probably_male') == 'yes':
            new_string = new_string.replace('PH_FEMALE', '\t\tfemale = yes')
        else:
            new_string = new_string.replace('PH_FEMALE\n', '')
        if value.get('adm', '') != 0:
            adm = value.get('adm', '0')
            dip = value.get('dip', '0')
            mil = value.get('mil', '0')
            new_string = new_string.replace('PH_STATS', f'\t\tadm = {adm} dip = {dip} mil = {mil}')
        else:
            new_string = new_string.replace('PH_STATS\n', '')
        new_string = new_string.replace('PH_BIRTH_DATE', value.get('birth_date', '1.1.1'))
        if value.get('death_date', '') != '':
            new_string = new_string.replace('PH_DEATH_DATE', f'\t\tdeath_date = {value.get("death_date")}')
        else:
            new_string = new_string.replace('PH_DEATH_DATE\n', '')
        if value.get('ruler_term_start', '') != '':
            new_string = new_string.replace('PH_REIGN_START', f'\t\truler_term_start = {value.get("ruler_term_start")}')
        else:
            new_string = new_string.replace('PH_REIGN_START\n', '')
        if value.get('ruler_term_end', '') != '':
            new_string = new_string.replace('PH_REIGN_END', f'\t\truler_term_end = {value.get("ruler_term_end")}')
        else:
            new_string = new_string.replace('PH_REIGN_END\n', '')
        new_string = new_string.replace('PH_PLACE_OF_BIRTH', value.get('birth_place', '???'))
        new_string = new_string.replace('PH_DYNASTY', value.get('dynasty', '???'))
        new_string = new_string.replace('PH_TAG', value.get('tag', '???'))

        new_string = new_string.replace('-', '_')

        rulers_file.write(new_string)

# Creating 10_countries.txt
locations_data = data

# Assign rulers to countries
ruler_dicts = {}
for key, value in rulers.items():
    country_tag = value.get('tag', '')
    if country_tag not in ruler_dicts:
        ruler_dicts[country_tag] = {}
    ruler_dicts[country_tag][key] = value

# Assign ownership and cores.
for location_key, location_values in locations_data.items():
    location = Location.instances.get(location_key)
    location_owner_tag = location_values.get('owner', '')
    location_owner_country = Country.instances.get(location_owner_tag)

    location_core_tags = location_values.get('cores', '').split(',')
    for core_tag in location_core_tags:
        core_country = Country.instances.get(core_tag)
        if core_country:
            location.cores.append(core_country)

    if location_owner_country:
        location.owner = location_owner_country
        if location_owner_tag in location_core_tags:
            location_owner_country.owned_core_provinces.append(location)
        else:
            location_owner_country.owned_non_core_provinces.append(location)
    for core_tag in location_core_tags:
        if core_tag != location_owner_tag:
            core_country = Country.instances.get(core_tag)
            if core_country:
                core_country.unowned_core_provinces.append(location)

with open('templates/anb_10_countries_template_file.txt', 'r', encoding='utf-8') as f:
    entire_file_template = f.read()

with open('templates/anb_10_countries_template_country.txt', 'r', encoding='utf-8') as f:
    single_country_template = f.read()

with open('output\\game\\main_menu\\setup\\start\\10_countries.txt', 'w', encoding='utf-8-sig') as country_setup_file:
    output_string = str(entire_file_template)
    countries_string = ''
    for country in Country.instances.values():
        country_data = countries_data.get(country.tag, {})
        country_string = str(single_country_template)
        country_string = country_string.replace('PH_COUNTRY_TAG', country.tag)
        capital = country_data.get('capital', 'unknown_capital')
        country_string = country_string.replace('PH_CAPITAL', capital)
        court_language = country_data.get('court_language', 'unknown_court_language')
        country_string = country_string.replace('PH_COURT_LANGUAGE', court_language)

        owned_non_core_provinces_strings = ''
        for province in country.owned_non_core_provinces:
            owned_non_core_provinces_strings += f'\t\t{province.name}'
            if province != country.owned_non_core_provinces[-1]:
                owned_non_core_provinces_strings += '\n'
        if owned_non_core_provinces_strings != '':
            country_string = country_string.replace('PH_OWNED_NON_CORE_PROVINCES', owned_non_core_provinces_strings)
        else:
            country_string = country_string.replace('PH_OWNED_NON_CORE_PROVINCES\n', '')

        owned_core_provinces_strings = ''
        for province in country.owned_core_provinces:
            owned_core_provinces_strings += f'\t\t{province.name}'
            if province != country.owned_core_provinces[-1]:
                owned_core_provinces_strings += '\n'
        if owned_core_provinces_strings != '':
            country_string = country_string.replace('PH_OWNED_CORE_PROVINCES', owned_core_provinces_strings)
        else:
            country_string = country_string.replace('PH_OWNED_CORE_PROVINCES\n', '')

        unowned_core_provinces_strings = ''
        for province in country.unowned_core_provinces:
            unowned_core_provinces_strings += f'\t\t{province.name}'
            if province != country.unowned_core_provinces[-1]:
                unowned_core_provinces_strings += '\n'
        if unowned_core_provinces_strings != '':
            country_string = country_string.replace('PH_UNOWNED_CORE_PROVINCES', unowned_core_provinces_strings)
        else:
            country_string = country_string.replace('PH_UNOWNED_CORE_PROVINCES\n', '')

        # Ruler terms.
        ruler_terms_string = ''
        # Sort rulers by start date of reign
        sorted_rulers = sorted(ruler_dicts.get(country.tag, {}).items(), key=lambda item: item[1].get('ruler_term_start', ''))

        for ruler_key, ruler_value in sorted_rulers:
            character = ruler_key
            term_start = ruler_value.get('ruler_term_start', '')
            term_end = ruler_value.get('ruler_term_end', '')
            regnal_number = ruler_value.get('regnal_number', '')
            ruler_terms_string += f'\t\truler_term = {{ character = {ruler_key} start_date = {term_start} TERM_END_PLACEHOLDER REGNAL_NUMBER_PLACEHOLDER }}\n'
            if term_end != '':
                ruler_terms_string = ruler_terms_string.replace('TERM_END_PLACEHOLDER', f'end_date = {term_end}')
            else:
                ruler_terms_string = ruler_terms_string.replace('TERM_END_PLACEHOLDER ', '')

            if regnal_number != '':
                ruler_terms_string = ruler_terms_string.replace('REGNAL_NUMBER_PLACEHOLDER', f'regnal_number = {regnal_number[0]}')
            else:
                ruler_terms_string = ruler_terms_string.replace('REGNAL_NUMBER_PLACEHOLDER ', '')

        country_string = country_string.replace('PH_RULER_TERMS', ruler_terms_string)

        countries_string += country_string + '\n'

    countries_string = countries_string.replace('\n', '\n\t\t')

    output_string = output_string.replace('PH_COUNTRIES', countries_string)
    country_setup_file.write(output_string)

with open('sea_zones.txt', 'w', encoding='utf-8') as f:
    for location in locations_data.values():
        if location.get('location_type', '') == 'sea':
            f.write('\t' + location.get('location_name', '') + '\n')

with open('wasteland.txt', 'w', encoding='utf-8') as f:
    for location in locations_data.values():
        if location.get('topography', '').endswith('_wasteland'):
            f.write('\t' + location.get('location_name', '') + '\n')