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
#ifndef LINE_REGION_LIST_HPP_4D3UIS3SDF
#define LINE_REGION_LIST_HPP_4D3UIS3SDF

#include <log4cxx/logger.h>
#include <log4cxx/basicconfigurator.h>
#include <log4cxx/helpers/exception.h>
#include <boost/foreach.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/unordered_map.hpp>
#include <boost/multi_array.hpp>
#include <fstream>
#include <iostream>


namespace std {using namespace __gnu_cxx;}
using namespace std;

namespace prhlt {
    class Line_Region_List{
        public:
            Line_Region_List(string ex_file_name, int ex_page_start, int ex_page_end);
            ~Line_Region_List();
            vector< vector <int> >  get_line_limits();
            vector< vector <int> >  get_search_zones();
        private:
            vector< vector <int> >  line_limits;
            vector< vector <int> >  search_zones;
            log4cxx::LoggerPtr logger;
            float average_line_size;
            float average_interline_size; 
            int page_start;
            int page_end;
            string file_name;
            void clear_limits_list();
            void clear_search_list();
            void load_file();
            void calculate_search_zones();
    };
}

#endif /* end of include guard*/
