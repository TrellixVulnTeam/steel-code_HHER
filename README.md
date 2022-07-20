# 项目说明
**基于PaddleDetection开发**<br>
**学号**：Z127 **学生姓名**：连榕榕 **就读学校**福建农林大学 **专业**：软件工程<br>
删减了PaddleDetection的冗余代码文件，保留了核心训练以及推理等代码文件。
> 为了减少项目体积大小，output文件夹中只保存了提交测试精度最高的权重文件。
# 项目启动
## 前置工作
遵循以下步骤即可完成项目顺利启动
```
#解压项目代码文件
unzip work/steel-code.zip

#将数据集拷贝到work/steel-code/dataset/steel_voc文件夹下 执行压缩命令 这步可以不用做，压缩包里自带数据集
unzip data/data158746/steel_bug_detect.zip -d work/steel-code/dataset/steel_voc

#进入工作目录
cd work/steel-code/

#安装需要的依赖
pip install -r requirements.txt 
```
## 模型启动训练
```
#faster_rcnn系列启动训练脚本
python tools/train.py -c configs/faster_rcnn/faster_rcnn_swin_tiny_fpn_1x_voc.yml \
-o pretrain_weights=./output/faster_rcnn_swin_tiny_fpn_1x_voc/best \
--use_vdl=true --vdl_log_dir=/home/aistudio/vdl_dir/scalar --eval
```
## 模型推理
执行以下脚本文件，完成后会在dataset/steel_voc/infer_output文件夹下生成所有文件的推理结果，并在steel-code根目录下生成submission_final.csv（未经过排序）与submission_final.csv文件（经过排序），使用submission_final.csv进行提交分更高。
```
#训练完毕，执行推理并转换为比赛需要的格式文件
#在steel-code目录下执行推理脚本
python tools/infer.py -c  configs/faster_rcnn/faster_rcnn_swin_tiny_fpn_1x_voc.yml \
-o weights=./output/faster_rcnn_swin_tiny_fpn_1x_voc/best \
--infer_dir=./dataset/steel_voc/test/images/ \
--output_dir=./dataset/steel_voc/infer_output\
--draw_threshold=0.001 --save_txt=True

#完成后执行得到比赛提交结果文件的脚本
python getResult.py
```
# baseline改进思路
整体baseline改进主要从以下几个方面入手：
* 数据清洗
* 数据增强
* 模型选取及优化
* 训练参数搜索
* 提交测试参数优化<br>
baseline改进整体调优如下框架图所示
![](https://ai-studio-static-online.cdn.bcebos.com/55d3d2a25ca349dbb2a26f6b5b209caf29286d229c0749edbeaf67bb79c69a00)

# 模型实验

**数据清洗**：利用labelimg打开训练数据，发现许多图片存在漏标或者误标的情况，如下图所示：
![](https://ai-studio-static-online.cdn.bcebos.com/96d3c8cec3a3484cb5242af0beb0d0ff9b954c9b708447cfa7dd59c398f19e7a)
![](https://ai-studio-static-online.cdn.bcebos.com/f63977441c9a4be69090ca02e9cd1d4f73c7d4590c824106bca971928401e13d)
对训练集的所有图片重新进行标注，完成数据清洗工作。
之后，划分训练数据与验证数据为9：1
<br>

1. 
**数据增强**：搜索空间中的增强策略有：RandomDistort（随机亮度扰动）、RandomResizeCrop（随机裁剪）、RandomResize（多尺度训练）、Mixup（图片混合）
> 经过实验，最终确定的数据增强策略为：RandomResize、RandomResizeCrop、RandomResize、RandomFlip<br>
> 统计整体图片的均值与方差，得到结果为：mean: [0.5025944, 0.5025944, 0.5025944], std: [0.2113286, 0.2113286, 0.2113286]

**模型选取**：主要测试了cascade_rcnn系列、faster_rcnn系列模型、ppyolo系列模型


| 模型         | 主干网络             | mAP(0.5) | 提交测试 |
| ------------ | -------------------- | -------- | -------- |
| Cascade RCNN | ResNet-101           | 0.594    | 30.60617 |
| Faster RCNN  | SwinTransformer-tiny | 0.73     | 43.3316  |
| Faster RCNN  | ResNet-101           | 0.71     | 39.39505 |
| PP-YOLO      | ResNet-101           | 0.43     | 25.93512 |

**模型调优过程**：
经过模型的选取，最终确定以Faster-RCNN为本项目的检测算法，使用SwinTransformer作为主要特征提取网络。通过网上查阅资料，在项目中使用了如下两种对模型的调优策略。
* 加入特征金字塔FPN结构融合高低层信息，采用该结构动机：
> <br>1.可以将特征提取网络得到的高底层信息进行结合从而进一步增强特征表达的能力。<br>2.候选框产生和提取特征的位置分散到了特征金字塔的每一层，这样可以增加小目标的特征映射分辨率。
* Contextual ROI Pooling
> 将整张图片作为一个ROI，利用ROI Pooling提取全局的特征并与局部进行相加，再送入之后的分类以及回归操作。<br>
> 注：不过该trick使用在本项目中无效果提升。。。。至于为啥今后有时间继续探索。

**训练参数调优**：
* 优化器选取：对比了Momentum以及Adamw进行测试，确定训练策略为：前100个epoch使用AdamW进行训练（目的使得模型快速收敛到一个大致精度的区间），之后200个epoch使用Momentum进行进一步微调。
* 学习策略：使用余弦退火方式进行学习，初始学习率设置为0.001

**其余Trick**：
使用基于yolov2的锚框聚类算法初始化锚框
> Faster-RCNN系列得到的初始锚框：[112, 162]、[94, 517]、[425, 188]、[222, 400]、[488, 548] 
> 注：用在Faster-RCNN系列上精度并没有变化，故还是使用原来的初始锚框

**测试参数搜索**：
测试方面选取精度最高的faster_rcnn系列进行提交<br>

| 图片尺寸 | 测试nms阈值 | BBP-nms_threshold | score_threshold | draw_threshold | 最终得分 |
| -------- | ----------- | ----------------- | --------------- | -------------- | -------- |
| 640-640  | 0.5         | 0.5               | 0.005           | 0.005          | 43.09703 |
| 640-640  | 0.5         | 0.5               | 0.001           | 0.001          | 43.1501  |
| 640-640  | 0.7         | 0.5               | 0.001           | 0.001          | 43.63953 |
| 640-640  | 0.7         | 0.7               | 0.001           | 0.001          | 44.12362 |
| 608-608  | 0.7         | 0.7               | 0.001           | 0.001          | 43.62723 |
| 800-800  | 0.7         | 0.7               | 0.001           | 0.001          | 43.4153  |

# 项目总结
通过本次比赛，我收获到了许多，其中掌握了PaddleDetection开发套件的使用以及包括主流模型的学习等。
当然，由于比赛时间较短，未能对项目进行更进一步的优化，今后尝试的优化思路如下：
1. 尝试更多目标检测模型
2. 对Faster-RCNN检测框架做进一步改进
3. 采取模型融合的方案
