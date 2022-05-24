# Visitor-tracker-pi
Code for DTAP 2022 visitor tracker Raspberry Pi

# Running
 - Download the repo and navigate to the downloaded directory
 - Run python3 src/main.py to start the program

# Installation
Base requirements:
 - Python 3.8+
 - Raspberry Pi 4B (or better) with camera module
 - Linux (Debian Legacy version, i.e., Buster)
 - Intel Neural Compute Stick 2 (or similar)

 Installation guides are taken from here: https://www.qengineering.eu/install-opencv-lite-on-raspberry-pi.html

Instal requirements on the Pi:
    # check for updates
    $ sudo apt-get update
    $ sudo apt-get upgrade
    # general tools (35.8 MB)
    $ sudo apt-get install build-essential cmake git pkg-config
    # if you want to get OpenCV working in python or python3 (208 MB)
    $ sudo apt-get install python3-dev python3-numpy
    # The latest Debian 11, Bullseye don't support python2 full
    # don't try to install if you're having a Raspberry Bullseye OS
    $ sudo apt-get install python-dev  python-numpy
    # image formats (0.9 MB)
    $ sudo apt-get install libjpeg-dev libpng-dev
    # video formats (32.1 MB)
    $ sudo apt-get install libavcodec-dev libavformat-dev
    $ sudo apt-get install libswscale-dev libdc1394-22-dev
    # video back engine (0.6 MB)
    $ sudo apt-get install libv4l-dev v4l-utils
    # the GTK+2 GUI (175 MB)
    $ sudo apt-get install libgtk2.0-dev libcanberra-gtk* libgtk-3-dev
    # parallel framework (2.7 MB)
    # don't install if your having a 1 core CPU (like RPi zero)
    $ sudo apt-get install libtbb2 libtbb-dev

Download OpenCV:
    # download OpenCV (you get always the latest version)
    $ cd ~
    $ git clone --depth=1 https://github.com/opencv/opencv.git
    $ cd opencv
    $ mkdir build
    $ cd build

Configure the build
    $ cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D ENABLE_NEON=ON \
    -D ENABLE_VFPV3=ON \
    -D BUILD_ZLIB=ON \
    -D BUILD_OPENMP=ON \
    -D BUILD_TIFF=OFF \
    -D BUILD_OPENJPEG=OFF \
    -D BUILD_JASPER=OFF \
    -D BUILD_OPENEXR=OFF \
    -D BUILD_WEBP=OFF \
    -D BUILD_TBB=ON \
    -D BUILD_IPP_IW=OFF \
    -D BUILD_ITT=OFF \
    -D WITH_OPENMP=ON \
    -D WITH_OPENCL=OFF \
    -D WITH_AVFOUNDATION=OFF \
    -D WITH_CAP_IOS=OFF \
    -D WITH_CAROTENE=OFF \
    -D WITH_CPUFEATURES=OFF \
    -D WITH_EIGEN=OFF \
    -D WITH_GSTREAMER=ON \
    -D WITH_GTK=ON \
    -D WITH_IPP=OFF \
    -D WITH_HALIDE=OFF \
    -D WITH_VULKAN=OFF \
    -D WITH_INF_ENGINE=OFF \
    -D WITH_NGRAPH=OFF \
    -D WITH_JASPER=OFF \
    -D WITH_OPENJPEG=OFF \
    -D WITH_WEBP=OFF \
    -D WITH_OPENEXR=OFF \
    -D WITH_TIFF=OFF \
    -D WITH_OPENVX=OFF \
    -D WITH_GDCM=OFF \
    -D WITH_TBB=ON \
    -D WITH_HPX=OFF \
    -D WITH_EIGEN=OFF \
    -D WITH_V4L=ON \
    -D WITH_LIBV4L=ON \
    -D WITH_VTK=OFF \
    -D WITH_QT=OFF \
    -D BUILD_opencv_python3=ON \
    -D BUILD_opencv_java=OFF \
    -D BUILD_opencv_gapi=OFF \
    -D BUILD_opencv_objc=OFF \
    -D BUILD_opencv_js=OFF \
    -D BUILD_opencv_ts=OFF \
    -D BUILD_opencv_dnn=OFF \
    -D BUILD_opencv_calib3d=OFF \
    -D BUILD_opencv_objdetect=OFF \
    -D BUILD_opencv_stitching=OFF \
    -D BUILD_opencv_ml=OFF \
    -D BUILD_opencv_world=OFF \
    -D BUILD_EXAMPLES=OFF \
    -D OPENCV_ENABLE_NONFREE=OFF \
    -D OPENCV_GENERATE_PKGCONFIG=ON \
    -D INSTALL_C_EXAMPLES=OFF \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D PYTHON3_PACKAGES_PATH=/usr/lib/python3/dist-package ..

Compile the code
    $ make -j$(nproc)

Install compiled files:
    $ sudo make install
    $ sudo ldconfig
    $ sudo apt-get update
