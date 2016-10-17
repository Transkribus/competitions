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
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <string>
#include <log4cxx/logger.h>
#include <log4cxx/basicconfigurator.h>
#include <log4cxx/helpers/exception.h>
#include <boost/thread/thread.hpp>
#include <boost/program_options.hpp>
#include <boost/filesystem.hpp>
#include <boost/foreach.hpp>
#include "image.hpp"
#include "page_file.hpp"

namespace po = boost::program_options;
using namespace std;
using namespace boost::filesystem;
using namespace log4cxx;
using namespace log4cxx::helpers;

LoggerPtr logger(Logger::getLogger("PRHLT"));

void setVerbosity(int verb){

	switch(verb){
		case 0:
			logger->setLevel(log4cxx::Level::getError());
			break;	
		case 1:
			logger->setLevel(log4cxx::Level::getInfo());
			break;
		case 2:
			logger->setLevel(log4cxx::Level::getDebug());
			break;
		default:
			logger->setLevel(log4cxx::Level::getError());
	}
}

bool areValidOptions(po::variables_map vm){
	
	if (  vm["operation_mode"].as<string>() != "LIST" and  vm["operation_mode"].as<string>() != "FILE"){
		LOG4CXX_ERROR(logger,"The operation method specified: \"" << vm["operation_mode"].as<string>() << "\" is not valid. Operation method must be either DISPLAY or FILE");
		return false;
	}
	if (  !exists(vm["input_image"].as<string>())){
		LOG4CXX_ERROR(logger,"The image file specified for input: \"" << vm["input_image"].as<string>() << "\" does not exist.");
		return false;
	}
	if (  !exists(vm["page_file"].as<string>())){
		LOG4CXX_ERROR(logger,"The page file specified: \"" << vm["page_file"].as<string>() << "\" does not exist.");
		return false;
	}
	
	if ( vm["verbosity"].as<int>() < 0 or vm["verbosity"].as<int>() > 2) {
		LOG4CXX_ERROR(logger,"Verbosity value must be betwee 0 and 2 ");
		return false;
	}
	
	return true;
}

void displayInputedValues(po::variables_map vm){
	LOG4CXX_INFO(logger,"<<INPUTED PARAMETERS>>");
	LOG4CXX_INFO(logger,"Input image file       : " << vm["input_image"].as<string>());
	LOG4CXX_INFO(logger,"Page file              : " << vm["page_file"].as<string>());
	//LOG4CXX_INFO(logger,"Transcription file     : " << vm["transcription_file"].as<string>());
	LOG4CXX_INFO(logger,"Operation mode         : " << vm["operation_mode"].as<string>());
	LOG4CXX_INFO(logger,"Verbosity              : " << vm["verbosity"].as<int>());	
}

int main(int argc, char **argv){   
	
	string input_image,page_file,transcription_file,operation_mode;
	int verbosity;

	BasicConfigurator::configure();
	po::options_description desc( "Allowed options" );
	desc.add_options()
		( "help,h", "Generates this help message" )
		( "input_image,i", po::value<string>(&input_image)->default_value("image.jpg"),"Input image from which to extract the line images (by default ./image.jpg)" )
		( "page_file,l", po::value<string>(&page_file)->default_value("page.xml"),"Page file path (by default ./page.xml)" )
		( "transcription_file,t", po::value<string>(&transcription_file)->default_value("trans.txt"),"Transcription file path (by default ./trans.txt)" )
		( "operation_mode,m", po::value<string>(&operation_mode)->default_value("DISPLAY"), "Operation mode of the command line tool, list printing out the list of line regions (LIST) or save the line images to (FILE) (default value is LIST)")
		( "verbosity,v", po::value<int>(&verbosity)->default_value(0), "\% Verbosity os messages during execution [0-2]");
	po::variables_map vm;
	po::store( po::parse_command_line( argc, argv, desc ), vm ); // to read command line options
	po::notify( vm );

	setVerbosity(vm["verbosity"].as<int>());

	if (vm.count("help"))
		std::cout << desc << std::endl;
	else{
		if(areValidOptions(vm)){
		    displayInputedValues(vm);
			  prhlt::Image input_image;
			  prhlt::Image output_image;
		    input_image.load_from_file(vm["input_image"].as<string>());
		    cv::Mat temp = input_image.get_matrix();
			prhlt::Page_File page(vm["page_file"].as<string>());
			page.load_image(temp);
        
       // prhlt::Points_File points_file_instance(vm["region_file"].as<string>());        
        
        //output_image.load_from_matrix(temp);
        if(vm["operation_mode"].as<string>()=="LIST"){
				page.print_file_info();
                                page.load_transcription_file(vm["transcription_file"].as<string>());
				page.add_loaded_transcription_text();
				//LOG4CXX_INFO(logger,"<<SAVING GLOBAL IMAGE>>");
				//page.display_contours_and_boxes();
		        //LOG4CXX_INFO(logger,"<<DONE SAVING GLOBAL IMAGE>>");
				//page.print_old_format();
				page.save_xml("output.xml");
        }else{
            LOG4CXX_INFO(logger,"<<SAVING LINE IMAGES TO FILE>>");
            page.extract_line_images();
        }
        
		}
		else{
			LOG4CXX_ERROR(logger,"Exiting due to incorrect input parameters");
			exit(EXIT_FAILURE);
		};
	}

	LOG4CXX_INFO(logger,"<<APPLICATION EXITING CORRECTLY>>");
	exit(EXIT_SUCCESS);
}
