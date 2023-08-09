import re
import pandas as pd
def text_to_dic(text):
    dic = []
    date_str=None
    date = re.search(r'[0-9]{2}.[0-9]{2}.[0-9]{4}',text)
    if date is None:
        date = re.search(r'[0-9]{1}.[0-9]{2}.[0-9]{4}',text)
        
    if date is not None:
        date_str = text[date.start():date.end()]
        text = text[date.end():]
    while True:
        first=re.search(r'[0-9]\.',text)
        if first is None:
            break
        end = first.end()
        second = re.search(r'[0-9]\.',text[end:])
        if second is None:
            start = len(text)
            line = text[end:start+end-1]
            key_val = line.split('-',1)
            if len(key_val)<=1:
                print('"-" Not found')
                return dic,date_str
            key  = key_val[0].strip()
            val = key_val[1].strip().split('\n')
            if len(val)>1:
                meaning = val[0]
                example = ' '.join(val[1:])
            else:
                meaning,example = val[0],''
            dic.append((key,meaning,example))
            break
        else:
            start = second.start()
            line = text[end:start+end-1]
            key_val = line.split('-',1)
            if len(key_val)<=1:
                print('"-" Not found')
                return dic,date_str
            key  = key_val[0].strip()
            val = key_val[1].strip().split('\n')
            if len(val)>1:
                meaning = val[0]
                example = ' '.join(val[1:])
            else:
                meaning,example = val[0],''
            dic.append((key,meaning,example))
            text = text[second.end():]
    return dic,date_str


def get_dictionary_from_xlsx(path):
    # with open(path,'rb') as f:
    #     file = f.read()
    df = pd.read_excel(path)
    return df.values.tolist()

    # for w, m, e in zip(data['word'].values(),data['meaning'].values,data['example'].values()):



# print(get_dictionary_from_xlsx('input.xlsx'))