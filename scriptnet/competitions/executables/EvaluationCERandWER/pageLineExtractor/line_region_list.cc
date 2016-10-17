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
#include "line_region_list.hpp"

namespace prhlt {
    using namespace log4cxx;
    using namespace log4cxx::helpers;
    using namespace boost;
            
    Line_Region_List::Line_Region_List(string ex_file_name, int ex_page_start, int ex_page_end){
        this->logger = Logger::getLogger("PRHLT.Line_Region_List");
        this->file_name = ex_file_name;
        this->page_start = ex_page_start;
        this->page_end = ex_page_end;
        LOG4CXX_INFO(this->logger,"<<INITIALIZING Line Region List>>"); 
        load_file();
        calculate_search_zones();
        LOG4CXX_INFO(this->logger,"<<DONE>>"); 
    }
    Line_Region_List::~Line_Region_List(){
        clear_limits_list();
        clear_search_list();
    }

    void Line_Region_List::clear_limits_list(){
        for (int i = 0 ; i < this->line_limits.size();i++)
            this->line_limits[i].clear();
        this->line_limits.clear();
    }

    void Line_Region_List::clear_search_list(){
        for(int i = 0 ; i < this->search_zones.size();i++)
            this->search_zones.clear();
        this->search_zones.clear();
    }
    void Line_Region_List::load_file(){
        ifstream file;
        string temp_line;
        std::vector<std::string> string_values;
        this->average_line_size = 0;
        this->average_interline_size = 0;
       
        LOG4CXX_INFO(this->logger,"<<Loading File>> "  << this->file_name); 
        file.open(this->file_name.c_str());
        if(file.is_open()){ 
            while(std::getline(file,temp_line)){
                boost::split(string_values,temp_line,boost::is_any_of(" "),boost::token_compress_on);
                if(string_values.size()==2)
                {
                    vector<int> tmp_vec;
                    int tmp;
                    istringstream(string_values[0]) >> tmp;
                    tmp_vec.push_back(tmp);
                    istringstream(string_values[1]) >> tmp;
                    tmp_vec.push_back(tmp);
                    this->average_line_size += tmp_vec[1]-tmp_vec[0];
                    if (this->line_limits.size()>=1)
                    	this->average_interline_size += tmp_vec[0]-this->line_limits[this->line_limits.size()-1][1];

                    this->line_limits.push_back(tmp_vec);
                }
                else{
                    LOG4CXX_ERROR(this->logger,"Incorrect number of elements in a line");
                    abort();
                }
            
            }
            this->average_line_size /= (float)this->line_limits.size();
            this->average_interline_size /= (float)(this->line_limits.size()-1);
            LOG4CXX_INFO(this->logger,"Average line size is >> " << this->average_line_size);
            LOG4CXX_INFO(this->logger,"Average interline size is >> " << this->average_interline_size);
        }
        else{
            LOG4CXX_ERROR(this->logger,"File could not be open!!");
            abort();
        }
    }
    void Line_Region_List::calculate_search_zones(){
        LOG4CXX_INFO(this->logger,"<<Computing Search Zones>>");
        int current_region_start = this->page_start;
        int current_region_end;
        int line_size;
        int last_line_size = 0;
        for (int i = 0; i < this->line_limits.size();i++)
        {
        	line_size = this->line_limits[i][1]-this->line_limits[i][0];
        	//if ((float)line_size/(float)this->average_line_size > 2)
        	//	continue;
            vector<int> tmp_vector;
            LOG4CXX_DEBUG(this->logger,"Line >> " << this->line_limits[i][0] << " - " << this->line_limits[i][1]);
            current_region_end = this->line_limits[i][1];
            if ( i != 0){
            	tmp_vector.push_back(current_region_start+(last_line_size/2)+abs(last_line_size-this->average_line_size));
            //	tmp_vector.push_back(current_region_start);
			}
			else
				tmp_vector.push_back(current_region_start);
            tmp_vector.push_back(current_region_end-(line_size/2));
            tmp_vector.push_back(current_region_end);
            this->search_zones.push_back(tmp_vector);
            LOG4CXX_DEBUG(this->logger,"Region >> " << tmp_vector[0] << " - " << tmp_vector[1]);
            current_region_start = this->line_limits[i][0];
            last_line_size = line_size;
        }
        vector<int> tmp_vector;
        tmp_vector.push_back(current_region_start+10);
        if (((float)(this->page_end-current_region_start)/(float)this->page_end) > 0.1 )
        	tmp_vector.push_back(current_region_end+1.5*this->average_interline_size);
		else
        	tmp_vector.push_back(this->page_end);
        LOG4CXX_DEBUG(this->logger,"Region >> " << tmp_vector[0] << " - " << tmp_vector[1]);
        
        this->search_zones.push_back(tmp_vector);
    }
    vector< vector <int> >Line_Region_List::get_line_limits(){
        return this->line_limits;
    }
    vector< vector <int> > Line_Region_List::get_search_zones(){
        return this->search_zones;
    }

}
