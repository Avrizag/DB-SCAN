#ifndef DBSCAN_H
#define DBSCAN_H

#include <vector>
#include <cmath>
#include<valarray>
#include <fstream>
#include <sstream>

#define UNCLASSIFIED -1
#define CORE_POINT 1
#define BORDER_POINT 2
#define NOISE -2
#define SUCCESS 0
#define FAILURE -3

using namespace std;



struct Point {
    valarray<double> vec;     // coordinates
    int  clusterID;     // no default cluster
    



    Point(valarray<double>& y) :vec(move(y)), clusterID(-1){
    }

    double distance(Point p) {//vec dist from vec
        valarray<double>&& tmp = p.vec - vec;
        double dist = (tmp * tmp).sum();
        return dist;
    }

    bool operator ==(Point p) {
        valarray<bool> bools = vec == p.vec;
        for (bool v : bools) {
            if (!v)return false;
        }
        return true;
    }
};



class DBSCAN {
public:    
    DBSCAN(unsigned int minPts, float eps, vector<Point> points){
        m_minPoints = minPts;
        m_epsilon = eps;
        m_points = points;
        m_pointSize = points.size();
    }
    ~DBSCAN(){}

    int run();
    vector<int> calculateCluster(Point point);
    int expandCluster(Point point, int clusterID);
  

    int getTotalPointSize() {return m_pointSize;}
    int getMinimumClusterSize() {return m_minPoints;}
    int getEpsilonSize() {return m_epsilon;}
    
    public:
    vector<Point> m_points;
    
private:    
    unsigned int m_pointSize;
    unsigned int m_minPoints;
    float m_epsilon;
};
vector<Point> findnewcentroids(int k, vector<Point>& points);
double silluate(vector <Point>& points, int k);

#endif // DBSCAN_H
