|**********************************************************************;
* Project           : ONR Transom Elevations
*
* Program name      : transom-elevation
*
* Author            : Alex Koziol (alekoz47@gmail.com)
*
* Date created      : 07152020
*
* Purpose           : find and interpret wave elevations from model test videos
|**********************************************************************;



Below are brief instructions on how to run the various script files.
All files are hardcoded for T1, T4, and T5, but could be easily updated.

- If you wish to run on all videos -
1. Ensure the /data directory is empty
2. Ensure the /videos directory is populated with appropriate videos in each folder
3. Run analyze_video.py
4. Run fourier.py
5. Run ventilation.py

- If you wish to run on one or more videos, but not all -
1. Ensure the /data directory does not contain data for the desired run
2. Ensure the desired video is located in the /videos directory
3. Change the video filepath in analyze_video_singular.py and run
4. Run fourier.py (you may need to change the filepaths)
5. Run ventilation.py (you may need to change the filepaths)



Below are brief descriptions of project organization and files.

+-- data
|	+-- 2016-03-11, T4 (contains raw elevation CSV output for each run)
|	+-- 2016-06-27_T1 (contains raw elevation CSV output for each run)
|	+-- 2016-06-29_T5 (contains raw elevation CSV output for each run)
|	+-- fft (contains FN, Amplitude, Frequency CSV output for each hull)
|	+-- testing (for testing elevations output)
|	+-- ventilation (contains FN, ventilation at each buttock CSV output for each hull)
+-- images (image dump, used while running analysis)
|	+-- testing (test_mask.py outputs images with contour overlays here)
+-- transom-elevation (contains script files)
|	+-- analyze_video.py (for finding elevations from videos)
|	+-- analyze_video_singular.py (for finding elevations from a video)
|	+-- elevations_utils.py (utility functions for video analysis - includes all elevations logic)
|	+-- fourier.py (for finding amplitude and frequency)
|	+-- test_mask.py (for testing masks on various videos, outputs to images/testing)
|	+-- ventilation.py (for finding ventilation factor)
+-- videos
|	+-- 2016-03-11, T4 (contains all T4 videos)
|	+-- 2016-06-27_T1 (contains all T1 videos)
|	+-- 2016-06-29_T5 (contains all T5 videos)
+-- LICENSE
+-- README.txt
