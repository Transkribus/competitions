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
#include "algorithm_kmeans.hpp"

namespace prhlt {


        Algorithm_KMeans::Algorithm_KMeans(cv::Mat &ex_data, cv::Mat &ex_image){    
            this->data= cv::Mat(ex_data.cols,ex_data.rows,CV_32F);    
            cvtColor(ex_image,this->image, CV_GRAY2RGB);
            ex_data.convertTo(this->data,CV_32F);
            this->data_labels = cv::Mat(1,ex_data.rows,CV_32F,0.0);           
        }
        Algorithm_KMeans::~Algorithm_KMeans(){
            this->centers.release();
            this->data.release();
            this->data_labels.release();
            this->center2label_map.clear();
        }

        void Algorithm_KMeans::run(int binarization_threshold){
            this->num_centers=15;
        
            this->center_grey_count.resize(this->num_centers);
            
            cv::TermCriteria term(cv::TermCriteria::EPS,1000, 0.00001);
            //cout << "HELLO" << endl; 
            cv::kmeans(this->data,this->num_centers,this->data_labels,term,20,cv::KMEANS_PP_CENTERS,this->centers);
            //cout << "HELLO" << endl; 
            
            /*for (int i = 0; i < this->data_labels.rows ; i++ )
            {
                cout << i << ": " << this->data_labels.at<int>(i) << " "<< this->data.at<float>(0,i)  << endl; // " -> " << this->center2label_map[this->data_labels.at<int>(0,i)] << endl;
            //    cout << i << ": " << this->data.at<float>(0,i) << " - " << this->centers.at<float>(0,this->data_labels.at<int>(0,i)) << endl;
            }*/
            //cout << this->centers << endl;
            //cout << "HELLO" << endl; 
            set_labels2centers(binarization_threshold);
            //cout << "HELLO" << endl; 
            //draw_result();
        }

        void Algorithm_KMeans::draw_result(){
            
            cv::Point2d from(0,0);
            cv::Point2d to(20,0);
            cv::Scalar color;

            for (int i = 0; i < this->data_labels.rows ; i++ )
            {
                if (this->center2label_map[this->data_labels.at<int>(0,i)]== Algorithm_KMeans::NL)
                    color = cv::Scalar(0,0,0);

                if (this->center2label_map[this->data_labels.at<int>(0,i)]== Algorithm_KMeans::IL)
                    color = cv::Scalar(0,0,255);

                if (this->center2label_map[this->data_labels.at<int>(0,i)]== Algorithm_KMeans::BS)
                    color = cv::Scalar(0,255,0);
                cv::line(this->image, from, to,color);
                to.y+=1;
                from.y+=1;

            }
            float scale = 0.3;
            string window_name = "KMEANS RESULTS";

            cv::Mat resized(this->image.rows*scale,this->image.cols*scale, CV_8UC3);
            cv::resize(this->image,resized,resized.size(), 0, 0);
            cv::namedWindow(window_name);
            cv::imshow(window_name,resized);
            cv::waitKey(30);
            resized.release();
           // cv::destroyWindow(window_name);

        }

        cv::Mat Algorithm_KMeans::get_labels(){

            cv::Mat line_labels = cv::Mat(1,this->data_labels.rows,CV_32F,0.0);            

            for (int i = 0; i < this->data_labels.rows ; i++ )
            {
                line_labels.at<int>(i)=this->center2label_map[this->data_labels.at<int>(i)];
            }

            return line_labels;
        }
        int Algorithm_KMeans::classify(cv::Mat sample){
            
            double min_distance = -1.0;
            double current_distance = -1.0;
            int min_index;
            cv::Mat current_center;

            for(int i = 0; i < this->num_centers; i++)
            {
                current_center=this->centers.row(i);
                current_distance = euclidean_distance(this->centers.row(i), sample);
                if (min_distance == -1.0 or current_distance < min_distance)
                {
                    min_distance = current_distance;
                    min_index = i;
                }
            }


            return this->center2label_map[min_index];

        }

        double Algorithm_KMeans::euclidean_distance(cv::Mat center,cv::Mat sample){
            
            double result=0.0;

            for (int i = 0; i < center.cols; i++)
            {
                result= pow((double)(center.at<float>(0,i) -  sample.at<float>(0,i)),2);
            }
            return sqrt(result);
        }

        void Algorithm_KMeans::set_labels2centers(int binarization_threshold){
            
            calculate_centers_grey_count(binarization_threshold);
            
            this->center2label_map.resize(this->num_centers);
            float min =  *(std::min_element(this->center_grey_count.begin(),this->center_grey_count.end()));
            float max =  *(std::max_element(this->center_grey_count.begin(),this->center_grey_count.end()));

            for (int i = 0; i < this ->num_centers; i++)
            {
                if(this->center_grey_count[i]==min)
                    this->center2label_map[i]=Algorithm_KMeans::BS;
                else 
                    if(this->center_grey_count[i]==max)
                        this->center2label_map[i]=Algorithm_KMeans::NL;
                     else
                        this->center2label_map[i]=Algorithm_KMeans::IL;
            }
        }

        void Algorithm_KMeans::calculate_centers_grey_count(int binarization_threshold){
            
            //cout << this->num_centers << " " << this->centers.cols << endl;

            for(int i = 0; i < this->num_centers; i++)            
            {
                this->center_grey_count[i]=this->centers.at<float>(0,i);
            }

            /*for(int i = 0; i < this->num_centers; i++)
                for (int j = 0; j < this->centers.cols; j++)
                {
                    if(this->centers.at<uchar>(i,j) <= binarization_threshold)
                        this->center_grey_count[i]+=1.0;
                }
            */

        }











}