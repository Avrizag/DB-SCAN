import threading
from itertools import chain

import numpy as np
import collections
import matplotlib.pyplot as plt
import queue
from time import time
from sklearn.cluster import DBSCAN

# Define label for differnt point group
NOISE = 0
UNASSIGNED = 0
core = -1
edge = -2
cl = 1

def calc_distance_squared(a, b):  # calc distance between 2 matrix

    bsize = b.shape[0]
    x = np.sum(a ** 2)  # a^2
    y = np.sum(b ** 2, axis=1).reshape([1, bsize])
    xy = np.dot(a, b.T)
    d = x + y - 2 * xy
    d[d < 0] = 0
    

    return d



# function to find all neighbor points in radius for each point, save the index of the point in points array
def neighbor_points(pointId, radius, data):
    distance_squared = np.squeeze(calc_distance_squared(data[pointId, :], data))
    return np.where(distance_squared < radius ** 2)[0]



def get_pointcount(Eps, data, n_threads):
    # return list(map(lambda ind: neighbor_points(ind, Eps, data), range(len(data))))
    size = int(data.shape[0] / n_threads)
    res = [None for _ in range(data.shape[0])]

    def run(start,stop):
        for i in range(start, stop):
            res[i] = neighbor_points(i, Eps, data)

    threds = [threading.Thread(target=run,args=(i,min(i+size,data.shape[0]))) for i in range(0,data.shape[0],size)]

    for t in threds:
        t.start()

    for t in threds:
        if t.is_alive():
            t.join()
    return res
def dbscan(data, Eps, MinPt):
    global cl
    # initilize all pointlable to unassign
    pointlabel = np.full(len(data), UNASSIGNED)
    # initilize list for core/noncore point
    corepoint = []
    noncore = []
    cl_num = 1
    # Find all neighbor for all point
    pointcount = get_pointcount(Eps, data, 28) #pointCount contains the index of neighbors of each point
    pointcountsum = np.array(list(map(lambda l: len(l), pointcount)))# calculate the len of each point count (number of neighbors of each point)
    # Find all core point, edgepoint and noise
    corepoint, = np.where(pointcountsum >= MinPt)
    pointlabel[corepoint] = core

    noncore, = np.where(pointcountsum < MinPt)
    for i in noncore:  # find edges between the non core points, if one of the neighbors of non core points is a core point it means that the non core point is an edge
        for j in pointcount[i]:
            if j in corepoint:
                pointlabel[i] = edge

                break

    # Using a Queue to put all neigbor core point in queue and find neigboir's neigbor
    for i in range(len(pointlabel)):
        q = queue.Queue()
        if pointlabel[i] == core:  # for each core point
            pointlabel[i] = cl  # mark this point different ( cluster number)
            for x in pointcount[i]:
                if pointlabel[x] == core:  # if the neighbors of this point are core than add them to the queue and mark them
                    q.put(x)
                    pointlabel[x] = cl
                elif pointlabel[x] == edge:
                    pointlabel[x] = cl
            # Stop when all point in Queue has been checked, add to queue neighbors of neighbors
            while not q.empty():  # do the same to the neighbors of neighbors
                neighbors = pointcount[q.get()]
                for y in neighbors:
                    if pointlabel[y] == core:
                        pointlabel[y] = cl
                        q.put(y)
                    if pointlabel[y] == edge:
                        pointlabel[y] = cl
            cl = cl + 1  # move to next cluster
            cl_num = cl_num + 1
    return pointlabel - 1, cl_num
# DB Scan algorithom



# Function to plot final result
def plotRes(data, clusterRes, clusterNum):
    nPoints = len(data)
    scatterColors = ['black', 'green', 'brown', 'red', 'purple', 'orange', 'yellow']
    for i in range(clusterNum):
        if i == -1:
            # Plot all noise point as blue
            color = 'blue'
        else:
            color = scatterColors[i % len(scatterColors)]
        x1 = []
        y1 = []
        for j in range(nPoints):
            if clusterRes[j] == i:
                x1.append(data[j, 0])
                y1.append(data[j, 1])
        plt.scatter(x1, y1, c=color, alpha=1, marker='.')


def getData():  # fetch data from txt into matrix
    f = open("data_1_3.txt", "r")
    ret = []
    for line in f:  # scan lines
        ret.append([float(i) for i in line.split(",")])  # insert words
    return ret





def calc_distance_mats(a, b):  # calc distance between 2 matrix

    asize = a.shape[0]
    bsize = b.shape[0]
    x = np.sum(a ** 2, axis=1).reshape([asize, 1])  # a^2
    y = np.sum(b ** 2, axis=1).reshape([1, bsize])
    xy = np.dot(a, b.T)
    d = x + y - 2 * xy
    d[d < 0] = 0
    # dist = np.sqrt(d)
    # dist = np.sqrt(np.sum(np.square(a-b)))

    return d



def sillhuete1(dataMatrix, clusters, k):
    data_rows = dataMatrix.shape[0] #100000
    centers = [np.mean(dataMatrix[clusters == i, :], axis=0) for i in range(k)] #calculate the mean point of each cluster shape (10, 100)
    centers = np.array(centers)

    dist = calc_distance_mats(dataMatrix, centers)
    a = np.empty([data_rows])
    b = np.empty([data_rows])

    for i in range(data_rows):
        a[i] = dist[i, clusters[i]] # take from the matrix the distance between point and its cluster center
        b[i] = (dist[i, :])[np.arange(k) != clusters[i]].min() #take from the matrix  the min distance between point to another cluster

    return ((b - a) / np.maximum(a, b)).mean()

def merge_clusters(cluster_list):

    for i in range(0, len(cluster_list) - 1):
        visited = []
        j = 0 #inner index of each 1000 cluster index points
        while (True):
            if ( j > len(cluster_list[i]) - 1 ):
                break
            if cluster_list[i][j] in visited:  # if already found the close points in next data (already assign this cluster index for the next data)
                j = j + 1
            else:
                close_to_point = calc_distance_mats(np.array([d[i * 1000 + j]]), d[(i + 1) * 1000:(i + 2) * 1000]) # distance mat between point to the next 1000 points
                close_to_point[close_to_point > eps] = 0
                # go over the distances and if the radious is to far then 0
                for k, distRow in enumerate(close_to_point[0]):
                    if distRow > 0:  # if its neighbor
                        clind = cluster_list[i + 1][k % 1000]  # find the cluster for the close point
                        for itindex, item in enumerate(cluster_list[i + 1]):  # find the same cluster in all  next 1000 points
                            if item == clind:
                                cluster_list[i + 1][itindex] = cluster_list[i][j]  # merge between the two close clusters
                visited.append(cluster_list[i][j])
                j = j + 1

    return cluster_list

if __name__ == '__main__':
    print("start")
    d = np.array(getData())
    print("got data")
    # Set EPS and Minpoint
    eps = 20  # min radius
    minpts = 5  # min points to call a core
    #t=time()
    #dbscan1 = DBSCAN(eps=eps, min_samples=minpts).fit(d)
    #print(f'sillhuete: {sillhuete1(d, np.array(dbscan1.labels_), 10)}')
    #print(time()-t)

    partition_size = 0
    cluster_list = []
    t = time()
    for i in range(1,101):#divide the data and execute dbScan
        pointlabel, cl_size = dbscan(d[1000*(i-1):1000*i], eps, minpts)
        cluster_list.append(pointlabel)
        print("itration "+str(i)+" = "+str(time() - t))
    cluster_list = merge_clusters(cluster_list)
    flatten_list = list(chain.from_iterable(cluster_list))
    #plotRes(d, flatten_list, 10)
    #plt.show()
    st = time()
    print(f'sillhuete: {sillhuete1(d, np.array(flatten_list), 10)}')
    print(time() - t)
    print(time() - st)

