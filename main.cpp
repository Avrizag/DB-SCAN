#define _CRT_SECURE_NO_WARNINGS

#include <stdio.h>
#include <iostream>
#include "dbscan.h"





#define MINIMUM_POINTS 4     // minimum number of cluster
#define EPSILON (20)  // distance for clustering, metre^2

    vector<Point> readdata(vector<Point>& points) {
    string line;
    ifstream file("data_1_3.txt");

    while (getline(file, line)) { //line by line
        stringstream lineStream(line);//work on line
        string bit;
        valarray<double> vec(100);
        int i = 0;
        while (getline(lineStream, bit, ',')) {//read word until ,
            vec[i++] = stof(bit); //string to float..
        }


        getline(lineStream, bit, '\n'); //read last word in line
        vec[99] = stof(bit);

        points.push_back(Point(vec));
    }
    points.shrink_to_fit(); //free unused space
return move(points);
}


void printResults(vector<Point>& points, int num_points)
{
    int i = 0;
    printf("Number of points: %u\n"
        "cluster_id\n"
        "-----------------------------\n"
        , num_points);
    while (i < 10000)
    {
        printf("%d point: %d\n", i,
            points[i].clusterID);
        ++i;
    }
}
vector<Point> findnewcentroids(int k, vector<Point>& points) {// calc the new centroids.
    vector<int> nPoints;
    vector<valarray<double>> sumvec;
    valarray<double> t(0.0, points[0].vec.size());
    // Initialise with zeroes
    for (int j = 0; j < k; ++j) {
        nPoints.push_back(0);
        sumvec.push_back(t);
    }
    // go over points to append thier data to their centroids
    for (vector<Point>::iterator it = points.begin(); it != points.end(); ++it) {
        int clusterId = it->clusterID;
        nPoints[clusterId-1] += 1; //array of number of points of each cluster
        sumvec[clusterId-1] += it->vec;//insert data for cluster

        
    }
    // Compute the new centroids
    vector<Point> c;
    valarray<double> s;
    for (int j = 0; j < k; j++) {
        s = sumvec[j] / nPoints[j]; // mean vector of cluster
        Point b = Point(s);
        b.clusterID = j+1;
        c.push_back(b);

    }
    c.shrink_to_fit();
    return move(c);




}


double silluate(vector <Point>& points, int k) { //shilluate 
    int m = points.size();
    vector<Point> means = findnewcentroids(k, points);
    double silSum = 0;
    for (Point p : points) { //go over points (shilluate for each point)
        double b = DBL_MAX; //find the distance for the closest cluster (not your own)
        double a = p.distance(means[p.clusterID-1]);//distance p from his cluster centroid (mean)
        for (int i = 0; i < k; i++) { //go over k clusters
            if (i != p.clusterID-1) { //not the same cluster
                double tmp = p.distance(means[i]);
                b = min(b, tmp); //if smaller .
            }
        }
        silSum += ((b - a) / max(b, a)); //shilluate
    }
    silSum= silSum / m;
    return silSum;
}

vector <vector< Point>> merge_cluster(vector<vector< Point>> cluster_list, vector<Point> d)
{
    
    
    for (int i = 0; i < cluster_list.size()-1; i++)
    {
        vector<double> closetopoint;
        vector<int> visited;
        int j = 0;
        while (true)
        {
            if (cluster_list[i].size() - 1 < j)
            {
                break;

            }
            if (std::find(visited.begin(), visited.end(), cluster_list[i][j].clusterID) != visited.end()) ////
            {
                j = j + 1;
            }
            else {
                
                for (int k = 0; k < 1000; k++)
                {
                    int dist = d[i * 1000 + j].distance(d[(i + 1) * 1000 + k]);
                    if (dist > EPSILON)
                    {

                        dist = 0;
                    }
                    
                    if (dist > 0) {
                        int clind=cluster_list[i+1][k%1000].clusterID;
                        for (int o = 0; o < cluster_list[i + 1].size(); o++)
                        {
                            if (cluster_list[i + 1][o].clusterID == clind)
                            {
                                cluster_list[i + 1][o] = cluster_list[i][j];
                            }
                        }
                    }
               }
                visited.push_back(cluster_list[i][j].clusterID);
                j = j + 1;
            }
            
        }
    }
    return cluster_list;
}
vector <Point>flattenVector(vector<vector<Point> > v)
{
    vector <Point> clusterlist;
    for (int i = 0; i < v.size(); i++)
    {
        for (int j = 0; j < 1000; j++)
        {
            clusterlist.push_back(v[i][j]);
        }
       
    }
    return clusterlist;
    
}

int main()
{    
    vector<Point> points;
    vector<Point> pointscheck;
    vector<vector< Point>> clusterlist;

    // read point data
    points= readdata(points);
    for (int i = 0; i < 100; i++)
    {
        pointscheck.clear();
        for (int o =i*1000; o < (i+1)*1000; o++)
        {
            pointscheck.push_back(points[o]);
           
        }
        //construct
        DBSCAN ds(MINIMUM_POINTS, EPSILON, pointscheck); 
        ds.run();
        clusterlist.push_back( ds.m_points); //array of 100 ,1000 points each
        printf("%d\n", i);
       

    }
    clusterlist=merge_cluster(clusterlist, points);
    points=flattenVector(clusterlist);
    printResults(points,points.size());
    
   
    // result of DBSCAN algorithm
   
    printf("%.6f",silluate(points, 10));
    return 0;
}
