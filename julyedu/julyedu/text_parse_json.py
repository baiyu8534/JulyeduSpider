import json
import re
import json

with open('./json_all_type.txt',"r",encoding="utf8") as f:
    json_str = f.read()

json_list_str = re.findall(r',"list":(.*?)]}', json_str)

print(json_list_str[0])

json_data = json.loads(json_list_str[0]+']')
print(json_data)
print("------------")
print(json_data[0]['ques_id'])

d = {}
if len(d.keys()) ==0:
    print(000)
f = 0
if f:
    print(1)
elif f == 0:
    print(000)
