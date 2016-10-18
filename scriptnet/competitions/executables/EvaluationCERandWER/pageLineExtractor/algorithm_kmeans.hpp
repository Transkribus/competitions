/*
    Tool for the extraction of lines or list information of layout data in PAGE format

    Copyright (C) 2013 Vicente Bosch Campos - viboscam@prhlt.upv.es

    This file is part of page_format_tool

    page_format_tool is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
#ifndef ALGORITHM_KMEANS_HPP_7D0XW1DK
#define ALGORITHM_KMEANS_HPP_7D0XW1DK

#include <math.h>
#include <log4cxx/logger.h>
#include <log4cxx/basicconfigurator.h>
#include <log4cxx/helpers/exception.h>
#include <boost/foreach.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/unordered_map.hpp>
#include <boost/multi_array.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>

using namespace log4cxx;
using namespace log4cxx::helpers;
namespace std {using namespace __gnu_cxx;}
using namespace std;
using namespace boost;


namespace prhlt {

    typedef vector<int> label_map;

    class Algorithm_KMeans
    {
    public:
        enum
        {
            BS=1,
            IL=2,
            NL=3
        };
        Algorithm_KMeans(cv::Mat &ex_data, cv::Mat &ex_image);
        ~Algorithm_KMeans();
        void run(int binarization_threshold);
        cv::Mat get_labels();
        int classify(cv::Mat sample);
    private:
        cv::Mat data;
        cv::Mat image;
        cv::Mat centers;
        int num_centers;
        cv::Mat data_labels;
        vector<float> center_grey_count;
        label_map center2label_map;
        double euclidean_distance(cv::Mat center,cv::Mat sample);
        void set_labels2centers(int binarization_threshold);
        void calculate_centers_grey_count(int binarization_threshold);
        void draw_result();
    };
}


#endif /* end of include guard: ALGORITHM_KMEANS_HPP_7D0XW1DK */
