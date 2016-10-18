#ifndef PAGE_FILE_HPP_45SDFXCB23
#define PAGE_FILE_HPP_45SDFXCB23

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
#include <iostream>
#include <fstream>
#include "line_region_list.hpp"
#include "pugixml.hpp"


namespace std {using namespace __gnu_cxx;}
using namespace std;

namespace prhlt {
    typedef std::pair<float, int> index_pair;
    typedef std::vector<index_pair> permutation_indices;
	class Page_File{
		public:
			Page_File(string ex_file_name);
			~Page_File();
			vector<vector<cv::Point2f> > get_regions();
			void load_image(cv::Mat image);
			void display_contours_and_boxes();
			void extract_line_images();
			int  calculate_mode_interline_space();
			void print_file_info();
			void add_text(vector<string> ex_text);
			void add_loaded_transcription_text();
			void save_xml(string new_file_name);
			void load_transcription_file(string transcription_file_name);
    		void load_line_limits(int ex_region , string ex_line_region_file_name);
			void load_line_limits(int ex_region , vector< vector <int> > ex_line_limits);
			void add_loaded_baselines(int correction_factor);
			vector <vector< vector <cv::Point> > > get_sorted_baselines();
			void clip_baselines();

            void print_old_format();
			void generate_countour_from_baseline(int descendent_offset, int ascendant_offset );
			void generate_countour_from_baseline(string line_id,int descendent_offset, int ascendant_offset );
			void generate_countour_from_baseline_interline_mode(int interline_mode, int descendent_percent, int ascendant_percent );
			void generate_countour_from_baseline_interline_mode(int descendent_percent, int ascendant_percent );
		private:
            log4cxx::LoggerPtr logger;
			cv::Mat image;
			cv::Scalar mean_grey;
			string file_name;
			pugi::xml_document doc;
			pugi::xml_parse_result result; 
    		vector <permutation_indices> paragraph_order;
    		permutation_indices region_order;
    		vector <permutation_indices> baseline_order;
    		vector <string> text;
            vector <vector< vector <cv::Point> > > contours;
            vector <vector< vector <cv::Point> > > baselines;
            vector <vector <cv::Mat> > line_images;
            vector <vector <int> > horizontal_max;
            vector < pugi::xml_node >   region_nodes;
            vector <vector < pugi::xml_node > >  line_nodes;
            vector< vector <cv::Rect> > bounding_rectangles;
            vector <int> baseline_length;
            vector <int> baseline_start;
            float average_baseline_start;
            float std_dev_baseline_start;
            float average_baseline_length;
            float std_dev_baseline_length;
            void calculate_baseline_horizontal_statistics();
            void load_contours();
            void load_baselines();
			void generate_line_images();
			void generate_line_images_with_alpha();
			void save_line_images(string base_file_name);
			void calculate_reading_order();
			void calculate_baseline_order();
			void calculate_line_order();
			void calculate_region_order();
			vector <cv::Point2f> extract_points_from_string(string point_string);
			string point_vectors_to_string(vector <cv::Point> ex_points );
			vector<cv::Point> sort_points_horizontally(vector<cv::Point> temp_baseline);
			//DESTRUCTOR HELPER FUNCTIONS
			void clean_text();
			void clean_contours();
			void clean_baselines();
			void clean_line_images();
			void clean_horizontal_max();
			void clean_line_nodes();
			void clean_bounding_rectangles();
	};
}

#endif /* End of include guard */
