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

from bs4 import BeautifulSoup
import subprocess
import re

def get_bound_box(file):
    response = open(file)
    html_doc = response.read()
    response.close()
    html_file = BeautifulSoup(html_doc, 'html.parser')

    all_elements = []
    blocks = html_file.findAll('block')
    number_blocks = len(blocks)
    number_words = 0
    for block in blocks:
        list_elements = []
        words = block.findAll('word')
        number_words += len(words)
        for word in words:
            word_list = [word["xmin"], word["ymin"], word["xmax"], word["ymax"], word.string]
            list_elements.append(word_list)
        all_elements.append(list_elements)
    new_all_elements = []

    for element in all_elements:
        later_bigger = (float(element[-1][0])-(float(element[0][0]))) #check if xmin from first element is bigger than xmin from last element
        if later_bigger >= -5:
            new_all_elements.append(element)
        else:
            new_element = sorted(element, key=lambda k: [float(k[0])])
            new_all_elements.append(new_element)
    return new_all_elements, number_blocks, number_words

def pdf_to_html(uuid,filepath, path):
    filename = path +"/temporary/" +str(uuid)+"out.html"
    print(filename)
    subprocess.call(['pdftotext', '-bbox-layout',
                     filepath, filename])
    return filename

def extract_isos(result):
    reg = r"(ISO\s\d\d\d\d*\W?\d?\W?\d?)|(EN\s\d*)"
    details_ = []
    reg_general = r"ISO\s?\d*\s*\W\s*[fmcv][HKL]"
    general_tol = ""
    for element in result:
        new_arr = ""
        for x in element:
            new_arr += x[4] + " "
        if re.search(reg,new_arr):
            found = re.findall(reg, new_arr)
            for f in found:
                if len(f[0]) != 0:
                    details_.append(f[0].replace(")",""))
                if len(f[1]) != 0:
                    details_.append(f[1])
        if re.search(reg_general, new_arr):
            general_tol = new_arr

    return details_, str(general_tol)

def get_tables(result):
    reg = r"(Start drawing)|(All dimensions)"
    tables = []
    for element in result:
        new = []
        if re.search(reg, element):
            new.extend(result[element])
            new.append(element)
            tables.append(new)
    number = len(tables)
    return tables
