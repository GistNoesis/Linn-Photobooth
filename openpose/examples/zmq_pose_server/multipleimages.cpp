// MultipleImages   ----a (quickly hacked) zmq server to serve the pose over the wire
// Inspired by the OpenPoseLibrary Tutorial - Pose - Example 1


// ------------------------- OpenPose Library Tutorial - Pose - Example 1 - Extract from Image -------------------------
// This first example shows the user how to:
    // 1. Load an image (`filestream` module)
    // 2. Extract the pose of that image (`pose` module)
    // 3. Render the pose on a resized copy of the input image (`pose` module)
    // 4. Display the rendered pose (`gui` module)
// In addition to the previous OpenPose modules, we also need to use:
    // 1. `core` module: for the Array<float> class that the `pose` module needs
    // 2. `utilities` module: for the error & logging functions, i.e. op::error & op::log respectively

// 3rdparty dependencies
// GFlags: DEFINE_bool, _int32, _int64, _uint64, _double, _string
#include <gflags/gflags.h>
// Allow Google Flags in Ubuntu 14
#ifndef GFLAGS_GFLAGS_H_
    namespace gflags = google;
#endif
// OpenPose dependencies
#include <openpose/core/headers.hpp>
#include <openpose/filestream/headers.hpp>
#include <openpose/gui/headers.hpp>
#include <openpose/pose/headers.hpp>
#include <openpose/utilities/headers.hpp>

#include <iostream>
#include <zmq.hpp>


// See all the available parameter options withe the `--help` flag. E.g. `build/examples/openpose/openpose.bin --help`
// Note: This command will show you flags for other unnecessary 3rdparty files. Check only the flags for the OpenPose
// executable. E.g. for `openpose.bin`, look for `Flags from examples/openpose/openpose.cpp:`.
// Debugging/Other
DEFINE_int32(logging_level,             3,              "The logging level. Integer in the range [0, 255]. 0 will output any log() message, while"
                                                        " 255 will not output any. Current OpenPose library messages are in the range 0-4: 1 for"
                                                        " low priority messages and 4 for important ones.");
// Producer
DEFINE_string(image_path,               "examples/media/COCO_val2014_000000000192.jpg",     "Process the desired image.");
// OpenPose
DEFINE_string(model_pose,               "COCO",         "Model to be used. E.g. `COCO` (18 keypoints), `MPI` (15 keypoints, ~10% faster), "
                                                        "`MPI_4_layers` (15 keypoints, even faster but less accurate).");
DEFINE_string(model_folder,             "models/",      "Folder path (absolute or relative) where the models (pose, face, ...) are located.");
DEFINE_string(net_resolution,           "-1x368",       "Multiples of 16. If it is increased, the accuracy potentially increases. If it is"
                                                        " decreased, the speed increases. For maximum speed-accuracy balance, it should keep the"
                                                        " closest aspect ratio possible to the images or videos to be processed. Using `-1` in"
                                                        " any of the dimensions, OP will choose the optimal aspect ratio depending on the user's"
                                                        " input value. E.g. the default `-1x368` is equivalent to `656x368` in 16:9 resolutions,"
                                                        " e.g. full HD (1980x1080) and HD (1280x720) resolutions.");
DEFINE_string(output_resolution,        "-1x-1",        "The image resolution (display and output). Use \"-1x-1\" to force the program to use the"
                                                        " input image resolution.");
DEFINE_int32(num_gpu_start,             0,              "GPU device start number.");
DEFINE_double(scale_gap,                0.3,            "Scale gap between scales. No effect unless scale_number > 1. Initial scale is always 1."
                                                        " If you want to change the initial scale, you actually want to multiply the"
                                                        " `net_resolution` by your desired initial scale.");
DEFINE_int32(scale_number,              1,              "Number of scales to average.");
// OpenPose Rendering
DEFINE_bool(disable_blending,           false,          "If enabled, it will render the results (keypoint skeletons or heatmaps) on a black"
                                                        " background, instead of being rendered into the original image. Related: `part_to_show`,"
                                                        " `alpha_pose`, and `alpha_pose`.");
DEFINE_double(render_threshold,         0.05,           "Only estimated keypoints whose score confidences are higher than this threshold will be"
                                                        " rendered. Generally, a high threshold (> 0.5) will only render very clear body parts;"
                                                        " while small thresholds (~0.1) will also output guessed and occluded keypoints, but also"
                                                        " more false positives (i.e. wrong detections).");
DEFINE_double(alpha_pose,               0.6,            "Blending factor (range 0-1) for the body part rendering. 1 will show it completely, 0 will"
                                                        " hide it. Only valid for GPU rendering.");


class PoseServer
{
    public :
    PoseServer( )
    {
    const auto outputSize = op::flagsToPoint(FLAGS_output_resolution, "-1x-1");
    // netInputSize
    const auto netInputSize = op::flagsToPoint(FLAGS_net_resolution, "-1x368");
    // poseModel
    const auto poseModel = op::flagsToPoseModel(FLAGS_model_pose);
    // Check no contradictory flags enabled
    if (FLAGS_alpha_pose < 0. || FLAGS_alpha_pose > 1.)
        op::error("Alpha value for blending must be in the range [0,1].", __LINE__, __FUNCTION__, __FILE__);
    if (FLAGS_scale_gap <= 0. && FLAGS_scale_number > 1)
        op::error("Incompatible flag configuration: scale_gap must be greater than 0 or scale_number = 1.",
                  __LINE__, __FUNCTION__, __FILE__);
    // Enabling Google Logging
    const bool enableGoogleLogging = true;
    // Logging
    op::log("", op::Priority::Low, __LINE__, __FUNCTION__, __FILE__);
    // Step 3 - Initialize all required classes
    scaleAndSizeExtractor = std::shared_ptr<op::ScaleAndSizeExtractor>(new op::ScaleAndSizeExtractor( netInputSize, outputSize, FLAGS_scale_number, FLAGS_scale_gap));

    poseExtractorCaffe = std::shared_ptr<op::PoseExtractorCaffe>(new op::PoseExtractorCaffe(poseModel, FLAGS_model_folder,
                                              FLAGS_num_gpu_start, {}, op::ScaleMode::ZeroToOne, enableGoogleLogging));
    poseExtractorCaffe->initializationOnThread();
    }

    void computePoseFromImage(const cv::Mat& inputImage, std::ostringstream& os)
    {
        // = op::loadImage(imageName, CV_LOAD_IMAGE_COLOR);
        if(inputImage.empty())
        op::error("Could not open or find the image: " + FLAGS_image_path, __LINE__, __FUNCTION__, __FILE__);
        const op::Point<int> imageSize{inputImage.cols, inputImage.rows};
        // Step 2 - Get desired scale sizes
        std::vector<double> scaleInputToNetInputs;
        std::vector<op::Point<int>> netInputSizes;
        double scaleInputToOutput;
        op::Point<int> outputResolution;
        std::tie(scaleInputToNetInputs, netInputSizes, scaleInputToOutput, outputResolution) =
        scaleAndSizeExtractor->extract(imageSize) ;
        op::CvMatToOpInput cvMatToOpInput;
        op::CvMatToOpOutput cvMatToOpOutput;
        // Step 3 - Format input image to OpenPose input and output formats
        const auto netInputArray = cvMatToOpInput.createArray(inputImage, scaleInputToNetInputs, netInputSizes);
        auto outputArray = cvMatToOpOutput.createArray(inputImage, scaleInputToOutput, outputResolution);
        // Step 4 - Estimate poseKeypoints
        poseExtractorCaffe->forwardPass(netInputArray, imageSize, scaleInputToNetInputs);
        const auto poseKeypoints = poseExtractorCaffe->getPoseKeypoints();

        const auto numberPeopleDetected = poseKeypoints.getSize(0);
        const auto numberBodyParts = poseKeypoints.getSize(1);
        // Easy version
        os << "[" ;
        for( int person = 0 ; person < numberPeopleDetected ; person++)
        {
            os << "[" ;

            for( int part = 0 ; part < numberBodyParts ; part++)
            {
                const auto x = poseKeypoints[{person, part, 0}];
                const auto y = poseKeypoints[{person, part, 1}];
                const auto score = poseKeypoints[{person, part, 2}];
                 os << "{  \"x\" : " << x << ", \"y\" : " << y << ", \"score\" : " << score << "}";
                 if( part != numberBodyParts-1)
                    os << ",";
            }
            os << "]";
            if( person != numberPeopleDetected-1)
                os << ",";


        }
        os << "]";

    }
    std::shared_ptr<op::ScaleAndSizeExtractor> scaleAndSizeExtractor;
    std::shared_ptr<op::PoseExtractorCaffe> poseExtractorCaffe;
};

int openPoseTutorialPose1()
{
    op::log("OpenPose Library Tutorial - Example 1.", op::Priority::High);
    // ------------------------- INITIALIZATION -------------------------
    // Step 1 - Set logging level
        // - 0 will output all the logging messages
        // - 255 will output nothing
    op::check(0 <= FLAGS_logging_level && FLAGS_logging_level <= 255, "Wrong logging_level value.",
              __LINE__, __FUNCTION__, __FILE__);
    op::ConfigureLog::setPriorityThreshold((op::Priority)FLAGS_logging_level);
    op::log("", op::Priority::Low, __LINE__, __FUNCTION__, __FILE__);
    // Step 2 - Read Google flags (user defined configuration)
    // outputSize
    const auto outputSize = op::flagsToPoint(FLAGS_output_resolution, "-1x-1");
    // netInputSize
    const auto netInputSize = op::flagsToPoint(FLAGS_net_resolution, "-1x368");
    // poseModel
    const auto poseModel = op::flagsToPoseModel(FLAGS_model_pose);
    // Check no contradictory flags enabled
    if (FLAGS_alpha_pose < 0. || FLAGS_alpha_pose > 1.)
        op::error("Alpha value for blending must be in the range [0,1].", __LINE__, __FUNCTION__, __FILE__);
    if (FLAGS_scale_gap <= 0. && FLAGS_scale_number > 1)
        op::error("Incompatible flag configuration: scale_gap must be greater than 0 or scale_number = 1.",
                  __LINE__, __FUNCTION__, __FILE__);
    // Enabling Google Logging
    const bool enableGoogleLogging = true;
    // Logging
    op::log("", op::Priority::Low, __LINE__, __FUNCTION__, __FILE__);
    // Step 3 - Initialize all required classes
    op::ScaleAndSizeExtractor scaleAndSizeExtractor(netInputSize, outputSize, FLAGS_scale_number, FLAGS_scale_gap);
    op::CvMatToOpInput cvMatToOpInput;
    op::CvMatToOpOutput cvMatToOpOutput;
    op::PoseExtractorCaffe poseExtractorCaffe{poseModel, FLAGS_model_folder,
                                              FLAGS_num_gpu_start, {}, op::ScaleMode::ZeroToOne, enableGoogleLogging};
    op::PoseCpuRenderer poseRenderer{poseModel, (float)FLAGS_render_threshold, !FLAGS_disable_blending,
                                     (float)FLAGS_alpha_pose};
    op::OpOutputToCvMat opOutputToCvMat;
    op::FrameDisplayer frameDisplayer{"OpenPose Tutorial - Example 1", outputSize};
    // Step 4 - Initialize resources on desired thread (in this case single thread, i.e. we init resources here)
    poseExtractorCaffe.initializationOnThread();
    poseRenderer.initializationOnThread();

    // ------------------------- POSE ESTIMATION AND RENDERING -------------------------
    // Step 1 - Read and load image, error if empty (possibly wrong path)
    // Alternative: cv::imread(FLAGS_image_path, CV_LOAD_IMAGE_COLOR);
    cv::Mat inputImage = op::loadImage(FLAGS_image_path, CV_LOAD_IMAGE_COLOR);
    if(inputImage.empty())
        op::error("Could not open or find the image: " + FLAGS_image_path, __LINE__, __FUNCTION__, __FILE__);
    const op::Point<int> imageSize{inputImage.cols, inputImage.rows};
    // Step 2 - Get desired scale sizes
    std::vector<double> scaleInputToNetInputs;
    std::vector<op::Point<int>> netInputSizes;
    double scaleInputToOutput;
    op::Point<int> outputResolution;
    std::tie(scaleInputToNetInputs, netInputSizes, scaleInputToOutput, outputResolution)
        = scaleAndSizeExtractor.extract(imageSize);
    // Step 3 - Format input image to OpenPose input and output formats
    const auto netInputArray = cvMatToOpInput.createArray(inputImage, scaleInputToNetInputs, netInputSizes);
    auto outputArray = cvMatToOpOutput.createArray(inputImage, scaleInputToOutput, outputResolution);
    // Step 4 - Estimate poseKeypoints
    poseExtractorCaffe.forwardPass(netInputArray, imageSize, scaleInputToNetInputs);
    const auto poseKeypoints = poseExtractorCaffe.getPoseKeypoints();

    const auto numberPeopleDetected = poseKeypoints.getSize(0);
    const auto numberBodyParts = poseKeypoints.getSize(1);
    // Easy version

    for( int person = 0 ; person < numberPeopleDetected ; person++)
    {
    for( int part = 0 ; part < numberBodyParts ; part++)
    {
        const auto x = poseKeypoints[{person, part, 0}];
        const auto y = poseKeypoints[{person, part, 1}];
        const auto score = poseKeypoints[{person, part, 2}];
        std::cout << "person " << person << " part " << part << " x : " << x << " y : " << y << " score : " << score << std::endl;
    }
    }
    // Step 5 - Render poseKeypoints
    poseRenderer.renderPose(outputArray, poseKeypoints, scaleInputToOutput);
    // Step 6 - OpenPose output format to cv::Mat
    auto outputImage = opOutputToCvMat.formatToCvMat(outputArray);

    // ------------------------- SHOWING RESULT AND CLOSING -------------------------
    // Step 1 - Show results
    frameDisplayer.displayFrame(outputImage, 0); // Alternative: cv::imshow(outputImage) + cv::waitKey(0)
    // Step 2 - Logging information message
    op::log("Example 1 successfully finished.", op::Priority::High);
    // Return successful message
    return 0;
}


#include <zmq.hpp>
#include <string>
#include <iostream>
#ifndef _WIN32
#include <unistd.h>
#else
#include <windows.h>

#define sleep(n)    Sleep(n)
#endif

static std::string
s_recv (zmq::socket_t & socket) {

    zmq::message_t message;
    socket.recv(&message);

    return std::string(static_cast<char*>(message.data()), message.size());
}

static bool
s_send (zmq::socket_t & socket, const std::string & string) {

    zmq::message_t message(string.size());
    memcpy(message.data(), string.data(), string.size());

    bool rc = socket.send(message);
    return (rc);
}

//  Sends string as 0MQ string, as multipart non-terminal
static bool
s_sendmore (zmq::socket_t & socket, const std::string & string) {

    zmq::message_t message(string.size());
    memcpy(message.data(), string.data(), string.size());

    bool rc = socket.send(message, ZMQ_SNDMORE);
    return (rc);
}

int main2 () {
    //  Prepare our context and socket
    zmq::context_t context (1);
    zmq::socket_t socket (context, ZMQ_ROUTER);
    socket.bind ("tcp://*:5555");

    PoseServer ps;

    while (true) {
        zmq::message_t request;

        //  Wait for next request from client
        std::string identity = s_recv(socket);

        std::string del = s_recv(socket);     //  Envelope delimiter
        std::string rpl = s_recv(socket);     //  Response from worker



        //std::string rpl = std::string(static_cast<char*>(request.data()), request.size());

        std::cout << "Received " << identity << " ---- "<< del <<" ---- "<< "imagedata"<< std::endl;
        s_sendmore(socket, identity);
        //s_sendmore(socket, "");

        //Decoding image

        std::vector<char> data;//(request.data(), request.data() + request.size());
        cv::Mat imgbuf(1, rpl.size(), CV_8UC1, (void*)(rpl.c_str()));
        cv::Mat inputImage = cv::imdecode(imgbuf,CV_LOAD_IMAGE_COLOR);
        //  Do some 'work'
        std::ostringstream os;
        ps.computePoseFromImage(inputImage,os);
        std::string resp = os.str();

        //  Send reply back to client
        s_send(socket,resp);
    }
    return 0;
}



int main(int argc, char *argv[])
{
    main2();
    // Parsing command line flags
    gflags::ParseCommandLineFlags(&argc, &argv, true);


    // Running openPoseTutorialPose1
    return 0;
}





