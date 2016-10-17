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
#ifndef LINE_HISTOGRAM_HPP_4R0UZ4YV
#define LINE_HISTOGRAM_HPP_4R0UZ4YV

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
#include "algorithm_kmeans.hpp"

namespace std {using namespace __gnu_cxx;}
using namespace std;

namespace prhlt {
    typedef vector<float> full_histogram;
    typedef boost::unordered_map<int,float> sparse_histogram;
    typedef boost::multi_array<cv::Point2d, 2> line_array;
    typedef vector<cv::Point2d> points_list;
    
    class Line_Histogram{
        public:
            Line_Histogram(int ex_threshold);
            Line_Histogram(cv::Mat &ex_image, int ex_threshold);
            Line_Histogram(cv::Mat &ex_image,cv::Rect rec, int ex_threshold);
            ~Line_Histogram();
            float& operator[] (const int nIndex);
            float get_derivate_value(const int nIndex);
            void calculation_initialization(string orientation_mode, string area_mode);
            //void calculate(string orientation_mode, string area_mode, int smoothing_factor);
			void calculate(string orientation_mode, string area_mode, int smoothing_factor,int derivate_window_size = 2);
            points_list get_maximums();
            points_list get_minimums();
            line_array get_local_drawable_histogram();
            line_array get_relative_drawable_histogram(cv::Rect rectangle);
            line_array get_drawable_list(string list_mode);
            void calculate_maxs_mins();
            int get_size();
            void set_interest_zone(cv::Rect rec);
            int get_grey_count();
            int get_binarization_threshold();
            int get_real_grey_count();
            int get_region_real_grey_count(string orientation_mode, string area_mode);
            void show_internal_image(float scale);
            static const string horizontal;
            static const string vertical;
            static const string mins;
            static const string maxs;
            static const string global;
            static const string local;
        private:
            void reset_histograms_lists();
            void perform_normalization();
            void initialize_coordinate_system(string mode);
            void initialize_line_histogram(string mode);
            void smooth_line_histogram(string mode,int num_smooth_columns);
            void calculate_line_histogram(string mode);
            void update_histogram(string mode,int rowIndex, int colIndex,float value);
            void calculate_maxs(cv::Mat line_labels);
            void calculate_mins(cv::Mat line_labels);
            void add_maximum(int index);
            void add_minimum(int index);
            int extract_index_from_point(cv::Point p);
            int get_normalization_value();
            void calculate_histogram_derivate(int window_size);
            float calculate_derivate_at(int line, int window_size);
            cv::Mat image;
            cv::Mat global_image;
            cv::Rect interest_zone;
            log4cxx::LoggerPtr logger;
            full_histogram image_histogram;
            full_histogram image_histogram_derivate;
            string orientation_mode;
            string area_mode;
            int binarization_threshold;
            int count;
            int global_count;
            bool is_initialized; 
            cv::Point2d zero;
            cv::Point2d increment;
            cv::Point2d max_bar_size;
		//Transition points from the histogram 
		        vector<cv::Point2d> max_list;
		        vector<cv::Point2d> min_list;
		};
}
#endif /* end of include guard: LINE_HISTOGRAM_HPP_4R0UZ4YV */

