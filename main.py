import order_bounding_boxes_in_each_block
import clustering_precomputed_dbscan as dbscan
import read_from_clustered_merged
import organize_drawing_according_to_details_new
import redis
import json
import sys
import csv
import numpy as np


config_path = "/home/bscheibel/technical_drawings_extraction"


def distance_knn(dm):
    knn = []
    for row in dm:
        row = row[row != 0]
        row = row.round(decimals=2)
        row = sorted(row)
        knn.extend(row[:2])
    return knn


def distance_btw_blocks(result, path):
    result.to_csv(path+"/temporary/blub_distances.csv", sep=";", index=False, header=None)
    with open(path+"/temporary/blub_distances.csv") as csvfile:
        read_csv = csv.reader(csvfile, delimiter=';')
        result = list(read_csv)
    dm = np.asarray([[dbscan.dist(p1, p2) for p2 in result] for p1 in result])
    return dm


def get_min_nn(result, path):
    dm = distance_btw_blocks(result, path)
    knn = distance_knn(dm)
    knn = list(set(knn))
    knn = sorted(knn)
    return knn


def find_nearest_above(my_array, target):
    diff = my_array - target
    mask = np.ma.less_equal(diff, 0)
    if np.all(mask):
        return None
    masked_diff = np.ma.masked_array(diff, mask)
    return masked_diff.argmin()


def write_redis(uuid, result, db_params):
    db_params = redis.Redis(db_params)
    #db = db = redis.Redis(unix_socket_path='/tmp/redis.sock',db=7)
    print(db_params)
    db_params.set(uuid, result)


def main(uuid, filepath, db, eps_manual):
    path = config_path
    filename = order_bounding_boxes_in_each_block.pdf_to_html(uuid, filepath, path)
    result, number_blocks, number_words= order_bounding_boxes_in_each_block.get_bound_box(filename)  ##get coordinates+text out of html file into array of arrays
    isos, general_tol = order_bounding_boxes_in_each_block.extract_isos(result)
    result_df = dbscan.get_average_xy(result, path)
    knn = get_min_nn(result_df, path)
    eps = min(knn)
    res, number_clusters, dbs, chs_old, silhoutte, dm = dbscan.cluster_and_preprocess(result, eps, path)
    stopping_criterion = False

    while not stopping_criterion:

        print("cluster, eps: ", eps)
        silhoutte_old = silhoutte
        res, number_clusters, dbs, chs, silhoutte = dbscan.clustering(dm, eps, path)

        read_from_clustered_merged.read(path + "/temporary/values_clusteredfrom_precomputed_dbscan.csv")
        old_eps = eps
        if not silhoutte >= silhoutte_old:
            print("stopping threshold reached")
            stopping_criterion = True
        try:
            eps = find_nearest_above(knn, eps)
            eps = knn[eps]
        except:
            print("highest nn value reached")
            break

    res, number_clusters, dbs, chs, silhouette = dbscan.clustering(dm, old_eps, path)
    clean_arrays = read_from_clustered_merged.read(path+"/temporary/values_clusteredfrom_precomputed_dbscan.csv")
    tables = order_bounding_boxes_in_each_block.get_tables(clean_arrays)
    pretty = read_from_clustered_merged.print_clean(clean_arrays)
    res, details_dict = organize_drawing_according_to_details_new.main_function(pretty, tables)

    json_isos = json.dumps(isos)
    json_result = json.dumps(res)
    json_details = json.dumps(details_dict)
    write_redis(uuid+"tol", general_tol, db)
    write_redis(uuid+"dims", json_result, db)
    write_redis(uuid+"isos",json_isos, db)
    write_redis(uuid+"eps", str(number_blocks)+"," + str(number_words), db)
    write_redis(uuid+"details", json_details, db)


if __name__ == "__main__":
    uuid = sys.argv[1]
    filename = sys.argv[2]
    db = sys.argv[3]
    eps = sys.argv[4]
    main(uuid, filename, db, eps)