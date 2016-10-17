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
#include "line_histogram.hpp"

namespace prhlt {
    using namespace log4cxx;
    using namespace log4cxx::helpers;
    using namespace boost;
    const string Line_Histogram::horizontal = "HORIZONTAL";
    const string Line_Histogram::vertical = "VERTICAL";
    const string Line_Histogram::global = "GLOBAL";
    const string Line_Histogram::local = "LOCAL";
    const string Line_Histogram::mins = "MINIMUMS";
    const string Line_Histogram::maxs = "MAXIMUMS";
    
    Line_Histogram::Line_Histogram(int ex_threshold){
        this->logger = Logger::getLogger("PRHLT.LineHistogram");
		this->count=0;
		this->binarization_threshold = 127;
		this->image = cv::Mat(0,0,CV_8U,0);
		this->interest_zone = cv::Rect(0,0,0,0);
		this->is_initialized = false;
		this->binarization_threshold = ex_threshold;
		this->global_image=this->image;

	}	
	Line_Histogram::Line_Histogram(cv::Mat &ex_image, int ex_threshold){
		this->logger = Logger::getLogger("LineSegmenter.Histogram");
		this->count=0;
		LOG4CXX_DEBUG(this->logger,"<<INITIALIZING LINE HISTOGRAM>>"); 
		this->binarization_threshold = 127;
		if(ex_image.channels()>1){
		  this->image = cv::Mat(ex_image.rows,ex_image.cols,CV_8U,0);
			cvtColor(ex_image, this->image, CV_RGB2GRAY);
		}
    else
        this->image= ex_image.clone();
		this->interest_zone = cv::Rect(0,0,this->image.cols,this->image.rows);
		this->binarization_threshold = ex_threshold;
		this->is_initialized = false;
		this->global_image=this->image;
		LOG4CXX_DEBUG(this->logger,"<<INITIALIZING LINE HISTOGRAM>> [DONE]"); 
	}

	Line_Histogram::Line_Histogram(cv::Mat &ex_image, cv::Rect rec, int ex_threshold){
		this->logger = Logger::getLogger("LineSegmenter.Histogram");
		this->count=0;
		LOG4CXX_DEBUG(this->logger,"<<INITIALIZING LINE HISTOGRAM>>"); 
		this->binarization_threshold = 127;
		this->image = cv::Mat(ex_image.rows,ex_image.cols,CV_8U,0);
		if(ex_image.channels()>1){
		  this->image = cv::Mat(ex_image.rows,ex_image.cols,CV_8U,0);
			cvtColor(ex_image, this->image, CV_RGB2GRAY);
		}
    else
        this->image= ex_image.clone();
		this->image = ex_image.clone();
		this->binarization_threshold = ex_threshold;
		this->interest_zone = rec;
		this->is_initialized = false;
		this->global_image=this->image;
		LOG4CXX_DEBUG(this->logger,"<<INITIALIZING LINE HISTOGRAM>> [DONE]"); 
	}

	Line_Histogram::~Line_Histogram(){
		this->image.release();
		reset_histograms_lists();
	}

	float& Line_Histogram::operator[] (const int nIndex)
	{
		if ((nIndex >= 0) and (nIndex < this->image_histogram.size()))
			return this->image_histogram[nIndex];
	}

	float Line_Histogram::get_derivate_value(const int nIndex){

			return this->image_histogram_derivate[nIndex];
	}
	/*
	Histogram & Histogram::operator= (const Histogram & other)
    {
        if (this != &other) // protect against invalid self-assignment
        {
            // 1: allocate new memory and copy the elements
			this->image = other.image.clone();

			//show_internal_image(0.3);
			this->interest_zone = other.interest_zone;
			this->is_initialized = other.is_initialized;
			this->binarization_threshold = other.binarization_threshold;
			//cout << " b t: " <<  other.binarization_threshold << endl;
			this->orientation_mode = other.orientation_mode;
			this->area_mode = other.area_mode;
			this->count=other.count;
			this->global_count=other.global_count;
			//cout << "x: " << this->interest_zone.x << " y: " << this->interest_zone.y << " width: " << this->interest_zone.width << " height: " << this->interest_zone.height << endl;
        }
        // by convention, always return *this
        return *this;
    }
*/
	void Line_Histogram::set_interest_zone(cv::Rect rec){
		this->interest_zone = rec;
	}
	int Line_Histogram::get_binarization_threshold()
	{
		return this->binarization_threshold;
	}

	void Line_Histogram::reset_histograms_lists(){
		this->image_histogram.clear();
		this->max_list.clear();
		this->min_list.clear();
		this->image_histogram_derivate.clear();
	}

	void Line_Histogram::initialize_coordinate_system(string mode){
		
		if (mode == this->horizontal){
			this->zero.x = 0;
			this->zero.y = 0;
			this->increment.x = 0; 
			this->increment.y = 1;
			this->max_bar_size.x = this->image.cols;
			this->max_bar_size.y = 0;
		}
		else
		{
			this->zero.x = 0;
			this->zero.y = this->image.rows;
			this->increment.x = 1; 
			this->increment.y = 0;
			this->max_bar_size.x = 0;
			this->max_bar_size.y = -(this->image.rows);
		}
	}

	int Line_Histogram::get_size(){
		
		return this->image_histogram.size();
	}

	int Line_Histogram::get_grey_count(){
		return this->count;
	}

	int Line_Histogram::get_region_real_grey_count(string orientation_mode, string area_mode){
		LOG4CXX_INFO(this->logger,"GET REAL COUNT"); 
		calculation_initialization(orientation_mode,area_mode);
		this->image = cv::Mat(this->image,this->interest_zone);
		return get_real_grey_count();
	}

	int Line_Histogram::get_real_grey_count(){
		int count=0;
		for (int r=0; r < this->image.rows; r++)
			for (int c=0; c < this->image.cols; c++)
				if(this->image.at<uchar>(r,c) <= this->binarization_threshold)
					count++;
			
		return count;
	}

	int Line_Histogram::get_normalization_value(){
		//cout << "Global: " << this->global_count << " Local: " << this->count << "\n"; 
		if (this->area_mode == this->global)
			return this->global_count;
		else
			return this->count;
	}

	void Line_Histogram::calculation_initialization(string orientation_mode, string area_mode){

		if(not this->is_initialized)
		{
			//LOG4CXX_INFO(this->logger,"STARTING TO CALCULATE"); 
			//show_internal_image(0.3);
			//cout << "x: " << this->interest_zone.x << " y: " << this->interest_zone.y << " width: " << this->interest_zone.width << " height: " << this->interest_zone.height << endl;
			this->orientation_mode = orientation_mode;
			this->area_mode = area_mode;
			this->count=0;
			reset_histograms_lists();
			//cout << " b t: " <<  this->binarization_threshold << endl;
			//LOG4CXX_INFO(this->logger,"RLSA"); 
			this->global_count=get_real_grey_count();
			this->is_initialized = true;
		}
		else 
			reset_histograms_lists();
	}


	void Line_Histogram::calculate(string orientation_mode, string area_mode, int smoothing_factor,int derivate_window_size ){

		calculation_initialization(orientation_mode,area_mode);
		//show_internal_image(0.3);
		//cout << "x: " << this->interest_zone.x << " y: " << this->interest_zone.y << " width: " << this->interest_zone.width << " height: " << this->interest_zone.height << endl;
		//cout << "area: " << this->interest_zone.area() << endl;
		this->image = cv::Mat(this->image.clone(),this->interest_zone);
		//this->image = tmp_size;
		initialize_coordinate_system(orientation_mode);
		LOG4CXX_DEBUG(this->logger,"CALCULATING HISTOGRAMS");  
		calculate_line_histogram(orientation_mode);
		if (smoothing_factor > 0) 
			smooth_line_histogram(orientation_mode,smoothing_factor);
		calculate_histogram_derivate(derivate_window_size);
		this->image=this->global_image;
		
	}

	void Line_Histogram::show_internal_image(float scale){
		
		cv::Mat resized(this->image.rows*scale,this->image.cols*scale, CV_8UC3);
		cv::resize(this->image,resized,resized.size(), 0, 0);
		cv::namedWindow("Histogram Image");
		cv::imshow("Histogram Image",resized);
	    cv::waitKey(100000);
		cvDestroyWindow( "Histogram Image" );
	}

	void Line_Histogram::initialize_line_histogram(string mode){
		if (mode == this->horizontal){
			this->image_histogram.resize(this->image.rows);
			this->image_histogram_derivate.resize(this->image.rows);
		}
		else{
			this->image_histogram.resize(this->image.cols);
			this->image_histogram_derivate.resize(this->image.cols);
		}
	}


	void Line_Histogram::calculate_line_histogram(string mode){
		reset_histograms_lists();
		initialize_line_histogram(mode);
		
		for (int r=0; r < this->image.rows; r++)
			for (int c=0; c < this->image.cols; c++){
				update_histogram(mode,r,c,this->image.at<uchar>(r,c));	
			}
		perform_normalization();
	}

	void Line_Histogram::update_histogram(string mode, int rowIndex, int colIndex,float value){
		if(value <= this->binarization_threshold){
			if (mode == this->horizontal)
				this->image_histogram[rowIndex]  +=1.0;
			else
				this->image_histogram[colIndex]  +=1.0;
			this->count++;
		}
	}
	void Line_Histogram::calculate_maxs_mins(){

		this->image = cv::Mat(this->image.clone(),this->interest_zone);
		cv::Mat kmeans_image;
		cv::Mat kmeans_data(this->image_histogram);

		if (this->orientation_mode == this->horizontal)
			kmeans_image = this->image;
		else
			kmeans_image = this->image.t();

		

		Algorithm_KMeans kmeans(kmeans_data,kmeans_image);
		LOG4CXX_DEBUG(this->logger,"CALCULATING KMEANS"); 
		kmeans.run(this->binarization_threshold);

		cv::Mat line_labels= kmeans.get_labels();

		LOG4CXX_DEBUG(this->logger,"DONE CALCULATING KMEANS"); 
		LOG4CXX_DEBUG(this->logger,"MAXMINS FOR REAL"); 
		//calculate_maxs(line_labels);
		calculate_mins(line_labels);

		kmeans_image.release();
		kmeans_data.release();
		line_labels.release();
		LOG4CXX_DEBUG(this->logger,"Found " << this->min_list.size() << " mins");  
		LOG4CXX_DEBUG(this->logger,"Found " << this->max_list.size() << " maxs"); 
		this->image=this->global_image; 

	}

	void Line_Histogram::calculate_maxs(cv::Mat line_labels){
		float current_max = 0.0;
		int index = 0, max_index=0; 
		LOG4CXX_DEBUG(this->logger,"CALCULATING MAXS");  

		add_maximum(0);

		BOOST_FOREACH( float & f, this->image_histogram )
		{
			LOG4CXX_DEBUG(this->logger,"Current value: " << index <<":" << f); 
			if( f > 0.0004 and f > current_max)
			{
				LOG4CXX_DEBUG(this->logger,"Found possible max"); 
				max_index = index;
				current_max = f;
			}
			if( f <= 0.0004 and current_max>0.0)
			{
				LOG4CXX_DEBUG(this->logger,"Inserted max " << max_index <<":"  << current_max << " <<<<<<<<<<<<<<<<<<<<<<"); 
				add_maximum(max_index);
				current_max=0.0;
			}

			index++;
		}
		add_maximum(this->image_histogram.size()-1);

	}

	void Line_Histogram::calculate_mins(cv::Mat line_labels){

		//float current_min = 1.0;
		//int from,to,min_index = 0;
		bool to_add;

		//LOG4CXX_DEBUG(this->logger,"CALCULATING MINS");  

		add_minimum(0);

		for(int i = 0; i < line_labels.cols ; i++)
		{
			
			to_add = false;
			//cout << i << ": " << line_labels.at<uchar>(i) << endl;

			if (line_labels.at<int>(i) == Algorithm_KMeans::BS)
			{
				
				if (i == 0 or line_labels.at<int>(i-1) != Algorithm_KMeans::BS)
					to_add=true;
				if (i == line_labels.rows-1 or line_labels.at<int>(i+1) != Algorithm_KMeans::BS)
					to_add=true;
			}

			if (to_add)
			{
				add_minimum(i);
			//	cout << "added min--------------------------" << endl;
			}


		}

		add_minimum(line_labels.cols-1);

	}

	void Line_Histogram::add_maximum(int index){
		cv::Point tmp;

		if (this->orientation_mode == this->horizontal){
			tmp.x = this->zero.x;
			tmp.y = index;		
		}	
		else{
			tmp.x = index;
			tmp.y = this->zero.y;		
		}
		this->max_list.push_back(tmp);
	}

	void Line_Histogram::add_minimum(int index){
		cv::Point tmp;

		if (this->orientation_mode == this->horizontal){
			tmp.x = this->zero.x;
			tmp.y = index;		
		}	
		else{
			tmp.x = index;
			tmp.y = this->zero.y;		
		}
		this->min_list.push_back(tmp);
	}

	int Line_Histogram::extract_index_from_point(cv::Point p){
		if (this->orientation_mode == this->horizontal)
			return p.y;		
		else
			return p.x;		
	}

	line_array Line_Histogram::get_drawable_list(string list_mode){

		vector<cv::Point2d> current_list;

		if(list_mode == this->mins)
			current_list = this->min_list;
		else
			current_list = this->max_list;
		
		

		line_array lines(boost::extents[current_list.size()][2]);
		int i = 0;
		BOOST_FOREACH( cv::Point2d & p,current_list)
		{
			lines[i][0].x=p.x;
			lines[i][0].y=p.y;
			lines[i][1].x=p.x+this->max_bar_size.x;
			lines[i][1].y=p.y+this->max_bar_size.y;
			i++;
		}

		return lines;
	}


	vector<cv::Point2d> Line_Histogram::get_maximums(){
		return this->max_list;
	}
	vector<cv::Point2d> Line_Histogram::get_minimums(){
		return this->min_list;
	}

	void Line_Histogram::perform_normalization(){

		float norm_fact = (float)get_normalization_value();
	    int row = 0;	
		BOOST_FOREACH( float & f, this->image_histogram )
		{
			LOG4CXX_DEBUG(this->logger,"Row: " << row <<  " Grey pixels: " << f );  
			row+=1;
			if (norm_fact == 0)
				f=0;
			else
				f/=norm_fact;
			LOG4CXX_DEBUG(this->logger,"Histogram level: " << f);  
		}
	}

	void Line_Histogram::calculate_histogram_derivate(int window_size){
		
		for (int line = 0 ; line < this->image_histogram_derivate.size(); line++)
			this->image_histogram_derivate[line]= calculate_derivate_at(line,window_size);
	}

	float Line_Histogram::calculate_derivate_at(int line, int window_size){
		float differences=0.0;
		float bef,aft;
		float normalization_factor = 0.0;

		for(int r = 1; r <=window_size; r++)
		{
			bef = line - r < 0 ? this->image_histogram[line] : this->image_histogram[line-r];
			aft = line + r > (this->image_histogram_derivate.size()-1) ? this->image_histogram[line] : this->image_histogram[line+r];

			differences = r*(aft - bef);
			normalization_factor+=r*r;
		}
		normalization_factor*=2;

		return differences/normalization_factor;

	}

	void Line_Histogram::smooth_line_histogram(string mode, int num_smooth_columns){

		int half_smooth = num_smooth_columns/2;
		full_histogram temp_histogram(this->image_histogram);
		this->image_histogram.clear();
	    initialize_line_histogram( mode);
	    

		float sum = 0.0;
			
		for (int r = 0; r < half_smooth and r < this->image_histogram.size(); r++)
			sum+=temp_histogram[r];
		for (int r = 0 ; r < this->image_histogram.size(); r++){
			this->image_histogram[r]=sum/float(num_smooth_columns);
			if (r - half_smooth >= 0)
				sum-=temp_histogram[r-half_smooth];
			if (r + half_smooth < this->image_histogram.size())
				sum+=temp_histogram[r+half_smooth];
		}
		temp_histogram.clear();
	}
	line_array Line_Histogram::get_local_drawable_histogram(){

		line_array histogram_lines(boost::extents[this->image_histogram.size()][2]);
		cv::Point2d current(this->zero.x,this->zero.y);
		int i = 0;

		//LOG4CXX_DEBUG(this->logger,"Total grey pixels:" << this->count );

		BOOST_FOREACH( float f, this->image_histogram )
		{

			histogram_lines[i][0].x=current.x;
			histogram_lines[i][0].y=current.y;
			histogram_lines[i][1].x=current.x+(this->max_bar_size.x*f*10);
			histogram_lines[i][1].y=current.y+(this->max_bar_size.y*f*10);

		//	LOG4CXX_DEBUG(this->logger,"Histogram line: " << histogram_lines[i][0].x << " " << histogram_lines[i][0].y << " " << histogram_lines[i][1].x << " " << histogram_lines[i][1].y);
		//	LOG4CXX_DEBUG(this->logger,"Histogram level: " << f);  
			current.x += this->increment.x;
			current.y += this->increment.y;
			i++;
		}
			
		return histogram_lines;
	}



	line_array Line_Histogram::get_relative_drawable_histogram(cv::Rect rectangle){

		line_array histogram_lines = get_local_drawable_histogram();

		for (int i = 0; i < histogram_lines.size(); i++)
		{
			histogram_lines[i][0].x += rectangle.x;
			histogram_lines[i][0].y += rectangle.y;
			histogram_lines[i][1].x += rectangle.x;
			histogram_lines[i][1].y += rectangle.y;
		}

		return histogram_lines;
	}

}




