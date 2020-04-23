import json


text= """{ "a" : 1, "b": 2, "c" : [1,2,3]}"""
result = json.loads(text)

print(result)
print(result['a'])
print(result['b'])
print(result['c'][2])


result = json.dumps(result)


print(result)
