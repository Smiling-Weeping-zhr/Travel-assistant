import json
import random
import argparse
import yaml
import re
import copy

from tqdm import tqdm

with open('config.yml', 'r', encoding='utf-8') as f:
    configs = yaml.load(f.read(), Loader=yaml.FullLoader)

def processing(prompt):
    conversation = {
        'system': '现在你是盐城市旅游小助手小优，我想了解盐城市生态养生旅游相关内容，请你用专业的知识帮我解决。',
        'input': '', 'output': ''}
    conversations = {'conversation': []}
    # temp = {'system':'现在你是一个心理专家，我有一些心理问题，请你用专业的知识帮我解决。', 'input':'', 'output':''}
    # 划分对话形式
    dialogue = re.split('导游：|游客：', prompt)
    # 对话前的数据处理
    if dialogue[0] == '':
        dialogue.pop(0)
    # 一次对话
    conversation['input'] = dialogue[0]
    conversation['output'] = dialogue[1]
    conversations['conversation'].append(conversation)

    conversation1 = {'input': '', 'output': ''}
    for ind, item in enumerate(dialogue):
        if ind == 0 or ind == 1:
            continue

        if (ind + 1) % 2 == 1:
            conversation1['input'] = dialogue[ind]
        else:
            conversation1['output'] = dialogue[ind]
        if (ind + 1) % 2 == 0 or ind + 1 == len(dialogue):
            # 浅赋值只会是同一个变量，必须要copy.deepcopy
            # 若conversations['conversation'].append(conversation)后面改的话，~s里面的conversation也会改动
            # 就会变成n个一样的数据（这是我们不想看到的）
            temp = copy.deepcopy(conversation1)
            conversations['conversation'].append(temp)

    return conversations

def qwen_api(data, emo):
    import dashscope
    from http import HTTPStatus

    area = [
        '中华麋鹿园',
        '盐城大纵湖旅游景区',
        '盐城市新四军纪念馆',
        '盐城市射阳县息心寺',
        '阜宁金沙湖旅游区',
        '东台西溪旅游文化景区',
        '大丰上海知青纪念馆',
        '盐城海盐历史文化风景区',
        '阜宁庙湾古城景区',
        '中国海盐博物馆',
        '水街',
        '荷兰花海',
        '新四军纪念馆',
        '戈公振故居',
        '黄海森林公园',
        '盐城市科技馆',
        '江苏盐城湿地珍禽国家级自然保护区',
        '东台董永七仙女文化园',
        '朦胧塔',
        '海春轩塔',
        '江苏省盐城市紫云山',
        '中华水浒园',
        '盐城世纪公园',
        '江苏省盐城市华都森林公园',
        '江苏省盐城市泰山寺'
    ]

    prompt = f'''你是盐城市旅游小助手小优，请你构造一些符合实际情况的对江苏省盐城市旅游景点感兴趣的游客和江苏省盐城市导游的一段对话记录。要求游客的问题是对于{area}景点的询问，导游的回复尽可能包含盐城市的旅游景点及相关知识，并且能够一步步诱导游客说出自己的问题进而提供具体旅游可行方案,包括交通路线及当地特色美食。注意，构造的数据必须以导游的陈述为结束语，请只返回完整的对话内容。请以如下格式返回生成的数据：
        游客：游客对旅游景点的咨询或陈述 
        导游：导游对旅游景点的推荐和建议
        '''
    # prompt =
    prompt.format(random.sample(area, k=random.randint(2, 5)))
    dashscope.api_key = configs['dashscope_api_key']
    response = dashscope.Generation.call(
        model='qwen-max',
        prompt=prompt,
        history=[],
    )

    if response.status_code == HTTPStatus.OK:
        result = response.output.text
        print(result)
    else:
        result = 'ERROR'
    return result


def save_jsonl(data_lis, file_path):
    import json

    # 将字典列表写入文件，每一行一个字典
    with open(file_path, 'at', encoding='utf-8') as file:
        for item in data_lis:
            json_string = json.dumps(item, ensure_ascii=False) + '\n'
            file.write(json_string)


if __name__ == '__main__':
    file_name = 'a0.jsonl'
    conversations = []
    for i in tqdm(range(200)):
        Input = processing(qwen_api(1, 1))
        conversations.append(Input)
        if i % 2 == 0:
            save_jsonl(conversations, file_name)
            conversations.clear()