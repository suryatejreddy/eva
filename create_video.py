import cv2
import os
import numpy as np
from src.models.server.response import Response
from src.models.storage.batch import Batch
from moviepy.editor import *

def create_video_from_frames(batch):
    image_folder = '.' # make sure to use your folder 
    video_name = 'mygeneratedvideo.mp4'
    
    #os.chdir("/home/vivian/eva-ui/public/videos") 
    print(batch.frames['FastRCNNObjectDetector(data)'][0])
    first_frame = np.array(batch.frames['data'][0])
    height, width, layers = first_frame.shape

    video = cv2.VideoWriter(video_name, cv2.VideoWriter_fourcc(*'mp4v'), 1, (width, height))  
  
    # Appending the images to the video one by one 
    for frame in batch.frames['data']:  
        image = cv2.UMat(np.array(frame, dtype=np.uint8))
        video.write(image)  
      
    # Deallocating memories taken for window creation 
    cv2.destroyAllWindows()  
    video.release()  # releasing the video generated 

    edit_video(video_name)

    return video_name

def edit_video(name):
    #path = "/home/vivian/eva/" + name
    video = VideoFileClip(name).set_duration(5)
    video.write_videofile("/home/vivian/eva-ui/public/videos/my_new_generated_video.mp4", fps = 30)
    video.close()
