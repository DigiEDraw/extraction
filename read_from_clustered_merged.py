# coding=utf8

# Copyright (C) 2021  Beate Scheibel
# This file is part of DigiEDraw.
#
# DigiEDraw is free software: you can redistribute it and/or modify it under the terms
# of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# DigiEDraw is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# DigiEDraw.  If not, see <http://www.gnu.org/licenses/>.


import re
import csv

def read(file):
    with open(file, "r") as f:
        reader = csv.reader(f, delimiter=";")
        result = []
        dict = {}
        for row in reader:
            ausrichtung = row[1]
            row3 = row[2]
            row3 = eval(row3)
            element = ""
            ymin = 100000000.0
            ymax = 0.0
            xmin = 100000000.0
            xmax = 0.0
            coords = []

            merged_elements = []
            length = 0
            for e in row3:
                length += len(e)

            for elem in row3:

                if len(row3) == 1:
                    element = elem[4]
                    xmin = float(elem[0])
                    ymin = float(elem[1])
                    xmax = float(elem[2])
                    ymax = float(elem[3])

                else:

                    if isinstance(elem[0],list):
                        merged_elements += elem

                        if len(merged_elements) < length:
                            continue

                        if int(ausrichtung) == 1:
                            merged_elements = sorted(merged_elements, key=lambda k: [float(k[3])], reverse=True)


                        for elemt in merged_elements:
                            element += elemt[4] + " "
                            if float(elemt[0]) < xmin:
                                xmin = float(elemt[0])
                            if float(elemt[1]) < ymin:
                                ymin = float(elemt[1])
                            if float(elemt[2]) > xmax:
                                xmax = float(elemt[2])
                            if float(elemt[3]) > ymax:
                                ymax = float(elemt[3])


                    else:
                        element += elem[4] + " "
                        if float(elem[0]) < xmin:
                            xmin = float(elem[0])
                        if float(elem[1]) < ymin:
                            ymin = float(elem[1])
                        if float(elem[2]) > xmax:
                            xmax = float(elem[2])
                        if float(elem[3]) > ymax:
                            ymax = float(elem[3])

            result.append(element)
            coords.append(xmin)
            coords.append(ymin)
            coords.append(xmax)
            coords.append(ymax)
            if element in dict.keys():
                element = element + " "
                dict[element] = coords
            else:
                dict[element] = coords
    return dict


def print_clean(dims): ##alles raus was nicht relevant ist! und zeichen ersetzen!
    dims_new = {}
    reg_clean = r"ISO|[a-zA-Z]{4,}|^\d\s\d$|^[a-zA-Z]{2,}\d.*$|^[A-Z]{1}$|^mm$|^\d{2}\.\d{2}\.\d{4}|^-$|A\d|^\d{1}$|^[A-Za-z]{3,}\.?$|^\d{5}|^\d{1}\s\W\s\d"
    reg_one_character_only = "^\s*\S{1}\s*x?\s*$" #get rid of singular characters or numbers, or times eg 4x
    for dim in dims:
        #dim = dim.strip()
        if re.search(reg_clean, dim):
            continue
        elif re.search(reg_one_character_only,dim):
            continue
        else:
            coords = dims[dim]
            if re.search(r"b\s\d*\W?\d*\s.",dim):
                dim = dim.replace('b', u"\u27C2")
            if re.search(r"g\s\d*\W?\d*", dim):
                dim = dim.replace('g', u"\u232D")
            if re.search(r"f\s\d*\W?\d*", dim):
                dim = dim.replace('f',  u"\u2225")
            if re.search(r"r\s\d*\W?\d*", dim):
                dim = dim.replace('r', u"\u25CE")
            if re.search(r"i\s\d*\W?\d*", dim):
                dim = dim.replace('i', u"\u232F")
            if re.search(r"j\s\d*\W?\d*", dim):
                dim = dim.replace('j', u"\u2316")
            if re.search(r"d\s\d*\W?\d*", dim):
                dim = dim.replace('d', u"\u2313")
            if re.search(r"c\s+\d*", dim):
                dim = dim.replace('c', u"\u23E5")
            if re.search(r"n\s+\d*", dim):
                dim = dim.replace('n', u"\u2300")
            if "È" in dim:
                dim = dim.replace('È', 'GG')
            if "`" in dim:
                dim = dim.replace('`', u"\u00B1")
            if "#" in dim:
                dim = dim.replace('#', "↔")
            if "⌀" in dim:
                dim = dim.replace('⌀', "Ø")
            reg12 = re.compile(r"(.*\d{1,4}\W?\d{0,4})\s?\+\s-\s?(\d{1,4}\W?\d{0,4})\s?(\d{1,4}\W?\d{0,3})") ##???? was machst du?? nach toleranzen suchen, mit +/- blabla
            reg13 = re.compile(r"(.*)\+\s\+\s(\d*\W\d*)\s(\d*\W\d*)(.*)")
            reg14 = re.compile(r"(\+\s?\d*,?.?\d*)\s*(\d*,?.?\d*)\s*(\+?\s?\-?\s?\d*,?.?\d*)")
            reg15 = re.compile(r"\d\s\d\.|\.\d\s\d")
            g = re.search(reg12, dim)
            f = re.search(reg13, dim)
            e = re.search(reg14, dim)
            if g:
                dim = re.sub(reg12, g.group(1) + " +" + g.group(2) + " -" + g.group(3), dim) # +/- toleranzen schön darstellen
            elif f:
                dim = f.group(1) + "+" + f.group(2) + " +" + f.group(3) + f.group(4)
            elif e:
                dim = e.group(2) + " " + e.group(1) + " " + e.group(3)
            dim = dim.replace(" ,",".").replace(", ",".").replace(",",".")
            dims_new[dim] = coords

    return dims_new
