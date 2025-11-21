# test_prompt.py
from re import escape
import sys
import json
import pandas as pd
from prompt_manager import PromptManager
from utils.utils import *
import random

manager = PromptManager('./prompts/full_dump_select_tools')

res_tag=True
if len(sys.argv)>3:
    res_tag=False

def get_features(file_name):
    df=read_df(file_name)
    data=[]
    for id, i in df.iterrows():
        query = i['query']
        title = i['title']

        if res_tag:
            try:
                command_list=eval(str(i['command_list']))
                select_tools=eval(str(i['select_tools']))
                query_rewrite=eval(str(i['tools_querys']))
                tools_params=eval(str(i['tools_params']))
            except:
                print("error1")
                continue
            if len(select_tools)>0 and  select_tools[0]!='do_nothing'  and  len(select_tools)!=len(tools_params):
                print('error2')
                continue
        else:
            try:
                command_list=eval(str(i['command_list']))
            except:
                continue

        if len(command_list)>10:
            print(query,"too many commands")
            continue
    
        if len(command_list)<1:
            print(query,"too few commands")
            continue

        random.shuffle(command_list)

        command_txt=""
        for idj, j in enumerate(command_list):
            if j not in tools:
                print("not found tool_name",j)
                continue
            command_txt=command_txt + str(idj + 1)+". " + str(tool_function_call[j]['function'])+'\n'
        command_txt= command_txt.strip()
            
        prompt=manager.build_prompt({
            'query': query,
            'title': title,
            #'time': generate_random_date(),
            'tool_desc': command_txt
        })

        if res_tag:
            response=""
            tag=True
            for j in select_tools:
                if j not in name2srcid:
                    print("not found tool_name",j)
                    tag=False
                    break

            res={}
            if tag:
                res['select_tools']=[]
                if len(select_tools)==len(tools_params) and len(tools_params)!=0 and len(select_tools)==len(query_rewrite):
                    for j in range(len(select_tools)):
                        if select_tools[j] not in name2srcid:
                            print("not found tool_name",select_tools[j])
                            continue
                        if len(tools_params[j])>0:
                            # 检查参数名是否符合要求
                            param_names=[tools[name2srcid[select_tools[j]]]['parameters'][k]['name'] for k in range(len(tools[name2srcid[select_tools[j]]]['parameters']))]
                            #print(select_tools[j],param_names)
                            tools_params_new=[]
                            for k in range(len(tools_params[j])):
                                t_param=list(tools_params[j][k].keys())[0]
                                if t_param not in param_names:
                                    print("not found param_name",select_tools[j],t_param)
                                    continue
                                tools_params_new.append(tools_params[j][k]) 
                            tools_params[j]=tools_params_new
                              
                            res['select_tools'].append({'tool_name':select_tools[j],'query':query_rewrite[j],'parameters':tools_params[j]})
                        else:
                            res['select_tools'].append({'tool_name':select_tools[j],'query':query_rewrite[j],'parameters':[]})
                elif len(tools_params)==0 or tools_params[0]==[]:
                    for j in range(len(select_tools)):
                        res['select_tools'].append({'tool_name':select_tools[j],'query':'','parameters':[]})
                else:
                    print(len(select_tools),len(tools_params))
                    response=""
            
            if res!={}:
                response=json.dumps(res,ensure_ascii=False,indent=4)
            else:
                response=""
            
            if response=="":
                continue
            data.append({
                'query': query,
                'title': title,
                'command_list':i['command_list'],
                'select_tools':i['select_tools'],
                'tools_querys':i['tools_querys'],
                'tools_params':i['tools_params'],
                'prompt': prompt,
                'response': response
            })
        else:
            t=i.to_dict()
            t['prompt']=prompt
            data.append(t)

    return data

if __name__ == '__main__':
    data=get_features(sys.argv[1])
    print(len(data))
    save_list_as_jsonl(data,sys.argv[2])
    print('done')