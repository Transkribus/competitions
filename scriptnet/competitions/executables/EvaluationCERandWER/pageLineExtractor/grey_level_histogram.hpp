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
#ifndef GREY_LEVEL_HISTOGRAM_HPP_45FTSEBNG7
#define GREY_LEVEL_HISTOGRAM_HPP_45FTSEBNG7

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


namespace std {using namespace __gnu_cxx;}
using namespace std;

namespace prhlt {
    typedef boost::unordered_map<int,float> sparse_histogram;
    
    class Grey_Level_Histogram{
        public:
            Grey_Level_Histogram();
            Grey_Level_Histogram(cv::Mat &ex_image);
            ~Grey_Level_Histogram();
            void set_image(cv::Mat &ex_image);
            float run();
            sparse_histogram histogram;
        private:
            cv::Mat image;
            log4cxx::LoggerPtr logger;
            float histogram_sum;
            float calculate_grey_level_histogram();
    };
}

#endif /* end of include guard: GREY_LEVEL_HISTOGRAM_HPP_45FTSEBNG7*/
