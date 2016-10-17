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
#include "image.hpp"

namespace prhlt {
    using namespace log4cxx;
    using namespace log4cxx::helpers;
    namespace std {using namespace __gnu_cxx;}
    using namespace std;
    using namespace boost;
    using namespace boost::filesystem;
    
    Image::Image(){
        this->logger = Logger::getLogger("PRHLT.Image");
        this->image_loaded=false;
        this->binarization_threshold=-1;
        this->image_binarized=false;
    }
    
    Image::~Image(){
        release_internal_images();
    }
    
    void Image::release_internal_images(){
        if(this->image_loaded){
            this->image.release();
            this->greyscale_image.release();
            this->image_loaded=false;
            if(this->image_binarized){
                this->binary_integral_image.release();
                this->binary_image.release();
                this->image_binarized=false;
            }
        }
    }
    
    bool Image::is_image_loaded(){
        return this->image_loaded;
    }
    
    bool Image::is_image_binarized(){
        return this->image_binarized;
    }
    
    int Image::get_binarization_threshold(){
        return this->binarization_threshold;
    }
    
    int Image::binarize_image(int ex_threshold){
        this->binarization_threshold=ex_threshold;
        this->image_binarized=true;
        initialize_binary_image_matrixes();
    }
    
    void Image::load_from_file(string file_path){
        release_internal_images();
        if(exists(file_path)){
            LOG4CXX_INFO(this->logger,"<<LOADING IMAGE FROM FILE>>");
            this->image=cv::imread(file_path,CV_LOAD_IMAGE_COLOR);//   CV_LOAD_IMAGE_GRAYSCALE);CV_LOAD_IMAGE_COLOR
            initialize_greyscale_image();
            this->image_loaded=true;
        }
        else
            LOG4CXX_ERROR(this->logger,"Indicated image path is not valid");	
    }
    
    void Image::load_from_matrix(cv::Mat &ex_image){
        release_internal_images();
        this->image = ex_image.clone();
        initialize_greyscale_image();
        this->image_loaded=true;
    }
    
    void Image::load_from_matrix_region(cv::Mat &ex_image, cv::Rect rec){
        release_internal_images();
        this->image =cv::Mat(ex_image.clone(),rec);
        initialize_greyscale_image();
        this->image_loaded=true;
    }
    
    void Image::initialize_greyscale_image(){
        LOG4CXX_DEBUG(this->logger,"<<BEFORE GREY SCALING>>");
        if(this->image.channels()>1){
            this->greyscale_image = cv::Mat(this->image.rows,this->image.cols,CV_8U,0);
            cvtColor(this->image, this->greyscale_image, CV_RGB2GRAY);
        }
        else
            this->greyscale_image= this->image.clone();
        
        LOG4CXX_DEBUG(this->logger,"<<AFTER GREYS SCALING>>");
    }
    
    void Image::initialize_binary_image_matrixes(){
        
        if( not is_image_binarized())
            LOG4CXX_ERROR(this->logger,"Attempted to initialize binary matrix before time");
        
        if (this->image_loaded){//BINARIZE IMAGE - 0 is black , 255 is white
            this->binary_image.release();
            this->binary_image = cv::Mat(this->greyscale_image.rows,this->greyscale_image.cols,CV_8U,0);
            cv::Mat tmp(this->greyscale_image.rows,this->greyscale_image.cols,CV_8U,0);
            cv::threshold(this->greyscale_image,this->binary_image,this->binarization_threshold,255,cv::THRESH_BINARY);
            
            //Count black pixels , we set foreground pixels to 1 and the background to 0 so that the threshold image
            //so that the threshold image will count the number of black pixels
            cv::threshold(this->greyscale_image,tmp,this->binarization_threshold,1,cv::THRESH_BINARY_INV);
            this->binary_integral_image.release();
            this->binary_integral_image = cv::Mat(this->greyscale_image.rows,this->greyscale_image.cols,CV_8U,0);
            cv::integral(tmp, this->binary_integral_image,CV_8U);
        }
    }
    
    void Image::save_image(string file_path){
        LOG4CXX_INFO(this->logger,"<<SAVING IMAGE TO FILE>>");
        cv::imwrite(file_path, this->image);
    }
  
    Image Image::clone_image(){
        Image new_image;
        new_image.load_from_matrix(this->image);
        return new_image;
    }
    
    bool Image::is_foreground_pixel(int r,int c){
        if( is_image_binarized() )
            if (coordinates_inside_image(r,c))
                if (this->image.at<uchar>(r,c)<=this->binarization_threshold)
                    return true;
                else
                    return false;
            else
                LOG4CXX_DEBUG(this->logger,"Tried to find if a pixel outside the image limits is foreground or not");
        return false;
    }
    
    bool Image::coordinates_inside_image(int r, int c){
        
        if ( (r >= 0) and (r < this->image.rows) and (c>=0) and ( c < this->image.cols)) 
            return true;
        else 
            return false;
    }
    
    cv::Rect Image::get_area_rectangle(){
        return cv::Rect(0,0,this->image.cols,this->image.rows);
    }
    
    cv::Mat Image::get_matrix(){
        return this->image;
    }
    cv::Mat Image::get_binary_matrix(){
        return this->binary_image;
    }
    
    int Image::get_num_rows(){
        return this->image.rows;
    }
    
    int Image::get_num_columns(){
        return this->image.cols;
    }
    
    void Image::display_with_scale(string window_name, float scale,int wait_time,bool destroy_on_exit){
        if (this->image_loaded){
            LOG4CXX_DEBUG(this->logger,"<<SHOWING SCALED IMAGE>>");
            cv::Mat resized(this->image.rows*scale,this->image.cols*scale, CV_8UC3);
            cv::resize(this->image,resized,resized.size(), 0, 0);
            cv::namedWindow(window_name);
            cv::imshow(window_name,resized);
            cv::waitKey(wait_time);
            if (destroy_on_exit)
                cv::destroyWindow(window_name);
            resized.release();
        }
    }
    
    void Image::display_binarized_with_scale(string window_name, float scale,int wait_time, bool destroy_on_exit){
        if ((this->image_loaded) and ( is_image_binarized() )){
            LOG4CXX_DEBUG(this->logger,"<<SHOWING BINARIZED SCALED IMAGE>>");
            cv::Mat resized(this->binary_image.rows*scale,this->binary_image.cols*scale, CV_8U);
            cv::resize(this->binary_image,resized,resized.size(), 0, 0);
            cv::namedWindow(window_name);
            cv::imshow(window_name,resized);
            cv::waitKey(wait_time);
            if (destroy_on_exit)
                cv::destroyWindow(window_name);
            resized.release();
        }
    }
    
    Image Image::draw_histogram(cv::Rect area_rectangle , Line_Histogram hist, cv::Scalar color){
        Image new_image = clone_image();
        line_array histogram_lines =hist.get_relative_drawable_histogram(area_rectangle);
        
        for(int i = 0; i < hist.get_size();i++){
            new_image.draw_line(histogram_lines[i][0],histogram_lines[i][1],color);
        }
        
        return new_image;		
    }
    void Image::draw_line(cv::Point2d from, cv::Point2d to,cv::Scalar color){
        cv::line(this->image, from, to,color,5);
    }
    
    void Image::overlay_image_with_color(cv::Mat input_mat, cv::Scalar color){
        for(int x = 0; x < this->image.rows;x++)
        	for(int y = 0; y < this->image.cols;y++){
        		if(input_mat.at<uchar>(x,y)==0){
					cv::circle(this->image,cv::Point2d(y,x),5,color);
            		this->image.at<cv::Vec3b>(x,y)[0] = 0;
            		this->image.at<cv::Vec3b>(x,y)[1] = 0;
            		this->image.at<cv::Vec3b>(x,y)[2] = 255;
				}
            		//this->image.at<cv::Scalar>(x,y) = color;
            }
    }
    
    void Image::draw_lines(line_array lines,cv::Scalar color){
        
        LOG4CXX_DEBUG(this->logger,"Image cols: " << this->image.cols << " rows: " << this->image.rows);
        LOG4CXX_DEBUG(this->logger,"DRAWING " << lines.size() <<  " LINES!");
        
        for(int i = 0; i < lines.size(); i++){
            LOG4CXX_DEBUG(this->logger,"DRAWING LINE");
            LOG4CXX_DEBUG(this->logger,"Drawing from: " << lines[i][0].x << " " << lines[i][0].y );
            LOG4CXX_DEBUG(this->logger,"Drawing to  : " << lines[i][1].x << " " << lines[i][1].y );
            draw_line(lines[i][0],lines[i][1],color);	
            draw_line(lines[i][0],cv::Point2d(this->image.cols,this->image.rows),color);   
        }
    }
    
    void Image::draw_randomed_colored_region(vector<cv::Point2d> points){
        CvRNG rng;
        int icolor = (unsigned) rng;
        for(int i = 0; i < points.size();i++){
            LOG4CXX_DEBUG(this->logger,"Painting :" << points[i].x << " - " << points[i].y);
            //this->image.at<cv::Vec3b>(points[i].x,points[i].y)[0] = icolor&255;
            this->image.at<cv::Vec3b>(points[i].x,points[i].y)[0] = 0;
            //this->image.at<cv::Vec3b>(points[i].x,points[i].y)[1] = (icolor>>8)&255;
            this->image.at<cv::Vec3b>(points[i].x,points[i].y)[1] = 0;
            //this->image.at<cv::Vec3b>(points[i].x,points[i].y)[2] = (icolor>>16)&255;
            this->image.at<cv::Vec3b>(points[i].x,points[i].y)[2] = 255;
        }
    }
    
    void Image::encircle_points(vector<cv::Point2d> points,int radius,cv::Scalar color){

    	for(int i = 0; i < points.size(); i++){
			cv::circle(this->image,cv::Point2d(points[i].y,points[i].x),radius,color);
		}
	}
    
    void Image::draw_randomed_colored_polyline(vector<cv::Point2d> points){
        CvRNG rng;
        cv::Scalar color = random_color(&rng);
        if(points.size()<2){
            LOG4CXX_ERROR(this->logger,"Image: attempted to draw a polyline with less than two points");
        }
        else
            for(int i = 1; i < points.size();i++){
                draw_line(points[i-1],points[i],color);	
            }
    }
  
    void Image::draw_polyline(vector<cv::Point2d> points, cv::Scalar color){
        if(points.size()<2){
            LOG4CXX_ERROR(this->logger,"Image: attempted to draw a polyline with less than two points");
        }
        else
            for(int i = 1; i < points.size();i++)
                draw_line(points[i-1],points[i],color);	
    }
    
    void Image::draw_rectangle(cv::Rect rec,cv::Scalar color){
        cv::rectangle(this->image,rec,color,-1,8,0);
    }
    
    void Image::draw_rectangles(rectangules_list rec_list){
        CvRNG rng;
        BOOST_FOREACH( cv::Rect &rec, rec_list ){
            draw_rectangle(rec,random_color(&rng));
			  }
		}
		
		pixel_results Image::calculate_pixels_in_regions(rectangules_list rec_list){
		    pixel_results results(boost::extents[rec_list.size()][2]);
		    int rec_index=0;
		    if( is_image_binarized() )
		    {
		        BOOST_FOREACH( cv::Rect &rec, rec_list )
		        {
		            if ((rec.x + rec.width <= this->image.cols) and (rec.y + rec.height <= this->image.rows) and rec.area() > 0){
		                results[rec_index][0]= this->binary_integral_image.at<int>(rec.y+rec.height,rec.x+rec.width)+ this->binary_integral_image.at<int>(rec.y,rec.x) - this->binary_integral_image.at<int>(rec.y+rec.height,rec.x) - this->binary_integral_image.at<int>(rec.y,rec.x+rec.width);
		                results[rec_index][1]=rec.area();
		            }
		            else{
		                results[rec_index][0]=0.0;
		                results[rec_index][1]=0.0;
		            }
		            rec_index++;
		        }
		    }
		    return results;
		}
        
        void Image::draw_text(cv::Point pos, string text){
        	int fontFace = cv::FONT_HERSHEY_SCRIPT_SIMPLEX;
        	double fontScale = 2;
        	int thickness = 3;  
			cv::putText(this->image,text,pos,fontFace,fontScale,cv::Scalar::all(255),thickness);

		}
		
		int Image::get_num_grey_pixels_in_subregion(cv::Rect rec){
		    if( is_image_binarized() )
		        if ((rec.x + rec.width <= this->image.cols) and (rec.y + rec.height <= this->image.rows) and rec.area() > 0)
		            return this->binary_integral_image.at<int>(rec.y+rec.height,rec.x+rec.width)+ this->binary_integral_image.at<int>(rec.y,rec.x) - this->binary_integral_image.at<int>(rec.y+rec.height,rec.x) - this->binary_integral_image.at<int>(rec.y,rec.x+rec.width);
		    
		    return 0;
    }
    
    cv::Mat Image::get_subregion_matrix(cv::Rect rec){
        
        if ((rec.x + rec.width <= this->image.cols) and (rec.y + rec.height <= this->image.rows)){
            cv::Mat tmp(this->image.clone(),rec);
            return tmp;
        }
        else 
            LOG4CXX_ERROR(this->logger,"Indicated subregion exceeds image size");
        return cv::Mat();
    }
    
    cv::Scalar Image::random_color(CvRNG *rng){
        int icolor = cvRandInt(rng);
        return cv::Scalar( icolor&255, (icolor>>8)&255, (icolor>>16)&255 );
    }
}
