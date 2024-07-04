import time
import sounddevice as sd
import soundfile as sf
import requests
# from funasr import AutoModel
# import os
import multiprocessing as mp
from multiprocessing import Process, Queue
import cv2
from ultralytics import YOLO
from collections import Counter

# 特殊话语：结束、关闭窗口、电子元器件类别名称、累计/实时

# 网址(根据云端代码运行弹出的服务器码更改）
url = 'http://10.64.19.20:5000/get_voice'
# 采样率
fs = 44100
# 音频录制时长
duration = 10
# 基础数据
source = 0
# 模型路径
model_path = 'models/best.pt'
# 导入目标检测模型
model = YOLO(model_path)
# 颜色池
color_list = [(255, 0, 0),
              (0, 255, 0),
              (0, 0, 255),
              (255, 255, 0),
              (0, 255, 255),
              (255, 0, 255)]


def panduan1(pl):  # 判断类型,用于检测所说内容
    op = []  # 初始化列表
    if '电容' in pl:
        op.append(0)
    if '电阻' in pl:
        op.append(1)
    if 'LED' in pl:
        op.append(2)
    if '芯片' in pl:
        op.append(3)
    if '数码管' in pl:
        op.append(4)
    return op


def record(queue, a):
    while True:
        # 开始录音
        rec = sd.rec(int(duration * fs), samplerate=fs, channels=2)
        print('在这10秒内,请对麦克风说话：')
        sd.wait()
        sf.write(r'temp/temp.wav', rec, fs)
        upload = requests.post(url, files={'sound': open(r'temp/temp.wav', 'rb')})

        if upload.status_code == 200:
            ceshi = upload.json()
            if 'data' in ceshi and ceshi['data']:
                read1 = upload.json()
                result = read1['data']
                queue.put(read1)

                if result:
                    print(result)

                    if '结束' in result:
                        a['end'] = True
                        break
                    if '关闭窗口' in result:
                        a['close_window'] = True

                else:
                    print('没有识别到语音或结果为空')
            else:
                print('连接服务器失败')
        else:
            print('没有识别到语音或结果为空')


def openvideo(queue, a):
    while True:
        read1 = queue.get()
        if a['end']:
            break

        if 'result' in read1:
            text1 = read1['result']
            print(text1)
            if '实时计算' in text1:
                realtime_count(panduan1(text1), a=a)
            elif '累计计数' in text1:
                accu_count(panduan1(text1), a=a)
            else:
                print('没有输入模式')
            print('')
        else:
            print('没有相应')
            print('')
        cv2.destroyAllWindows()

# 主函数
def main():
    mp.set_start_method(method='spawn')
    queue = Queue()   # Queue的功能是将每个核或线程的运算结果放在队里中，等到每个线程或核运行完毕后再从队列中取出结果，继续加载运算。
    m = mp.Manager()  # 创建共享字典
    a = m.dict()
    a['close_window'] = False  # 是否关闭当前计数窗口
    a['end'] = False  # 是否终止整个程序
    a['ac'] = False  # 是否累加
    # 子程序编写
    A1 = mp.Process(target=record, args=(queue, a,))
    A2 = mp.Process(target=openvideo, args=(queue, a,))

    # 启动子程序
    A1.start()
    A2.start()

    # 主程序阻塞
    A1.join()
    A2.join()
    print('结束运行')


















# 还有摄像头关闭程序没做
# 再次定义一个函数来控制是否累加一次









# 取消了对two文件的引用，选择直接复制在此进行改动
# 功能一 实时计数
def realtime_count(classes,a):
    cv2.destroyAllWindows()
    n_result = {'C': 0, 'R': 0, 'LED': 0, 'A': 0, 'B': 0}  # 初始化数量
    results = model.predict(source=source, classes=classes, stream=True, show=False)  # 获取推理结果
    # result = result1[0]
    for result in results:
        cls_names = result.names  # 获取类别标签字典
        img = result.orig_img  # 获取帧图像
        boxes = result.boxes
        data = boxes.data
        data = data.cpu().numpy()  # 获取目标对象的边界框、类别名称和置信度等信息
        show_result(data, img, cls_names)

        if a['close_window'] or a['end']:
            cv2.destroyAllWindows()
            a['close_window'] = False
            break
        else:
            for i in classes:
                n = len(data[data[:, -1] == i])
                n_result[cls_names[i]] = n

        print('计算结果', n_result)
    cv2.destroyAllWindows()  # 加一层保险


# 显示
def show_result(data, img, cls_names):
    i1 = 0
    while i1 < len(data):  # 画图
        conf = data[i1, -2]
        cl1 = data[i1, -1]
        x1, y1, x2, y2 = data[i1, :4]
        cls_index = data[i1, -1]
        name = cls_names[cls_index]
        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color=color_list[int(cl1)], thickness=2)  # 绘画边框
        cv2.putText(img, name + ' ' + str(conf)[:4], (int(x1), int(y1)), 2, 1, color_list[int(cl1)], 2)
        i1 += 1
    cv2.imshow('show', img)


# 功能二 按a键累计计数
def accu_count(classes,a):
    cv2.destroyAllWindows()
    n_result = {'C': 0, 'R': 0, 'LED': 0, 'A': 0, 'B': 0}  #初始化数量
    nl = Counter(n_result)   # 对访问的对象的频率进行计数
    results = model.predict(source=source, classes=classes, stream=True, show=False)

    for result in results:
        cls_names = result.names  # 获取类别标签字典
        img = result.orig_img  # 获取帧图像
        boxes = result.boxes
        data = boxes.data
        data = data.cpu().numpy()   # 获取目标对象的边界框、类别名称和置信度等信息
        show_result(data, img, cls_names)

        if a['close_window'] or a['end']:
            cv2.destroyAllWindows()
            a['close_window'] = False
            break
        elif a['ac']:
            for i in classes:
                n = len(data[data[:, -1] == i])
                n_result[cls_names[i]] = n
            print('当前数量', n_result)
            nl.update(n_result)
            print('总数:', nl)
            a['ac'] = False  # 还原累加状态
    cv2.destroyAllWindows()  # 加层保险


if __name__ == '__main__':
    main()
