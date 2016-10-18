#include "page_file.hpp"

namespace prhlt{
    using namespace log4cxx;
    using namespace log4cxx::helpers;
    using namespace boost;
    
	Page_File::Page_File(string ex_file_name){
        this->logger = Logger::getLogger("PRHLT.Page_File");
		this->file_name = ex_file_name;
        LOG4CXX_INFO(this->logger,"<<Loading Page Format File >> " << this->file_name);
		this->result = this->doc.load_file(this->file_name.c_str());
        //LOG4CXX_INFO(this->logger,"<<Loading contours >> " << this->file_name);
		load_contours();
    	//LOG4CXX_INFO(this->logger,"<<Loading baselines >> " << this->file_name);
		//load_baselines();
		//calculate_baseline_order();
        //LOG4CXX_INFO(this->logger,"<<Calculating order >> " << this->file_name);
		calculate_reading_order();
	}
    
	Page_File::~Page_File(){
		clean_text();
		clean_contours();
		clean_baselines();
		clean_line_images();
		clean_horizontal_max();
		clean_line_nodes();
		clean_bounding_rectangles();
	}

	void Page_File::clean_text(){
		this->text.clear();
	}
	void Page_File::clean_contours(){
		
		for(int i = 0; i < this->contours.size(); i++)
			for(int j = 0; j < this->contours[i].size();j++)
				this->contours[i][j].clear();

		this->contours.clear();
	}
	void Page_File::clean_baselines(){
		
		for(int i = 0; i < this->baselines.size(); i++)
			for(int j = 0; j < this->baselines[i].size();j++)
				this->baselines[i][j].clear();

		this->baselines.clear();
	}
	void Page_File::clean_line_images(){
		
		for(int i = 0; i < this->line_images.size(); i++)
			for(int j = 0; j < this->line_images[i].size();j++)
				this->line_images[i][j].release();

		this->line_images.clear();
	}
	void Page_File::clean_horizontal_max(){
		
		for(int i = 0; i < this->horizontal_max.size(); i++)
				this->horizontal_max[i].clear();

		this->horizontal_max.clear();
	}
	void Page_File::clean_line_nodes(){
		
		for(int i = 0; i < this->line_nodes.size(); i++)
				this->line_nodes[i].clear();

		this->line_nodes.clear();
	}
	void Page_File::clean_bounding_rectangles(){
		
		for(int i = 0; i < this->bounding_rectangles.size(); i++)
				this->bounding_rectangles[i].clear();

		this->bounding_rectangles.clear();
	}

	void Page_File::clip_baselines(){
		vector <cv::Point2f>  tmp_region;
	/*	vector <cv::Point2f>  tmp_baseline;
		pugi::xml_node page = this->doc.child("PcGts").child("Page");	
		
		for (pugi::xml_node text_region = page.child("TextRegion"); text_region; text_region = text_region.next_sibling("TextRegion"))
		{
			tmp_region.clear();
			LOG4CXX_INFO(this->logger,"Id:" << text_region.attribute("id").value());
			LOG4CXX_INFO(this->logger,"Type:" << text_region.attribute("type").value()<<":");
			if(((string)text_region.attribute("type").value()) != "floating"){
				LOG4CXX_INFO(this->logger,"LOADING");
				string point_string = text_region.child("Coords").attribute("points").value();
			    tmp_region = extract_points_from_string(point_string);	
				
				for (pugi::xml_node line_region = text_region.child("TextLine"); line_region; line_region = line_region.next_sibling("TextLine"))
				{
					tmp_baseline.clear();
					LOG4CXX_INFO(this->logger,"At line Id " << line_region.attribute("id").value());
					std::vector<std::string> string_values;
					string point_string = line_region.child("Baseline").attribute("points").value();
					tmp_baseline=extract_points_from_string(point_string);
					cv::clipLine(cv::boundingRect(cv::Mat(tmp_region),tmp_baseline.begin(),tmp_baseline.end());
					line_region.child("Baseline").attribute("points").set_value(point_vectors_to_string(tmp_baseline).c_str());
				}
			}
		}
*/
	}
	
	vector<vector<cv::Point2f> > Page_File::get_regions(){
		vector<vector<cv::Point2f> > regions;
		pugi::xml_node page = this->doc.child("PcGts").child("Page");	
		
		for (pugi::xml_node text_region = page.child("TextRegion"); text_region; text_region = text_region.next_sibling("TextRegion"))
		{
			LOG4CXX_DEBUG(this->logger,"Id:" << text_region.attribute("id").value());
			LOG4CXX_DEBUG(this->logger,"Type:" << text_region.attribute("type").value()<<":");
			if(((string)text_region.attribute("type").value()) != "floating"){
				LOG4CXX_DEBUG(this->logger,"LOADING");
				vector <cv::Point2f>  tmp_region;
				string point_string = text_region.child("Coords").attribute("points").value();
			    tmp_region = extract_points_from_string(point_string);	
				regions.push_back(tmp_region);
			}
		}
		return regions;

	}

	vector <cv::Point2f> Page_File::extract_points_from_string(string point_string){
				LOG4CXX_DEBUG(this->logger,"Coords are " << point_string);
        		std::vector<std::string> string_values;
				boost::split(string_values,point_string,boost::is_any_of(" "),boost::token_compress_on);
				vector <cv::Point2f>  tmp_region;
				for(int p = 0; p < string_values.size();p++){
					std::vector<std::string> string_point;
				   	LOG4CXX_DEBUG(this->logger,"\t \t String point " << string_values[p]);
					boost::split(string_point,string_values[p],boost::is_any_of(","),boost::token_compress_on);
					int x;
					istringstream(string_point[0]) >> x;
					int y; 
					istringstream(string_point[1]) >> y;
				   LOG4CXX_DEBUG(this->logger,"\t \t x " << x << " y " << y);
				   tmp_region.push_back(cv::Point(x,y));
				}
				return tmp_region;
	}

	void Page_File::load_baselines(){
		int regions = 0;
		int lines = 0;
		pugi::xml_node page = this->doc.child("PcGts").child("Page");	
		vector<cv::Point> temp_baseline;
		
		for (pugi::xml_node text_region = page.child("TextRegion"); text_region; text_region = text_region.next_sibling("TextRegion"))
		{
			permutation_indices tmp_order;
			vector < vector < cv::Point> > tmp_points;
			this->baselines.push_back(tmp_points);
			this->baseline_order.push_back(tmp_order);
			vector <pugi::xml_node> tmp_nodes;
			this->line_nodes.push_back(tmp_nodes);
			LOG4CXX_DEBUG(this->logger,"Id " << text_region.attribute("id").value());
			LOG4CXX_DEBUG(this->logger,"Type " << text_region.attribute("type").value());

			for (pugi::xml_node line_region = text_region.child("TextLine"); line_region; line_region = line_region.next_sibling("TextLine"))
			{
				lines+=1;
				int coord_count = 0;
				float coord_mean_y = 0.0;
				float max_coord_y = -1;
				float min_coord_y = 1000000;
				temp_baseline.clear();
				
        		std::vector<std::string> string_values;
				string point_string = line_region.child("Baseline").attribute("points").value();
				LOG4CXX_DEBUG(this->logger,"At line Id " << line_region.attribute("id").value());
				LOG4CXX_DEBUG(this->logger,"Coords are " << point_string);
				if(point_string != ""){
					boost::split(string_values,point_string,boost::is_any_of(" "),boost::token_compress_on);
					
					for(int p = 0; p < string_values.size();p++){
						std::vector<std::string> string_point;
						boost::split(string_point,string_values[p],boost::is_any_of(","),boost::token_compress_on);
						int x;
						istringstream(string_point[0]) >> x;
						int y; 
						istringstream(string_point[1]) >> y;
						LOG4CXX_DEBUG(this->logger,"\t \t x " << x << " y " << y);
						temp_baseline.push_back(cv::Point(x,y));
						coord_count += 1;
						max_coord_y = ( y > max_coord_y) ? y : max_coord_y;  
						min_coord_y = ( y < min_coord_y) ? y : min_coord_y;  
						coord_mean_y += y;
					}
					this->baselines[this->baselines.size()-1].push_back(temp_baseline);
					coord_mean_y /= coord_count;
					this->baseline_order[this->baseline_order.size()-1].push_back(std::make_pair(max_coord_y,this->baseline_order.size()));
					this->line_nodes[this->line_nodes.size()-1].push_back(line_region);
				}
			}
		}
	}
	vector <vector< vector <cv::Point> > > Page_File::get_sorted_baselines(){
		vector <vector< vector <cv::Point> > > sorted_baselines;


		return sorted_baselines;
	}

	int Page_File::calculate_mode_interline_space(){
		
		int mode_interline_space = 0;
		vector<int> interline_spaces;
		int last = -1;
		int current = -1;

		calculate_baseline_order();
		for(int j = 0 ; j < this->region_order.size(); j ++){
			int k = this->region_order[j].second;
			for(int i = 0 ; i < this->baseline_order[k].size(); i ++){
				
				current = (int)this->baseline_order[k][i].first;
				if (last != -1){
					interline_spaces.push_back(current - last);
				}
				last = current;
			}
		}
      	
      	sort(interline_spaces.begin(),interline_spaces.end());
      	
      	mode_interline_space = interline_spaces[(int)(interline_spaces.size()/2)];

		return mode_interline_space;
	}
/*	void Page_File::generate_countour_from_baseline_interline_mode( int descendant_percent, int ascendant_percent ){
		int interline_mode = calculate_mode_interline_space();
		generate_countour_from_baseline_interline_mode(interline_mode,descendant_percent,ascendant_percent );

	}
	void Page_File::generate_countour_from_baseline_interline_mode(int interline_mode, int descendant_percent, int ascendant_percent ){

		int descendant_offset = (interline_mode/100)*descendant_percent;
		int ascendant_offset = (interline_mode/100)*ascendant_percent; 
		generate_countour_from_baseline(descendant_offset,ascendant_offset);
	}

	int Page_File::estimate_average_interline_space(int region_id, int line_id, int window_size){

		int interline_space=0;

		return (int)(interline_space/window_size);

	}

	void Page_File::geneare_contour_from_baseline_local_mode( int window_estimation_size, int descendant_percent, int ascendant_percent){
		vector<cv::Point> temp_contour;
		clean_contours();
		
		vector < vector < cv::Point> > tmp_points;
		this->contours.push_back(tmp_points);

		
		this->contours[this->contours.size()-1].push_back(temp_contour);
		
		LOG4CXX_INFO(this->logger,"Num regions :  " << this->baselines.size());
		for(int j = 0 ; j < this->baselines.size(); j++){
			//int k = this->region_order[j].second;
			LOG4CXX_INFO(this->logger,"Lines in region :  " << this->baselines[j].size());
			for(int i = 0 ; i < this->baselines[j].size(); i++){
				int interline_mode=estimate_average_interline_space(j,i,window_estimation_size);
				int descendant_offset = (interline_mode/100)*descendant_percent;
				int ascendant_offset = (interline_mode/100)*ascendant_percent; 
				generate_contour_for_baseline(j,i,descendant_offset, ascendant_offset);
			}
		}



	}
	
	void Page_File::generate_countour_for_baseline(int region_id, int line_id,int descendant_offset, int ascendant_offset ){
				 
				vector<cv::Point> sorted_baseline=this->baselines[region_id][line_id];
				 pugi::xml_attribute line_points_attr = this->line_nodes[region_id][line_id].child("Coords").attribute("points");
				 vector<cv::Point> new_contour;
				 LOG4CXX_INFO(this->logger,"Generating contour for  " << this->line_nodes[region_id][line_id].attribute("id").value() << " points : " << sorted_baseline.size() );
				 for(int p=0; p < sorted_baseline.size(); p++){
				 	 LOG4CXX_INFO(this->logger,"Point " << p << " : " << sorted_baseline[p].x << " - " << sorted_baseline[p].y);
				 	 new_contour.insert(new_contour.begin(),cv::Point(sorted_baseline[p].x,sorted_baseline[p].y+ascendant_offset));
				 	 new_contour.push_back(cv::Point(sorted_baseline[p].x,sorted_baseline[p].y+descendant_offset));
				 }
				 line_points_attr.set_value(point_vectors_to_string(new_contour).c_str());
	}
*/

	void Page_File::generate_countour_from_baseline(int descendant_offset, int ascendant_offset ){
		vector<cv::Point> temp_contour;
		clean_contours();
		
		vector < vector < cv::Point> > tmp_points;
		this->contours.push_back(tmp_points);
		vector<vector<cv::Point2f> > regions = get_regions();
		int last = 0; 
		int bottom = 0;

		this->contours[this->contours.size()-1].push_back(temp_contour);
		
		LOG4CXX_DEBUG(this->logger,"Num regions :  " << this->baselines.size());
		for(int j = 0 ; j < this->baselines.size(); j++){
			cv::Rect containing_rect =  boundingRect(regions[j]);
			//int k = this->region_order[j].second;
			LOG4CXX_DEBUG(this->logger,"Lines in region :  " << this->baselines[j].size());
			last = containing_rect.y;
			for(int i = 0 ; i < this->baselines[j].size(); i++){
				//int h = this->baseline_order[k][i].second;
				 vector<cv::Point> sorted_baseline=this->baselines[j][i];
				 bottom = this->baselines[j][i][0].y;
				 for(int p = 1; p < this->baselines[j][i].size();p++){
				 	 bottom = ( (this->baselines[j][i][p].y > bottom) ? this->baselines[j][i][p].y : bottom); 
				 }

				 float interline_space = bottom - last; 
				 int ascendant_pixels =(int) ((interline_space/100.0)*ascendant_offset);
				 int descendant_pixels =(int) ((interline_space/100.0)*descendant_offset);

				 //clipLine(containing_rect, sorted_baseline[0], sorted_baseline[1]);

				 pugi::xml_attribute line_points_attr = this->line_nodes[j][i].child("Coords").attribute("points");
				 vector<cv::Point> new_contour;
				 LOG4CXX_DEBUG(this->logger,"Generating contour for  " << this->line_nodes[j][i].attribute("id").value() << " points : " << sorted_baseline.size() );
				 for(int p=0; p < sorted_baseline.size(); p++){
				 	 LOG4CXX_DEBUG(this->logger,"Point " << p << " : " << sorted_baseline[p].x << " - " << sorted_baseline[p].y);
				 	 new_contour.insert(new_contour.begin(),cv::Point(sorted_baseline[p].x,sorted_baseline[p].y+ascendant_pixels));
				 	 new_contour.push_back(cv::Point(sorted_baseline[p].x,sorted_baseline[p].y+descendant_pixels));
				 }
				 line_points_attr.set_value(point_vectors_to_string(new_contour).c_str());
				 last = bottom; 
			}
		}
	}
	void Page_File::generate_countour_from_baseline(string line_id, int descendant_offset, int ascendant_offset ){
		vector<cv::Point> temp_contour;
		clean_contours();
		
		vector < vector < cv::Point> > tmp_points;
		this->contours.push_back(tmp_points);
		vector<vector<cv::Point2f> > regions = get_regions();
		int last = 0; 
		int bottom = 0;

		this->contours[this->contours.size()-1].push_back(temp_contour);
		
		LOG4CXX_DEBUG(this->logger,"Num regions :  " << this->baselines.size());
		for(int j = 0 ; j < this->baselines.size(); j++){
			cv::Rect containing_rect =  boundingRect(regions[j]);
			//int k = this->region_order[j].second;
			LOG4CXX_DEBUG(this->logger,"Lines in region :  " << this->baselines[j].size());
			last = containing_rect.y;
			for(int i = 0 ; i < this->baselines[j].size(); i++){

				//int h = this->baseline_order[k][i].second;
				 vector<cv::Point> sorted_baseline=this->baselines[j][i];
				 bottom = this->baselines[j][i][0].y;
				 for(int p = 1; p < this->baselines[j][i].size();p++){
				 	 bottom = ( (this->baselines[j][i][p].y > bottom) ? this->baselines[j][i][p].y : bottom); 
				 }

				 float interline_space = bottom - last; 
				 int ascendant_pixels =(int) ((interline_space/100.0)*ascendant_offset);
				 int descendant_pixels =(int) ((interline_space/100.0)*descendant_offset);

				 //clipLine(containing_rect, sorted_baseline[0], sorted_baseline[1]);

				if(line_id == this->line_nodes[j][i].attribute("id").value())
				{
					pugi::xml_attribute line_points_attr = this->line_nodes[j][i].child("Coords").attribute("points");
					vector<cv::Point> new_contour;
					LOG4CXX_DEBUG(this->logger,"Generating contour for  " << this->line_nodes[j][i].attribute("id").value() << " points : " << sorted_baseline.size() );
					for(int p=0; p < sorted_baseline.size(); p++){
						LOG4CXX_DEBUG(this->logger,"Point " << p << " : " << sorted_baseline[p].x << " - " << sorted_baseline[p].y);
						new_contour.insert(new_contour.begin(),cv::Point(sorted_baseline[p].x,sorted_baseline[p].y+ascendant_pixels));
						new_contour.push_back(cv::Point(sorted_baseline[p].x,sorted_baseline[p].y+descendant_pixels));
					}
					line_points_attr.set_value(point_vectors_to_string(new_contour).c_str());
				}
				last = bottom; 
			}
		}
	}

	vector<cv::Point> Page_File::sort_points_horizontally(vector<cv::Point> temp_baseline){
		vector<cv::Point> res;

		return res;
	}
	
	string Page_File::point_vectors_to_string(vector <cv::Point> ex_points ){
		stringstream res;
		for(int j = 0 ; j < ex_points.size()-1; j++){
			res << ex_points[j].x   <<","<< ex_points[j].y<<" ";
		}
		res << ex_points.back().x   <<","<< ex_points.back().y;
		return res.str();
	}

	void Page_File::load_contours(){
		int regions = 0;
		int lines = 0;
		vector<cv::Point> temp_contour;
		vector<cv::Rect> temp_rectangles;
		pugi::xml_node page = this->doc.child("PcGts").child("Page");	
		
		for (pugi::xml_node text_region = page.child("TextRegion"); text_region; text_region = text_region.next_sibling("TextRegion"))
		{
			LOG4CXX_INFO(this->logger,"Id " << text_region.attribute("id").value());
			LOG4CXX_INFO(this->logger,"Type " << text_region.attribute("type").value());
			temp_rectangles.clear();
			regions += 1;
		    this->region_nodes.push_back(text_region);	
			vector < vector < cv::Point> > tmp_points;
			vector <pugi::xml_node> tmp_nodes;
			this->contours.push_back(tmp_points);
			permutation_indices tmp_order;
			vector<int> tmp_hor_max;
			this->line_nodes.push_back(tmp_nodes);
			this->paragraph_order.push_back(tmp_order);
			this->horizontal_max.push_back(tmp_hor_max);

			for (pugi::xml_node line_region = text_region.child("TextLine"); line_region; line_region = line_region.next_sibling("TextLine"))
			{
				lines+=1;
				temp_contour.clear();
				int coord_count = 0;
				float coord_mean_y = 0.0;
				int coord_max_x = -1;

        		std::vector<std::string> string_values;
				string point_string = line_region.child("Coords").attribute("points").value();
				LOG4CXX_INFO(this->logger,"Coords are " << point_string);
	
				boost::split(string_values,point_string,boost::is_any_of(" "),boost::token_compress_on);

				for(int p = 0; p < string_values.size();p++){
					std::vector<std::string> string_point;
					boost::split(string_point,string_values[p],boost::is_any_of(","),boost::token_compress_on);
					int x;
					istringstream(string_point[0]) >> x;
					int y; 
					istringstream(string_point[1]) >> y;
				   	LOG4CXX_DEBUG(this->logger,"\t \t x " << x << " y " << y);
				   	temp_contour.push_back(cv::Point(x,y));
				   	coord_count += 1;
				   	coord_mean_y += y;
				   	coord_max_x = coord_max_x > x ? coord_max_x : x;
				}

				/*for (pugi::xml_node point = line_region.child("Coords").child("Point"); point; point = point.next_sibling("Point")){
				   LOG4CXX_DEBUG(this->logger,"\t \t x " << point.attribute("x").value() << " y " << point.attribute("y").value());
				   temp_contour.push_back(cv::Point(point.attribute("x").as_int(),point.attribute("y").as_int()));
				   coord_count += 1;
				   coord_mean_y += point.attribute("y").as_int();
				   coord_max_x = coord_max_x > point.attribute("x").as_int() ? coord_max_x : point.attribute("x").as_int();
				}*/
			
				coord_mean_y /= coord_count;
                cv::Rect tmp_rec = cv::boundingRect(cv::Mat(temp_contour));
				LOG4CXX_DEBUG(this->logger,"\t Id " << line_region.attribute("id").value() << " y_mean : " << coord_mean_y << " max_x  : " << coord_max_x);
          		this->line_nodes[this->line_nodes.size()-1].push_back(line_region);
          		this->paragraph_order[this->paragraph_order.size()-1].push_back(std::make_pair(coord_mean_y,this->contours[this->contours.size()-1].size()));
          		this->horizontal_max[this->horizontal_max.size()-1].push_back(coord_max_x);

				temp_rectangles.push_back(cv::boundingRect(cv::Mat(temp_contour)));
				this->contours[this->contours.size()-1].push_back(temp_contour);

			}
			this->bounding_rectangles.push_back(temp_rectangles);
		}

	}

	void Page_File::display_contours_and_boxes(){
		cv::RNG rng(12345);
		cv::Mat drawing(this->image.rows,1.5*this->image.cols,this->image.type(),cv::Scalar(255,255,255));
		cv::Mat tmp(drawing,cv::Rect( 0,  0, this->image.cols,this->image.rows));
		this->image.copyTo(tmp);
        int fontFace = cv::FONT_HERSHEY_SIMPLEX;
        double fontScale = 2;
        int thickness = 3;  
	
		int line_count = 0;
		for(int i = 0 ; i < this->line_nodes.size(); i ++){
			cv::Scalar color = cv::Scalar(rng.uniform(0, 255),rng.uniform(0,255),rng.uniform(0,255) );
			if( i < this->region_order.size()){
				int k = this->region_order[i].second;
				if(k < this->bounding_rectangles.size())
				for(int j = 0; j < this->line_nodes[k].size(); j++){
					int h = this->paragraph_order[k][j].second;
					cv::drawContours(drawing,this->contours[k],h, color, 2, 8, vector<cv::Vec4i>(), 0, cv::Point() );
		    		cv::rectangle(drawing, this->bounding_rectangles[k][h],cv::Scalar(0,0,0),2,8,0);
					LOG4CXX_INFO(this->logger," Rec " << k << " Line " << h );
					LOG4CXX_INFO(this->logger," Total regions " << this->contours.size() << " Lines in reg " << this->contours[k].size());
					LOG4CXX_INFO(this->logger," Line" << line_count << "N Lines " << this->text.size());

					
					
					
				    cv::Point textPos(this->horizontal_max[k][h],this->paragraph_order[k][j].first);
					cv::putText(drawing,this->text[line_count],textPos,fontFace,fontScale,cv::Scalar(0,0,255),thickness);
					line_count++;
				}
			}
		}
/*
		cv::Point textPos(700,100);
		LOG4CXX_INFO(this->logger," Line " << line_count<< " - "  << this->text[line_count] << " N Lines " << this->text.size());
		while(line_count < this->text.size()){
			
			cv::putText(drawing,this->text[line_count],textPos,fontFace,fontScale,cv::Scalar(0,0,255),thickness);
			textPos.y+=100;
			line_count++;
		LOG4CXX_INFO(this->logger," Line" << line_count << " N Lines " << this->text.size());

		}
*/		
		/*
		
		for( int i = 0; i< this->contours.size(); i++ ){
			cv::Scalar color = cv::Scalar(rng.uniform(0, 255),rng.uniform(0,255),rng.uniform(0,255) );
	//		LOG4CXX_INFO(this->logger,"Num areas " << this->contours.size());
			vector< vector< cv::Point> > contour_vector = this->contours[i];
			for( int j = 0; j< contour_vector.size(); j++ ){

	//			LOG4CXX_INFO(this->logger,"Area " << i  << " Contour " << j << " has " << contour_vector[j].size());
				//LOG4CXX_INFO(this->logger,"x " << this->contours[i][j][0].x << " y " << this->contours[i][j][0].y);
				cv::drawContours(drawing,contour_vector,j, color, 2, 8, vector<cv::Vec4i>(), 0, cv::Point() );
			//	cv::polylines(drawing,contour_vector,true,color);
		    //  cv::rectangle(drawing, this->bounding_rectangles[i][j], color,2,8,0);
			}
		}*/
        cv::imwrite("global.png", drawing);

	}
	void Page_File::load_image(cv::Mat ex_image){
        //if(ex_image.channels()>1){
        //    this->image = cv::Mat(ex_image.rows,ex_image.cols,CV_8U,0);
        //    cvtColor(ex_image, this->image, CV_RGB2GRAY);
        //}
        //else
            this->image= ex_image.clone();
        this->mean_grey = cv::mean(this->image);
		LOG4CXX_DEBUG(this->logger," mean " << this->mean_grey[0]);
	}

	void Page_File::extract_line_images(){
		string base_name = this->file_name;
		unsigned found = this->file_name.find_last_of(".");
		LOG4CXX_INFO(this->logger," Found . at " << found);
		if(found!=-1)
			base_name.erase(found,-1);
		generate_line_images_with_alpha();
		//generate_line_images();
		save_line_images(base_name);
	}
	
	void Page_File::generate_line_images(){

		for( int i = 0; i< this->contours.size(); i++ ){
			vector <cv::Mat> tmp;
			this->line_images.push_back(tmp);
			vector< vector< cv::Point> > contour_vector = this->contours[i];
			for( int j = 0; j< contour_vector.size(); j++ ){
				cv::Mat mask = cv::Mat::zeros(this->image.rows,this->image.cols, CV_8UC1);
				drawContours(mask,contour_vector,j,cv::Scalar(255), CV_FILLED);
				//cv::Mat inv_mask(this->image.rows,this->image.cols, CV_8UC1,cv::Scalar(255));
				//drawContours(inv_mask,contour_vector,j,cv::Scalar(0), CV_FILLED);
				//cv::Scalar mean,stdev;
        		//this->mean_grey = cv::mean(this->image,mask);
        		//meanStdDev(this->image, mean, stdev,mask);	
        		//double maxval;
        		//cv::minMaxLoc(this->image,NULL, &maxval, NULL, NULL, mask);
// minMaxLoc(InputArray src, double* minVal, double* maxVal=0, Point* minLoc=0, Point* maxLoc=0, InputArray mask=noArray())
				//cv::Mat cutout_image(this->image.rows,this->image.cols, CV_8U,(int)maxval);
				//cv::Mat cutout_image(this->image.rows,this->image.cols, CV_8U,this->mean_grey[0]);
				//cv::Mat cutout_image(this->image.rows,this->image.cols,CV_8UC3);
				//this->image.copyTo(cutout_image,mask);
				cv::Mat cutout_image(this->image,this->bounding_rectangles[i][j]);
				//cutout_image.setTo(mean_grey);
				cv::Mat transparent( this->image.rows,this->image.cols, CV_8UC4);
				cv::Mat srcImg[] = {cutout_image,mask};
				int from_to[] = { 0,0, 1,1, 2,2, 3,3 };
				cv::mixChannels( srcImg, 2, &transparent, 1, from_to, 4 );
				cv::Mat cropped_image;
				cv::Mat(transparent,this->bounding_rectangles[i][j]).copyTo(cropped_image);
				this->line_images[this->line_images.size()-1].push_back(cropped_image);
				cropped_image.release();
				mask.release();
				cutout_image.release();
			}
		}
	}
	
	void Page_File::generate_line_images_with_alpha(){

		for( int i = 0; i< this->contours.size(); i++ ){
			vector <cv::Mat> tmp;
			this->line_images.push_back(tmp);
			vector< vector< cv::Point> > contour_vector = this->contours[i];
			
			for( int j = 0; j< contour_vector.size(); j++ ){
			
				cv::Mat mask = cv::Mat::zeros(this->image.rows,this->image.cols, CV_8UC1);
				drawContours(mask,contour_vector,j,cv::Scalar(255), CV_FILLED);
				cv::Mat transparent( this->image.rows,this->image.cols, CV_8UC4);
				cv::Mat srcImg[] = {this->image,mask};
				int from_to[] = { 0,0, 1,1, 2,2, 3,3 };
				cv::mixChannels( srcImg, 2, &transparent, 1, from_to, 4 );
				cv::Mat cropped_image;
				cv::Mat(transparent,this->bounding_rectangles[i][j]).copyTo(cropped_image);
				this->line_images[this->line_images.size()-1].push_back(cropped_image);
				cropped_image.release();
				mask.release();
				transparent.release();
			}
		}
	}
	
	void Page_File::calculate_reading_order(){
		LOG4CXX_DEBUG(this->logger," Sorting lines");
		calculate_line_order();
		LOG4CXX_DEBUG(this->logger," Sorting Regions");
		calculate_region_order();
		//LOG4CXX_INFO(this->logger," Sorting Baselines");
		//calculate_baseline_order();
		LOG4CXX_DEBUG(this->logger," Done sorting " << this->paragraph_order.size());
	}
	void Page_File::calculate_baseline_order(){
      for (int i = 0 ; i < this->baseline_order.size(); i++)
      	sort(this->baseline_order[i].begin(),this->baseline_order[i].end());
	}

	void Page_File::calculate_region_order(){
      for (int i = 0 ; i < this->paragraph_order.size(); i++){
	 	  if(this->paragraph_order[i].size() > 0)
      	  	this->region_order.push_back(std::make_pair(this->paragraph_order[i][this->paragraph_order[i].size()-1].first,i));
	  }
      sort(this->region_order.begin(),this->region_order.end());
	}

	void Page_File::calculate_line_order(){
      for (int i = 0 ; i < this->paragraph_order.size(); i++)
      	  sort(this->paragraph_order[i].begin(),this->paragraph_order[i].end());
	}


	void Page_File::save_line_images(string base_file_name){
		for(int i = 0 ; i < this->line_images.size(); i ++){
			if( i < this->region_order.size()){
				int k = this->region_order[i].second;
				for(int j = 0; j < this->line_images[k].size(); j++){
					if(j != this->paragraph_order[k][j].second)
						LOG4CXX_ERROR(this->logger," Out of place line >> " << j  << " for " << this->paragraph_order[k][j].second);
					int h = this->paragraph_order[k][j].second;
					stringstream png_file_name;//create a stringstream
                    //"_"<< this->region_nodes[k].attribute("id").value() << "_" << this->line_nodes[k][h].attribute("id").value()<<
					png_file_name << base_file_name << "_" << (i+1 < 10 ? "0" : "") << i+1 << "_" << (j+1 < 10 ? "0" : "") << j+1<< "_"<< this->region_nodes[k].attribute("id").value() << "_" << this->line_nodes[k][h].attribute("id").value()<<".png";
					//png_file_name << base_file_name << "_" << (i+1 < 10 ? "0" : "") << i+1 << "_" << (j+1 < 10 ? "0" : "") << j+1<< ".png";
					stringstream txt_file_name;//create a stringstream
					txt_file_name << base_file_name << "_" << (i+1 < 10 ? "0" : "") << i+1 << "_" << (j+1 < 10 ? "0" : "") << j+1<< "_"<< this->region_nodes[k].attribute("id").value() << "_" << this->line_nodes[k][h].attribute("id").value()<<".txt";
					//txt_file_name << base_file_name << "_" << (i+1 < 10 ? "0" : "") << i+1 << "_" << (j+1 < 10 ? "0" : "") << j+1<< ".txt";
             //cv::Mat tmp_image = cv::Mat(this->line_images[i][h].rows,this->line_images[i][h].cols,CV_8U,0);
             //cvtColor(this->line_images[i][h], tmp_image, CV_RGB2GRAY);
					LOG4CXX_INFO(this->logger," File : " << png_file_name.str());
             		cv::imwrite(png_file_name.str(),this->line_images[k][h]);
             		string line_transcription = (string) this->line_nodes[k][h].child("TextEquiv").child_value("Unicode");
             		ofstream txt_file;
             		   txt_file.open (txt_file_name.str().c_str());
             		   txt_file << line_transcription;
             		   txt_file.close();

             	}
             }
        }
    }

	void Page_File::print_file_info(){
		pugi::xml_node page = this->doc.child("PcGts").child("Page");	
		
		cout << "#Name:   " << page.attribute("imageFilename").value() << endl;
		cout << "#Width:  " << page.attribute("imageWidth").value() << endl;
		cout << "#Height: " << page.attribute("imageHeight").value() << endl;
		cout << "# Coord-X Coord-Y Width Height Id-1 Id-2 Id-PG-1 Id-PG-2" << endl;
		
		for(int i = 0 ; i < this->bounding_rectangles.size(); i ++){
			if( i < this->region_order.size()){
				int k = this->region_order[i].second;
		//		cout << "#Order: " << i << " is " << k  << endl;
				if(k < this->bounding_rectangles.size())
				for(int j = 0; j < this->bounding_rectangles[k].size(); j++){
					int h = this->paragraph_order[k][j].second;
                    cout << this->bounding_rectangles[k][h].x << " " << this->bounding_rectangles[k][h].y << " " << this->bounding_rectangles[k][h].width << " " << this->bounding_rectangles[k][h].height << " " << (i+1 < 10 ? "0" : "") << i+1 << " " << (j+1 < 10 ? "0" : "") << j+1 << " " << this->region_nodes[k].attribute("id").value() << " " << this->line_nodes[k][h].attribute("id").value()  << endl;
		//			cout << this->bounding_rectangles[k][h].width << " " << this->bounding_rectangles[k][h].height << endl;
				}
			}
		}
	}
    void Page_File::calculate_baseline_horizontal_statistics(){

    	  /*
    	  accumulator_set<double, stats<tag::variance> > acc;
    	  for_each(a_vec.begin(), a_vec.end(), bind<void>(ref(acc), _1));

    	  cout << mean(acc) << endl;
    	  cout << sqrt(variance(acc)) << endl;
    	  */

	}
    void Page_File::print_old_format(){
    	int line_count =0;
    	int bs_substract = 40;
    	int line_substract = 30;
    	//int line_substract = 0;
    	int line_add = 10;
    	//int line_add = 0;
		pugi::xml_node page = this->doc.child("PcGts").child("Page");	
    	cout << "# File " << page.attribute("imageFilename").value() << endl;
    	cout << "# Resl " << this->image.rows << " " << this->image.cols << endl;
		int last = 0;
		for(int j = 0 ; j < this->region_order.size(); j ++){
			int k = this->region_order[j].second;
	    	if(j==0){
	    		cout << "Line "<< ++line_count << ": " << last  << " " << (int) (this->baseline_order[k][0].first -bs_substract ) << " BS" << endl ;
				last = (int) (this->baseline_order[k][0].first -bs_substract );
			}
			for(int i = 0 ; i < this->baseline_order[k].size(); i ++){
				cout << "Line " << ++line_count << ": " << (int) last << " " << (int) (this->baseline_order[k][i].first -line_substract ) << " IL" << endl ;
				cout << "Line " << ++line_count << ": " << (int) (this->baseline_order[k][i].first -line_substract) << " " << (int) (this->baseline_order[k][i].first + line_add ) << " NL" << endl ;

				//CALCULATES 50% LIMIT FOR SEGMENTATION FORMAT
				//int next = i+1 < this->baseline_order.size() ? ((int)this->baseline_order[k][i].first+(int)this->baseline_order[k][i+1].first)/2 : this->baseline_order[k][i].first+30; 
				// USED FOR SEGMENTATION FORMAT
				//			cout << "Line " << ++line_count << ": " << (int) last << " " << (int) (this->baseline_order[k][i].first + line_add ) << " NL" << endl ;
				// USED FOR SEGMENTATION FORMAT 50%
				//			cout << "Line " << ++line_count << ": " << (int) last << " " << (int) (next) << " NL" << endl ;
				last = (int) this->baseline_order[k][i].first+line_add;
			}
		}
		cout << "Line "<< ++line_count << ": " << last  << " " << (this->image.rows-1) << " BS" << endl ;
	//	cout << "Line "<< ++line_count << ": " << last  << " " << (this->image.rows-1) << " NL" << endl ;

	}
	
	void Page_File::add_text(vector<string> ex_text){
		int line_count = 0;
		for(int i = 0 ; i < this->bounding_rectangles.size(); i ++){
		//for(int i = 0 ; i < this->line_nodes.size(); i ++){
			if( i < this->region_order.size()){
				int k = this->region_order[i].second;
				if(k < this->bounding_rectangles.size())
				for(int j = 0; j < this->bounding_rectangles[k].size(); j++){
				        int h = this->paragraph_order[k][j].second;
					pugi::xml_node text = this->line_nodes[k][h].append_child("TextEquiv").append_child("Unicode");
					text.append_child(pugi::node_pcdata).set_value(ex_text[line_count].c_str());
					line_count++;
				}
			}
		}
	}
	
	void Page_File::add_loaded_transcription_text(){
		add_text(this->text);
	}
	void Page_File::save_xml(string new_file_name){
		if (new_file_name == "")
			this->doc.save(std::cout);
		else
			 this->doc.save_file(new_file_name.c_str());
	}
	void Page_File::load_transcription_file(string transcription_file_name){
      ifstream file;
      bool size_line_found = false;
      string temp_line;
      file.open(transcription_file_name.c_str());
      if(file.is_open()){ 
         while(std::getline(file,temp_line)){
         	 this->text.push_back(temp_line);
			 //cout << this->text[this->text.size()-1] << endl;
      	}
	  }
	  if (file)
	  	  file.close();
	}
    
    void Page_File::load_line_limits(int ex_region , string ex_line_region_file_name){
		
		if(this->paragraph_order.size() > 1){
			ex_region = 0;
		}
		else
			ex_region = 0;
		Line_Region_List line_list(ex_line_region_file_name,0,this->image.rows);
        LOG4CXX_INFO(logger,"<<Loading baseline file>>");
        vector< vector <int> > line_limits = line_list.get_line_limits();
        load_line_limits(ex_region,line_limits);
     }

	void Page_File::load_line_limits(int ex_region , vector< vector <int> > ex_line_limits){
        LOG4CXX_INFO(logger,"<<Saving baselines in object>>");
		int width = this->image.cols-1;
        
        LOG4CXX_INFO(logger,"<<Resizing vectors>> " << this->paragraph_order.size());
		this->baselines.resize(this->paragraph_order.size());
		//this->baselines[ex_region].resize(ex_line_limits.size());
        LOG4CXX_INFO(logger,"<<Setting data>> " << ex_line_limits.size());

		for(int i = 0; i < ex_line_limits.size(); i++){
			vector <cv::Point> tmp_vector;
			tmp_vector.push_back(cv::Point(0,ex_line_limits[i][1]));
			tmp_vector.push_back(cv::Point(width,ex_line_limits[i][1]));
			this->baselines[ex_region].push_back(tmp_vector);
        LOG4CXX_INFO(logger,"<<Added Baselines>> " << this->baselines[ex_region].size());
		}
        LOG4CXX_INFO(logger,"<<Added Baselines>> " << this->baselines[ex_region].size());

	}

	void Page_File::add_loaded_baselines(int correction_factor){
		
		if(this->baselines.size() > 0){
		int reg_count = 0;
		int line_count = 0;
		pugi::xml_node page = this->doc.child("PcGts").child("Page");	
		
		for (pugi::xml_node text_region = page.child("TextRegion"); text_region; text_region = text_region.next_sibling("TextRegion"))
		{
			
			for(int i = 0; i < this->baselines[reg_count].size();i++){
				
				//NEW LINE
				pugi::xml_node line = text_region.append_child("TextLine");
				
				//ID ATRIBUTE 
				pugi::xml_attribute id_attr = line.append_attribute("id");
				stringstream ss;
				ss << "l" << line_count;
				id_attr.set_value(ss.str().c_str());
				
				pugi::xml_node line_coords=line.append_child("Coords");
				pugi::xml_attribute line_points_attr = line_coords.append_attribute("points");
				line_points_attr.set_value("");

				//BASE LINE
				pugi::xml_node baseline = line.append_child("Baseline");
				stringstream points_stream;
				
				for(int j = 0 ; j < this->baselines[reg_count][i].size()-1; j++){
					points_stream << this->baselines[reg_count][i][j].x   <<","<< this->baselines[reg_count][i][j].y+correction_factor<<" ";
				}
				points_stream << this->baselines[reg_count][i].back().x   <<","<< this->baselines[reg_count][i].back().y+correction_factor;
				pugi::xml_attribute points_attr = baseline.append_attribute("points");
				points_attr.set_value(points_stream.str().c_str());
				line_count++;
			}
			reg_count++;
		}
		
		}
	}


}
