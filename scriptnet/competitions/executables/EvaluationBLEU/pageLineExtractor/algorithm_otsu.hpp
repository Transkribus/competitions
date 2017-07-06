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
#ifndef ALGORITHM_OTSU_HPP_10GTZXCBS4
#define ALGORITHM_OTSU_HPP_10GTZXCBS4

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
#include "grey_level_histogram.hpp"


namespace std {using namespace __gnu_cxx;}
using namespace std;

namespace prhlt {
    class Algorithm_OTSU{
        public:
            Algorithm_OTSU(cv::Mat &ex_image);
            int run();
        private:
            Grey_Level_Histogram grey_level_histogram;
            log4cxx::LoggerPtr logger;
            int threshold;
            int calculate_otsu_threshold();	
    };
}

#endif /* end of include guard: ALGORITHM_OTSU_HPP_10GTZXCBS4*/
