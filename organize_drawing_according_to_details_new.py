import re

def get_details(result): #search for all details in drawing and store it in list details, first need to append all text elements of one line and then check if regular expression is found in this text element
    reg = r"([A-Z])-\1|([A-Z]\W?[A-Z]?\s?\W\s?\d\d?\s?\s?:\s?\d\d?\s?\W)"
    details = []
    for element in result:
        new = []
        if re.search(reg,element):
            new.extend(result[element])
            new.append(element)
            details.append(new)
    number = len(details)
    return details, number

def get_borders(details, tables):
    sections = []
    #print(coords)
    for first in details:
        x_min = -1
        y_min = -1
        x_max = -1
        y_max = -1
        firstx_max = first[2]
        firstx_min = first[0]
        firsty_max = first[3]
        firsty_min = first[1]

        distance_xmax = 100000000000
        distance_xmin = 100000000000
        distance_ymin = 100000000000
        distance_ymax = 100000000000

        for second in details:
            secondx_min = second[0]
            secondx_max = second[2]
            secondy_min = second[1]
            secondy_max = second[3]

            if secondx_max < firstx_min and abs(firsty_min-secondy_min) < 90 and first != second:  ###check for left side, are there any other details at the left side at a certain y-span
                if abs(firstx_min - secondx_max)/2 < distance_xmax:
                    distance_xmax = abs(firstx_min - secondx_max)/2
                    x_min = secondx_max + distance_xmax
            if secondx_min > firstx_max and abs(firsty_min-secondy_min) < 190 and first != second: ####check for right side
                if abs(secondx_min - firstx_max)/2 < distance_xmin:
                    distance_xmin = abs(secondx_min - firstx_max)/2
                    x_max = firstx_max + distance_xmin
            if firsty_min > secondy_max and abs(firstx_min-secondx_min) < 80 and first != second: ####check above
                if abs(firsty_min - secondy_max)/2 < distance_ymin:
                    distance_ymin = abs(firsty_min - secondy_max)/2
                    y_min = firsty_min
            if firsty_max < secondy_min and abs(firstx_min-secondx_min) < 80 and first != second: ####check below
                if abs(firsty_max - secondy_min)/2 < distance_ymax:
                    distance_ymax = abs(firsty_max - secondy_min)/2
                    y_max = secondy_min



        if y_min == -1:
            y_min = firsty_min
        if x_min == -1:
            x_min = 0
        if x_max == -1:
            x_max = firstx_max + distance_xmax
        if y_max == -1:
            y_max = 1000000000

        ##check if it intersects with tables
        for table in tables:
            table_xmin = table[0]
            if "Start drawing" in table[4]:
                table_xmax = 100000000
            else:
                table_xmax = table[2]
            table_ymin = table[1]
            if y_max > table_ymin:
                if table_xmin < firstx_min < table_xmax:
                    y_max = table_ymin
                elif table_xmin < x_max < table_xmax:
                    y_max = table_ymin

        sections.append((first,x_min, y_min,x_max,y_max))

    """for section in sections:
        print(section)"""
    return sections

def intersects(detail, rectangle): #using the separating axis theorem

    rect1_bottom_left_x = float(detail[1][0])
    rect1_top_right_x = float(detail[1][2])
    rect1_bottom_left_y = float(detail[1][3])
    rect1_top_right_y = float(detail[1][1])

    rect2_bottom_left_x = float(rectangle[0])
    rect2_top_right_x = float(rectangle[2])
    rect2_bottom_left_y = float(rectangle[3])
    rect2_top_right_y = float(rectangle[1])


    return not (rect1_top_right_x < rect2_bottom_left_x or rect1_bottom_left_x > rect2_top_right_x or rect1_top_right_y > rect2_bottom_left_y or rect1_bottom_left_y < rect2_top_right_y)


def main_function(result, tables):
    reg = r"([A-Z])-\1|([A-Z]\W?[A-Z]?\s?\W\s?\d\d?\s?\s?:\s?\d\d?\s?\W)"
    details, number = get_details(result)

    details = sorted(details, key=lambda x: x[0]) #sort by distance from 0,0
    sections = get_borders(details, tables)

    section = []
    details_dict = {}

    for sect in sections:
        coord = []
        coord_name = sect[0][4]
        for sec in sect[1:]:
            coord.append(sec)
        details_dict[coord_name] = coord
        section.append(list((coord_name,coord)))
    for table in tables:
        table[3] = 10000000
        coord = []
        name = "ZZZZZTable"
        for tab in table[:4]:
            coord.append(tab)
        details_dict[name] = coord
        section.append(list((name,coord)))

    if number == 0 | len(section) == 0:
            section.append(list(("No details",list((000.000,000.000,100000000.000,10000000.000)))))


    dict_help = {}

    for res in result:
        for det in section:
            help_dict = {}
            if re.match(reg, res): ###damit nicht details zu details zugeordnet werden!!!
                break
            if intersects(det,result[res]):
                name = det[0]
                help_dict[res] = result[res]
                if name in dict_help:
                    dict_help[name].update(help_dict)
                else:
                    dict_help[name] = help_dict
                break

    return dict_help, details_dict

