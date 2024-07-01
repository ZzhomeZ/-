from funasr import AutoModel
from flask import Flask, request
import json

# 采样率
fs = 44100
# 音频录制时长
duration = 10
md = r'models\speech_seaco_paraformer_large_asr_nat-zh-cn-16k-common-vocab8404-pytorch'
vm = r'models\speech_fsmn_vad_zh-cn-16k-common-pytorch'
pm = r'models\punc_ct-transformer_zh-cn-common-vocab272727-pytorch'
slist = []

# # 开始录音
# rec = sd.rec(int(duration*fs),samplerate=fs,channels=2)
# print('在这10秒内,请对麦克风说话：')
# sd.wait()
# sf.write(r'temp/temp.wav',rec,fs)
#
# 导入模型
model = AutoModel(model=md,
                  vad_model = vm,
                  punc_model = pm)
mode = ''

# # 模型推理
# result = model.generate(input = r'temp/temp.wav', batchi_size_s = 300)
# print(result[0]['text'])
# result = result[0]['text']

def stop2(l):
    global slist
    if '电容' in l:
        slist.append('电容')
    if '电阻' in l:
        slist.append('电阻')
    if 'LED' in l:
        slist.append('LED')
    if '芯片' in l:
        slist.append('芯片')
    if '数码管' in l:
        slist.append('数码管')
    return slist


def yy(l):
    global mode,slist
    slist.clear()
    if '实时' in l:
        mode = '实时计算'
    elif '累计' in l:
        mode = '累计计数'
    elif '实时累计' in l:
        mode = ''
    else:
        mode = ''

    if mode != '':
        if mode == '实时计算':
            stop2(l)
        else:
            stop2(l)

    # print('mode:{0},电子元器件名称列表：{1}'.format(mode, slist))
    return mode,slist



# yy(result)

app =Flask(__name__)

@app.route('/get_voice',methods= ['POST'])
def test():
    response = {'code':0, 'mess':'成功', 'data':''}
    result = request.files['sound']
    result.save(r'cloud\temp2.wav')
    a = model.generate(input = r'cloud\temp2.wav', batch_size_s = 300)
    response['data'] = a[0]['text']
    yy(a[0]['text'])
    response['result'] = 'mode:{0},电子元器件名称列表：{1}'.format(mode, slist)
    return json.dumps(response,ensure_ascii=False)

if __name__ == '__main__':
    app.config['JSON_AS_ASCII'] = False
    app.run(host='0.0.0.0',port=5000)




