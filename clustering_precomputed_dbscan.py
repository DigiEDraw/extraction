# coding: utf8
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

import numpy as np
import pandas
import csv
from math import sqrt
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.metrics import davies_bouldin_score
import time

def get_average_xy(list_input, path):
    csv_name = path+"/temporary/list_to_csv_with_corner_points.csv"
    resultFile = open(csv_name, 'w')
    wr = csv.writer(resultFile, delimiter=";")
    wr.writerow(["element", "xmin","ymin","xmax","ymax", "ausrichtung","point_xmi_ymi","point_xma_ymi","point_xmi_yma","point_xma_yma"])
    result_df = pandas.DataFrame(columns=["point_xmi_ymi","point_xma_ymi","point_xmi_yma","point_xma_yma","ausrichtung"])

    for element in list_input:
        ymin = 100000000
        ymax = 0
        xmin = 100000000
        xmax = 0
        newList = []
        if len(element) == 5 and not isinstance(element[0], list):
            newList.append(element)
            element = newList
        for blub in element: #get the smallest and largest x and y value for whole block

            if isinstance(blub[0],list) and len(blub[0]) == 5:
                blub = blub [0]
            if float(blub[1]) < ymin:
                ymin = float(blub[1])
            if float(blub[0]) < xmin:
                xmin = float(blub[0])
            if float(blub[3]) > ymax:
                ymax = float(blub[3])
            if float(blub[2]) > xmax:
                xmax = float(blub[2])
        if float(xmax)-float(xmin) > 1.3*(float(ymax)-float(ymin)):
            ausrichtung = 0  # horizontal
        #elif
        elif 1.3*(float(xmax)-float(xmin)) < float(ymax)-float(ymin):
            ausrichtung = 1   # vertikal
        else:
            ausrichtung = 3   # sonstiges

        ##### GET CORNER POINTS
        point_xmi_ymi = [xmin,ymin]
        point_xma_ymi = [xmax,ymin]
        point_xmi_yma = [xmin,ymax]
        point_xma_yma = [xmax,ymax]
        wr.writerow([element,xmin,ymin,xmax,ymax, ausrichtung,point_xmi_ymi,point_xma_ymi,point_xmi_yma,point_xma_yma])
        result_df.loc[len(result_df)]=[point_xmi_ymi,point_xma_ymi, point_xmi_yma, point_xma_yma,ausrichtung]

    resultFile.close()
    return result_df

def intersects(rectangle1, rectangle2): #using the separating axis theorem, returns true if they intersect, otherwise false

    rect_1_min = eval(rectangle1[0])
    rect_1_max = eval(rectangle1[3])
    rect1_bottom_left_x = rect_1_min[0]
    rect1_top_right_x = rect_1_max[0]
    rect1_bottom_left_y = rect_1_max[1]
    rect1_top_right_y = rect_1_min[1]

    rect_2_min = eval(rectangle2[0])
    rect_2_max = eval(rectangle2[3])
    rect2_bottom_left_x = rect_2_min[0]
    rect2_top_right_x = rect_2_max[0]
    rect2_bottom_left_y = rect_2_max[1]
    rect2_top_right_y = rect_2_min[1]

    return not (rect1_top_right_x < rect2_bottom_left_x or rect1_bottom_left_x > rect2_top_right_x or rect1_top_right_y > rect2_bottom_left_y or rect1_bottom_left_y < rect2_top_right_y)


def get_ausrichtung(rectangle1,rectangle2):
    #check if rect 1 and rect 2 are above or beside, r,l, a,b

    min_1 = eval(rectangle1[0])
    min_2 = eval(rectangle2[0])
    diff_y = min_1[1] - min_2[1]
    diff_x = min_1[0] - min_2[0]
    if diff_x < diff_y:
        ausrichtung = "above"
    else:
        ausrichtung = "side"
    return ausrichtung


def get_parallel(rectangle1, rectangle2):
    parallel = False
    ausrichtung_1 = eval(rectangle1[4])
    ausrichtung_2 = eval(rectangle2[4])
    if ausrichtung_1 == ausrichtung_2 and ausrichtung_1 == 0:
        ausrichtung = get_ausrichtung(rectangle1, rectangle2)
        if ausrichtung == "above":
            parallel = True

    if ausrichtung_1 == ausrichtung_2 and ausrichtung_1 == 1:
        ausrichtung = get_ausrichtung(rectangle1, rectangle2)
        if ausrichtung == "side":
            parallel = True
    return parallel


def dist(rectangle1, rectangle2):
 #get minimal distance between two rectangles
    distance = 100000000
    second_dist = 100000
    for point1 in rectangle1[:4]:
        point1 = eval(point1)
        for point2 in rectangle2[:4]:
            point2 = eval(point2)
            dist = sqrt((float(point2[0]) - float(point1[0]))**2 + ((float(point2[1]) - float(point1[1])))**2)
            if dist < distance:
                second_dist = distance
                distance = dist
        if get_parallel(rectangle1,rectangle2):
            distance += 1000
            second_dist += 1000
        if intersects(rectangle1, rectangle2):
          distance = 0
          second_dist = 0
    distance = (distance+second_dist)/2
    return distance

def clustering(dm,eps,path):
    db = DBSCAN(eps=eps, min_samples=1, metric="precomputed").fit(dm)
    labels = db.labels_
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

    print('Estimated number of clusters: %d' % n_clusters_)
    data_df = pandas.read_csv(path +"/temporary/list_to_csv_with_corner_points.csv", sep=";")
    data_df["cluster"] = labels
    try:
        dbs = davies_bouldin_score(dm, labels)
        #dbs = "1"
        chs = metrics.calinski_harabasz_score(dm, labels)
        #chs = 1
        silhoutte = metrics.silhouette_score(dm, labels, metric='precomputed')
        #silhoutte = 2
        print("DBscore: ", dbs)
        print("calsinski: ", chs)
        print("silhoutte: ", silhoutte)

    except:
        dbs=1
        chs=1
        silhoutte=1

    data_df["ausrichtung"] = 1
    data_df = data_df.groupby(['cluster', 'ausrichtung'])['element'].apply(','.join).reset_index()
    data_df.to_csv(path+"/temporary/values_clusteredfrom_precomputed_dbscan.csv",sep=";", header=False, index=False)

    return data_df, n_clusters_, dbs, chs, silhoutte

def cluster_and_preprocess(result,eps,path):
    start_time = time.time()
    result = get_average_xy(result, path) #input: array of arrays, output: either csv file or array of arrays
    end_time = time.time()
    time_taken_get_average = end_time - start_time
    print("time get average: ", time_taken_get_average)

    start_time = time.time()
    result.to_csv(path+"/temporary/blub.csv", sep=";", index=False, header=None)
    end_time = time.time()
    time_taken_tocsv = end_time - start_time
    print("time to csv:" , time_taken_tocsv)

    with open(path+"/temporary/blub.csv") as csvfile:
        readCSV = csv.reader(csvfile, delimiter=';')
        result = list(readCSV)


    start_time = time.time()
    dm = np.asarray([[dist(p1, p2) for p2 in result] for p1 in result])
    end_time = time.time()
    time_taken_dm = end_time - start_time
    print("time dm:" , time_taken_dm)


    start_time = time.time()
    clustering_result, n_clusters_, dbs, chs, silhoutte = clustering(dm,float(eps), path)
    end_time = time.time()
    time_taken_clustering = end_time - start_time
    print("time clustering:" , time_taken_clustering)

    return clustering_result, n_clusters_, dbs, chs, silhoutte, dm

