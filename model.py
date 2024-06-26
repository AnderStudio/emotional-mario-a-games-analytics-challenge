# -*- coding: utf-8 -*-
"""model.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1sN2lpxGZEWL1yMEuf7lk8-RZJFpa8kuo

###Image size : 240, 256

# Library and Package

# New Section
"""
'''
#install Pytesseract 
!sudo apt install tesseract-ocr
!pip install pytesseract
'''

#image
import cv2
#get file
import os
from os import listdir
from os.path import isfile, join
import numpy as np
import pandas as pd
import warnings
from pathlib import Path
# text 
import pytesseract
import shutil
from PIL import Image
import csv
import re
#pip install Pillow==9.0.0
import sys
import json
import argparse
import random
from scipy.signal import argrelextrema
print("Import Successfully!")

argument_parser = argparse.ArgumentParser(description="A script used to replay the game session.")

# participants-path = .../toadstool/participants
# groundtruth-path = .../GroundTruth
argument_parser.add_argument("-p", "--participants-path", type=str, default=None)
argument_parser.add_argument("-i", "--participant-idx", type=str, default=None)
argument_parser.add_argument("-g", "--groundtruth-path", type=str, default=None)
argument_parser.add_argument("-o", "--output-path", type=str, default= None)

#functions

def is_empty_or_blank(msg):
  return re.search("^\s*$", msg)
# get grayscale image
def get_grayscale(image):
  return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#thresholding
def thresholding(image):
  return cv2.threshold(src=gray, thresh=0, maxval=255, type=cv2.THRESH_OTSU + cv2.THRESH_BINARY_INV)[1]


if __name__ == "__main__":
  #parser
  args = argument_parser.parse_args()
  participants_path = args.participants_path
  participant_idx = args.participant_idx
  groundtruth_path = args.groundtruth_path
  output_path = args.output_path
  
  #file path
  #path = f'{participants_path}/participant_{participant_idx}/participant_{participant_idx}_game_frame'
  
  path = f'./{participant_idx}/{participant_idx}_game_frame'
  
  #divide frames
  frames = {}
  fid = 0
  id = 0
  files = os.listdir(path)
  for i in range(len(files)):
    files[i] = files[i].replace("game_", "")
  files.sort(key=lambda x:int(x.split('.')[0]))
  for id in range(len(files)):
    if id%30 == 0:
      tmp = "game_" + files[id]
      frames[fid]= join(path, tmp)
      fid = fid+1
  print("Sample Successfully!")
  """ text detectation"""
  score = []
  world_1 = []
  world_2 = []
  time = []
  for i in frames:
    path = frames[i]
    print(i)
    print(path)
    img = cv2.imread(path)
    #score
    crop_img = img[23:32, 20:80]
    gray = get_grayscale(crop_img)
    thr = thresholding(gray)
    config='--psm 11 --oem 3 -c tessedit_char_whitelist=0123456789 tessedit_char_blacklist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    data = pytesseract.image_to_string(thr, config = config)
    score.append(data)
    #world_1
    crop_img = img[23:32, 152:160]
    gray = get_grayscale(crop_img)
    thr = thresholding(gray)
    config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789 tessedit_char_blacklist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    data = pytesseract.image_to_string(thr, config = config)
    world_1.append(data)
    #world_2
    crop_img = img[23:32, 168:176]
    gray = get_grayscale(crop_img)
    thr = thresholding(gray)
    config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789 tessedit_char_blacklist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    data = pytesseract.image_to_string(thr, config = config)
    world_2.append(data)
    #time
    crop_img = img[23:33, 205:235]#num:23:33, 20:240/world:13:23, 20:240
    gray = get_grayscale(crop_img)
    thr = thresholding(gray)
    config='--psm 11 --oem 3 -c tessedit_char_whitelist=0123456789 tessedit_char_blacklist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    data = pytesseract.image_to_string(thr, config = config)
    time.append(data)
  print("Text Detectation Successfully!")
  #turn score into int_score
  score_int = []
  for i in range(len(score)):
    if is_empty_or_blank(score[i]):
        score[i] = score[i-1]
    score[i] = re.sub("[^0-9]", "", score[i])
    if score[i].isdigit():
      score_int.append(int(score[i])) 
  print("score_int", type(score_int))
  print(score_int)

  #Create new_world
  pre = ''
  new_world = []
  for i in range(len(world_1)):
    #check if empty string
    if is_empty_or_blank(world_1[i]):
        world_1[i] = world_1[i-1]
    if is_empty_or_blank(world_1[i]):
        world_2[i] = world_2[i-1]
    world_1[i] = re.sub("[^0-9]", "", world_1[i])
    world_2[i] = re.sub("[^0-9]", "", world_2[i])
    s = world_1[i] + '-' + world_2[i]
    if world_1[i] == '':
      s = pre
    elif world_2[i] == '':
      s = pre
    pre = s
    new_world.append(s)

  print("new_world", type(new_world))
  print(new_world)

  #time
  time_int = []
  for i in range(len(time)):
    if type(time[i]) != str:
      time[i] = str(time[i])
    if is_empty_or_blank(time[i]):
        time[i] = time[i-1]
  for i in range(len(time)):
    time[i] = re.sub("[^0-9]", "", time[i])
    if is_empty_or_blank(time[i]):
        time[i] = time[i-1]
    time_int.append(int(time[i]))
  for i in range(len(time_int)-1):
    if time_int[i]-time_int[i+1] < 3:
      continue
    elif time_int[i]>500:
      time_int[i] = time_int[i-1]-1
    elif time_int[i]-time_int[i+1]<0:
      if time_int[i]%100 == 0:
        continue
      else:
        time_int[i+1] = int((time_int[i]-1))
    else:
      time_int[i+1] = int((time_int[i]-1))
  print("time", type(time_int))
  print(time_int)

  # turn frames[i] into frame numbers
  frames_num = {}
  p = f'./{participant_idx}/{participant_idx}_game_frame/game_'
  for i in frames:
    t = frames[i].replace(p, '')
    frames_num[i] = t.replace('.png', '')
    frames_num[i] = int(frames_num[i])
  print("frames_num", type(frames_num))
  print(frames_num)

  ans = {}

  id = 0
  c = 0 #count number of events
  current_world = new_world[0]
  current_status = 0 #1: mushroom
  level_time = time_int[0]

  for i in range(len(score_int)):  
    if i+1 >= len(score_int):
      #print(i, 'stop')
      break
    elif score_int[i+1] == 0: 
      if new_world[i+1] != current_world:#flag reach and new stage
          ans[id] = ['flag_reached',frames_num[i+1]-1 ]
          id = id + 1
          ans[id] = ['new_stage',frames_num[i+1] ]
          id = id + 1
          c = c + 2
          current_world = new_world[i+1]
          level_time = time_int[i]

      elif time_int[i] < time_int[i+1]:
        #print(i, time_int[i+1], time_int[i])
        ans[id] = ['life_lost',frames_num[i+1]]#life lost
        id = id + 1
        c = c + 1
    
    #status up
    elif score_int[i+1]-score_int[i] == 1000:
        ans[id] = ['status_up',frames_num[i] ]
        id = id + 1
        c = c + 1
        current_status = 1
    else:
      current_world = new_world[i]

  d={'event':[], 'frame_number':[]}
  for i in ans:
    d['event'].append(ans[i][1])
    d['frame_number'].append(ans[i][0])

  df = pd.DataFrame(d)
  df.to_csv(output_path, index=False, header=False)
print("100%: Output Successfully!")
