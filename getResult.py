import csv
import os
headers = ['image_id','bbox','category_id','confidence']
classList = ['crazing','inclusion','pitted_surface','scratches','patches','rolled-in_scale']
rows = []

rootdir = './dataset/steel_voc/infer_output'
list = os.listdir(rootdir) #列出文件夹下所有的目录与文件
for i in range(0,len(list)):
       path = os.path.join(rootdir,list[i])
       if os.path.isfile(path) and path.endswith('txt'):
           txtFile = open(path)
           print(path)
           result = txtFile.readlines()
           for r in result:
               ls = r.split(' ')
               Cls = ls[0]
               sco = float(ls[1])
               xmin = float(ls[2])
               ymin = float(ls[3])
               w = float(ls[4])
               h = float(ls[5])
               xmax = xmin+w
               ymax = ymin+h
               clsID = classList.index(Cls)
               imgID = list[i][:-4]
               row = [imgID,[xmin,ymin,xmax,ymax],clsID,sco]
               rows.append(row)
with open('submission.csv','w')as f:
    f_csv = csv.writer(f)
    f_csv.writerow(headers)
    f_csv.writerows(rows)
import pandas as pd
datafile = pd.read_csv('/home/aistudio/work/PaddleDetection/submission.csv')
# 按照列值排序
data = datafile.sort_values(by="image_id", ascending=True)
data.to_csv('submission_final.csv', mode='a+', index=False)