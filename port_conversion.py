import csv

top_margin = 731
bottom_margin = 1503

old_height = 2048
old_width = 5632

new_height = 8192
new_width = 16384
actual_height = new_height - top_margin - bottom_margin


def convert_coords(x, y):
    new_x = int((x / old_width) * new_width)
    new_y = int((y / old_height) * actual_height) + bottom_margin
    return new_x, new_y


with open('input\\eu4_ports.csv', 'r', encoding='utf-8') as infile, \
    open('output\\game\\in_game\\map_data\\eu5_ports.csv', 'w', encoding='utf-8', newline='') as outfile:
    reader = csv.DictReader(infile, delimiter=';')
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=';')
    writer.writeheader()
    
    for row in reader:
        x = int(row.get('x'))
        y = int(row.get('y'))
        new_x, new_y = convert_coords(x, y)
        row['x'] = new_x
        row['y'] = new_y
        writer.writerow(row)

# Open output file and strip the newline from the final line.
with open('output\\game\\in_game\\map_data\\eu5_ports.csv', 'r', encoding='utf-8') as outfile:
    lines = outfile.readlines()
with open('output\\game\\in_game\\map_data\\eu5_ports.csv', 'w', encoding='utf-8', newline='') as outfile:
    outfile.writelines(lines[:-1])
    outfile.write(lines[-1].rstrip('\n'))
