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
#include "grey_level_histogram.hpp"

namespace prhlt{
    using namespace log4cxx;
    using namespace log4cxx::helpers;
    using namespace boost;
    Grey_Level_Histogram::Grey_Level_Histogram(){
        this->logger = Logger::getLogger("PRHLT.Grey_Level_Histogram");
    }
    Grey_Level_Histogram::Grey_Level_Histogram(cv::Mat &ex_image){
        this->logger = Logger::getLogger("PRHLT.Grey_Level_Histogram");
        this->image = ex_image;
    }
    
    Grey_Level_Histogram::~Grey_Level_Histogram(){
        this->image.release();
        this->histogram.clear();
    }
    void Grey_Level_Histogram::set_image(cv::Mat &ex_image){
        this->image = ex_image;
    }
    
    float Grey_Level_Histogram::run(){
        return calculate_grey_level_histogram();
    }
    
    float Grey_Level_Histogram::calculate_grey_level_histogram(){
        this->histogram_sum = 0.0;
        for (int r=0; r < this->image.rows; r++)
            for (int c=0; c < this->image.cols; c++)
                this->histogram[this->image.at<uchar>(r,c)]+=1.0;
        
        int num_pixels = this->image.rows * this->image.cols;
        
        BOOST_FOREACH(sparse_histogram::value_type i, this->histogram){
            this->histogram[i.first]= i.second/num_pixels;
        }
        
        BOOST_FOREACH(sparse_histogram::value_type i, this->histogram){
            this->histogram_sum+= i.first * i.second;
        }
        
        return this->histogram_sum;
    }
}
