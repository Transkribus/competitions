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
#ifndef IMAGE_HPP_7HEI0TM0
#define IMAGE_HPP_7HEI0TM0

#include <log4cxx/logger.h>
#include <log4cxx/basicconfigurator.h>
#include <log4cxx/helpers/exception.h>
#include <boost/foreach.hpp>
#include <boost/filesystem.hpp>
#include <boost/algorithm/string.hpp>
#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include "line_histogram.hpp"
#include "algorithm_otsu.hpp"

typedef vector<cv::Rect> rectangules_list;
typedef boost::multi_array<float, 2> pixel_results;

namespace prhlt {
    class Image{
        public:
            Image();
            ~Image();
            void load_from_file(string file_path);
            bool is_image_loaded();
            void load_from_matrix(cv::Mat &ex_image);
            void load_from_matrix_region(cv::Mat &ex_image, cv::Rect rec);
            int binarize_image(int ex_threshold);
            bool is_image_binarized();
            int get_binarization_threshold();
            int get_num_rows();
            int get_num_columns();
            cv::Mat get_matrix();
    		cv::Mat get_binary_matrix();
            bool is_foreground_pixel(int x,int y);
            bool coordinates_inside_image(int x, int y);
            void display_with_scale(string window_name, float scale,int wait_time, bool destroy_on_exit);
            void overlay_image_with_color(cv::Mat input_mat, cv::Scalar color);
            void display_binarized_with_scale(string window_name, float scale,int wait_time, bool destroy_on_exit);
            Image draw_histogram(cv::Rect area_rectangle , Line_Histogram hist, cv::Scalar color);
            void draw_line(cv::Point2d from, cv::Point2d to,cv::Scalar color);
            void draw_lines(line_array lines,cv::Scalar color);
            void draw_randomed_colored_region(vector<cv::Point2d> points);
            void draw_polyline(vector<cv::Point2d> points, cv::Scalar color);
            void draw_randomed_colored_polyline(vector<cv::Point2d> points);
            void draw_rectangle(cv::Rect rec,cv::Scalar color);
            void draw_rectangles(rectangules_list rec_list);
            void draw_text(cv::Point pos, string text);
		    void encircle_points(vector<cv::Point2d> points,int radius,cv::Scalar color);
            cv::Rect get_area_rectangle(); 
            int get_num_grey_pixels_in_subregion(cv::Rect rec);
            pixel_results calculate_pixels_in_regions(rectangules_list rec_list);
            cv::Mat get_subregion_matrix(cv::Rect rec);
            void save_image(string path);
            Image clone_image();
        private:
            bool image_loaded;
            bool image_binarized;
            cv::Mat image;
            cv::Mat greyscale_image;
            cv::Mat binary_integral_image;
            cv::Mat binary_image;
            int binarization_threshold;
            log4cxx::LoggerPtr logger;
            cv::Scalar random_color(CvRNG *rng);
            void initialize_greyscale_image();
            void initialize_binary_image_matrixes();
            void release_internal_images();
    };
}
#endif /* end of include guard: IMAGE_HPP_7HEI0TM0 */

