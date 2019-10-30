#include "pch.h"

#include <opencv2/objdetect.hpp>
#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/dnn.hpp>
#include <dlib/opencv.h>
#include <dlib/image_processing/frontal_face_detector.h>
#include <dlib/image_processing/render_face_detections.h>
#include <iostream>
#include <stdio.h>
#include <dlib/dnn.h>

using namespace std;
using namespace cv;

template <long num_filters, typename SUBNET> using con5d = dlib::con<num_filters, 5, 5, 2, 2, SUBNET>;
template <long num_filters, typename SUBNET> using con5 = dlib::con<num_filters, 5, 5, 1, 1, SUBNET>;

template <typename SUBNET> using downsampler = dlib::relu<dlib::affine<con5d<32, dlib::relu<dlib::affine<con5d<32, dlib::relu<dlib::affine<con5d<16, SUBNET>>>>>>>>>;
template <typename SUBNET> using rcon5 = dlib::relu<dlib::affine<con5<45, SUBNET>>>;

using net_type = dlib::loss_mmod<dlib::con<1, 9, 9, 1, 1, rcon5<rcon5<rcon5<downsampler<dlib::input_rgb_image_pyramid<dlib::pyramid_down<6>>>>>>>>;

void detectAndDraw(Mat& img, CascadeClassifier& cascade,
	CascadeClassifier& nestedCascade,
	double scale, bool tryflip, cv::dnn::Net& net, dlib::frontal_face_detector& detector, net_type& dlibnet);

string cascadeName;
string nestedCascadeName;

const std::string caffeConfigFile = "C:/Users/PA544767/Desktop/opencvdlib64/opencv/etc/dnn/deploy.prototxt";
const std::string caffeWeightFile = "C:/Users/PA544767/Desktop/opencvdlib64/opencv/etc/dnn/res10_300x300_ssd_iter_140000_fp16.caffemodel";

const std::string tensorflowConfigFile = "C:/Users/PA544767/Desktop/opencvdlib64/opencv/etc/dnn/opencv_face_detector.pbtxt";
const std::string tensorflowWeightFile = "C:/Users/PA544767/Desktop/opencvdlib64/opencv/etc/dnn/opencv_face_detector_uint8.pb";

const std::string dlibcnn = "C:/dlib/mmod_human_face_detector.dat";

int main(int argc, const char** argv)
{
	VideoCapture capture;
	Mat frame, image;
	string inputName;
	bool tryflip;
	CascadeClassifier cascade, nestedCascade;
	double scale;

	cv::CommandLineParser parser(argc, argv,
		"{help h||}"
		"{cascade|C:/Users/PA544767/Desktop/opencvdlib64/opencv/etc/haarcascades/haarcascade_frontalface_default.xml|}"
		"{nested-cascade|C:/Users/PA544767/Desktop/opencvdlib64/opencv/etc/haarcascades/haarcascade_eye_tree_eyeglasses.xml|}"
		"{scale|1|}{try-flip||}{@filename||}"
	);
	if (parser.has("help"))
	{
		return 0;
	}
	cascadeName = parser.get<string>("cascade");
	nestedCascadeName = parser.get<string>("nested-cascade");
	scale = parser.get<double>("scale");
	if (scale < 1)
		scale = 1;
	scale = 4;
	tryflip = parser.has("try-flip");
	tryflip = false;
	inputName = parser.get<string>("@filename");
	if (!parser.check())
	{
		parser.printErrors();
		return 0;
	}

	if (!nestedCascade.load(nestedCascadeName))
		cerr << "WARNING: Could not load classifier cascade for nested objects" << endl;
	if (!cascade.load(cascadeName))
	{
		cerr << "ERROR: Could not load classifier cascade" << endl;
		return -1;
	}

	cv::dnn::Net net = cv::dnn::readNetFromCaffe(caffeConfigFile, caffeWeightFile);
	//cv::dnn::Net net = cv::dnn::readNetFromTensorflow(tensorflowWeightFile, tensorflowConfigFile);
	dlib::frontal_face_detector detector = dlib::get_frontal_face_detector();

	net_type dlibnet;
	dlib::deserialize(dlibcnn) >> dlibnet;

	if (inputName.empty() || (isdigit(inputName[0]) && inputName.size() == 1))
	{
		int camera = inputName.empty() ? 0 : inputName[0] - '0';
		if (!capture.open(camera, cv::CAP_DSHOW))
		{
			cout << "Capture from camera #" << camera << " didn't work" << endl;
			return 1;
		}
	}
	else if (!inputName.empty())
	{
		image = imread(samples::findFileOrKeep(inputName), IMREAD_COLOR);
		if (image.empty())
		{
			if (!capture.open(samples::findFileOrKeep(inputName)))
			{
				cout << "Could not read " << inputName << endl;
				return 1;
			}
		}
	}
	else
	{
		image = imread(samples::findFile("lena.jpg"), IMREAD_COLOR);
		if (image.empty())
		{
			cout << "Couldn't read lena.jpg" << endl;
			return 1;
		}
	}

	if (capture.isOpened())
	{
		capture.set(CAP_PROP_FRAME_WIDTH, 1280);
		capture.set(CAP_PROP_FRAME_HEIGHT, 720);

		cout << "Video capturing has been started ..." << endl;

		for (;;)
		{
			capture >> frame;
			if (frame.empty())
				break;

			//Mat frame1 = frame.clone();
			flip(frame, frame, 1);
			detectAndDraw(frame, cascade, nestedCascade, scale, tryflip, net, detector, dlibnet);

			char c = (char)waitKey(10);
			if (c == 27 || c == 'q' || c == 'Q')
				break;
		}
	}
	return 0;
}

void detectAndDraw(Mat& img, CascadeClassifier& cascade,
	CascadeClassifier& nestedCascade,
	double scale, bool tryflip, cv::dnn::Net& net, dlib::frontal_face_detector& detector, net_type& dlibnet)
{
	double t = 0;
	vector<Rect> faces, faces2;
	const static Scalar colors[] =
	{
		Scalar(255,0,0),
		Scalar(255,128,0),
		Scalar(255,255,0),
		Scalar(0,255,0),
		Scalar(0,128,255),
		Scalar(0,255,255),
		Scalar(0,0,255),
		Scalar(255,0,255)
	};
	Mat gray, smallImg;

	Mat dnncpy = img.clone();
	Mat dlibcpy = img.clone();

	cvtColor(img, gray, COLOR_BGR2GRAY);
	double fx = 1 / scale;
	resize(gray, smallImg, Size(), fx, fx, INTER_LINEAR_EXACT);
	equalizeHist(smallImg, smallImg);

	t = (double)getTickCount();
	cascade.detectMultiScale(smallImg, faces,
		1.1, 2, 0
		//|CASCADE_FIND_BIGGEST_OBJECT
		//|CASCADE_DO_ROUGH_SEARCH
		| CASCADE_SCALE_IMAGE,
		Size(30, 30), Size(72, 72));
	if (tryflip)
	{
		flip(smallImg, smallImg, 1);
		cascade.detectMultiScale(smallImg, faces2,
			1.1, 2, 0
			//|CASCADE_FIND_BIGGEST_OBJECT
			//|CASCADE_DO_ROUGH_SEARCH
			| CASCADE_SCALE_IMAGE,
			Size(30, 30));
		for (vector<Rect>::const_iterator r = faces2.begin(); r != faces2.end(); ++r)
		{
			faces.push_back(Rect(smallImg.cols - r->x - r->width, r->y, r->width, r->height));
		}
	}
	t = (double)getTickCount() - t;
	printf("opencv haar detection time = %g ms\n", t * 1000 / getTickFrequency());
	for (size_t i = 0; i < faces.size(); i++)
	{
		Rect r = faces[i];
		Mat smallImgROI;
		//vector<Rect> nestedObjects;
		Point center;
		Scalar color = Scalar(0, 0, 255);
		int radius;

		/*double aspect_ratio = (double)r.width / r.height;
		if (0.75 < aspect_ratio && aspect_ratio < 1.3)
		{
			center.x = cvRound((r.x + r.width*0.5)*scale);
			center.y = cvRound((r.y + r.height*0.5)*scale);
			radius = cvRound((r.width + r.height)*0.25*scale);
			circle(img, center, radius, color, 3, 8, 0);
		}
		else*/
		rectangle(img, Point(cvRound(r.x*scale), cvRound(r.y*scale)),
			Point(cvRound((r.x + r.width - 1)*scale), cvRound((r.y + r.height - 1)*scale)),
			color, 3, 8, 0);
		//if (nestedCascade.empty())
		//	continue;
		//smallImgROI = smallImg(r);
		//nestedCascade.detectMultiScale(smallImgROI, nestedObjects,
		//	1.1, 2, 0
		//	//|CASCADE_FIND_BIGGEST_OBJECT
		//	//|CASCADE_DO_ROUGH_SEARCH
		//	//|CASCADE_DO_CANNY_PRUNING
		//	| CASCADE_SCALE_IMAGE,
		//	Size(30, 30));
		//for (size_t j = 0; j < nestedObjects.size(); j++)
		//{
		//	Rect nr = nestedObjects[j];
		//	center.x = cvRound((r.x + nr.x + nr.width*0.5)*scale);
		//	center.y = cvRound((r.y + nr.y + nr.height*0.5)*scale);
		//	radius = cvRound((nr.width + nr.height)*0.25*scale);
		//	circle(img, center, radius, color, 3, 8, 0);
		//}
	}

	cv::Mat inputBlob = cv::dnn::blobFromImage(dnncpy, 300.0 / 720.0, cv::Size(300, 300), Scalar(), false, true);
	//cv::Mat inputBlob = cv::dnn::blobFromImage(frameOpenCVDNN, inScaleFactor, cv::Size(inWidth, inHeight), meanVal, true, false);
	t = (double)getTickCount();
	//net.setInput(inputBlob, "data", 4, Scalar(104.0, 177.0, 123.0));
	net.setInput(inputBlob, "data");
	cv::Mat detection = net.forward("detection_out");
	t = (double)getTickCount() - t;
	printf("opencv dnn detection time = %g ms\n", t * 1000 / getTickFrequency());
	cv::Mat detectionMat(detection.size[2], detection.size[3], CV_32F, detection.ptr<float>());
	double frameWidth = 1280;
	double frameHeight = 720;
	float confidenceThreshold = 0.8;
	for (int i = 0; i < detectionMat.rows; i++)
	{
		float confidence = detectionMat.at<float>(i, 2);
		if (confidence > confidenceThreshold)
		{
			int x1 = static_cast<int>(detectionMat.at<float>(i, 3) * 720) + 280;
			int y1 = static_cast<int>(detectionMat.at<float>(i, 4) * frameHeight);
			int x2 = static_cast<int>(detectionMat.at<float>(i, 5) * 720) + 280;
			int y2 = static_cast<int>(detectionMat.at<float>(i, 6) * frameHeight);
			cv::rectangle(img, cv::Point(x1, y1), cv::Point(x2, y2), cv::Scalar(0, 255, 0), 2, 4);
		}
	}

	Mat resizedDlib;
	resize(dnncpy, resizedDlib, Size(640, 360));
	dlib::cv_image<dlib::bgr_pixel> cimg(resizedDlib);
	// Detect faces 
	t = (double)cv::getTickCount();
	std::vector<dlib::rectangle> dlibfaces = detector(cimg);
	t = (double)cv::getTickCount() - t;
	printf("dlib hog detection time = %g ms\n", t * 1000 / cv::getTickFrequency());
	for (size_t i = 0; i < dlibfaces.size(); i++)
	{
		dlib::rectangle rr = dlibfaces[i];
		rectangle(img, Point(rr.left() * 2 , rr.top() * 2),
			Point(rr.right() * 2, rr.bottom() * 2),
			Scalar(255, 0, 0), 3, 8, 0);
	}

	
	/*Mat resizedDlib;
	resize(dnncpy, resizedDlib, Size(320, 180));
	dlib::cv_image<dlib::bgr_pixel> cimg2(resizedDlib);
	dlib::matrix<dlib::rgb_pixel> dlibimg;
	dlib::assign_image(dlibimg, cimg2);
	t = (double)cv::getTickCount();
	auto dets = dlibnet(dlibimg);
	t = (double)cv::getTickCount() - t;
	printf("dlib cnn detection time = %g ms\n", t * 1000 / cv::getTickFrequency());

	for (size_t i = 0; i < dets.size(); i++)
	{
		dlib::mmod_rect rr = dets[i];
		rectangle(img, Point(rr.rect.left() * 4, rr.rect.top() * 4),
			Point(rr.rect.right() * 4, rr.rect.bottom() * 4),
			Scalar(0, 0, 0), 3, 8, 0);
	}*/

	imshow("result", img);
}
