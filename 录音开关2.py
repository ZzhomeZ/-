import time
import sounddevice as sd
import soundfile as sf
import requests
# from funasr import AutoModel
# import os
import two
import multiprocessing as mp
from multiprocessing import Process, Queue
import cv2

# 网页
url = 'http://10.42.67.44:5000/get_voice'
# 采样率
fs = 44100
# 音频录制时长
duration = 10


# 废弃方案，让云端去整
# md = r'models\speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch'
# vm = r'models\speech_fsmn_vad_zh-cn-16k-common-pytorch'
# pm = r'models\punc_ct-transformer_zh-cn-common-vocab272727-pytorch'
# # 导入模型
# model = AutoModel(model=md,
#                   vad_model=vm,
#                   punc_model=pm)

def panduan1(pl):  # 判断类型,用于检测所说内容
    op = []
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


def record(queue,a):
    while True:
        # 开始录音
        a['close_window'] = False
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


def openvideo(queue,a):
    while True:
        read1 = queue.get()

        if 'result' in read1:
            text1 = read1['result']
            print(text1)
            if '实时计算' in text1:
                two.realtime_count(panduan1(text1))
            elif '累计计数' in text1:
                two.accu_count(panduan1(text1))
            else:
                print('没有输入模式')
            print('')
        else:
            print('没有相应')
            print('')


def closedoor(a):
    while True:
        if a['close_window']:
            cv2.destroyAllWindows()

        if a['end']:
            cv2.destroyAllWindows()
            break


def main():
    mp.set_start_method(method='spawn')
    queue = Queue()
    m = mp.Manager()    #创建共享字典
    a = m.dict()
    a['close_window'] = False  # 是否关闭当前计数窗口
    a['end'] = False  # 是否终止整个程序
    A1 = mp.Process(target=record, args=(queue,a,))
    A2 = mp.Process(target=openvideo, args=(queue,a,))
    A3 = mp.Process(target=closedoor,args=(a,))

    A1.start()
    A2.start()
    A3.start()

    A1.join()
    A2.join()
    A3.start()
    print('结束运行')


if __name__ == '__main__':
    main()
