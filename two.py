from ultralytics import YOLO
import cv2
from collections import Counter
import numpy as np

# 基础数据
source = 0
model_path = 'models/best.pt'
# classes = [0,1,2,3,4]

model = YOLO(model_path)

# 颜色池
color_list = [(255, 0, 0),
              (0, 255, 0),
              (0, 0, 255),
              (255, 255, 0),
              (0, 255, 255),
              (255, 0, 255)]


# 实时计数
def realtime_count(classes):
    n_result = {'C':0,'R':0,'LED':0,'A':0,'B':0}
    results = model.predict(source=source, classes=classes, stream=True, show=False)
    # result = result1[0]
    for result in results:
        cls_names = result.names
        img = result.orig_img
        boxes = result.boxes
        data = boxes.data
        data = data.cpu().numpy()
        k = show_result(data, img, cls_names)

        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            break
        else:
            for i in classes:
                n = len(data[data[:, -1] == i])
                n_result[cls_names[i]] = n

        print('计算结果',n_result)

# 显示
def show_result(data, img, cls_names):
    i1 = 0
    while i1 < len(data):  # 画图
        conf = data[i1, -2]
        cl1 = data[i1, -1]
        x1, y1, x2, y2 = data[i1, :4]
        cls_index = data[i1, -1]
        name = cls_names[cls_index]
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color=color_list[int(cl1)], thickness=2)
        cv2.putText(img, name + ' ' + str(conf)[:4], (int(x1), int(y1)), 2, 1, color_list[int(cl1)], 2)
        i1 += 1
    cv2.imshow('show', img)

#按a键累计计数
def accu_count(classes):
    n_result = {'C': 0, 'R': 0, 'LED': 0, 'A': 0, 'B': 0}
    nl = Counter(n_result)
    results = model.predict(source=source, classes=classes, stream=True, show=False)

    for result in results:
        cls_names = result.names
        img = result.orig_img
        boxes = result.boxes
        data = boxes.data
        data = data.cpu().numpy()
        k = show_result(data, img, cls_names)

        key = cv2.waitKey(1)
        if key == ord('q'):
            cv2.destroyAllWindows()
            break
        elif key == ord('a'):
            for i in classes:
                n = len(data[data[:, -1] == i])
                n_result[cls_names[i]] = n
            print('当前数量', n_result)
            nl.update(n_result)
            print('总数:', nl)


