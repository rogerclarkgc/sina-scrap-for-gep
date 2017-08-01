import pymongo

KEY = 'keyword'
CONTENT = '大熊猫'

client = pymongo.MongoClient()
col = client.sina.weibo
cursor = col.find({})
count = 0
non = 0

for file in cursor:
    if 'keyword' in file.keys():
        non+=1
    else:
        file[KEY] = CONTENT
        res = col.replace_one(filter={'_id':file['_id']},
                              replacement=file,
                              upsert=True)
        count = count + res.matched_count

print('update:', count, non)
print(file)

client.close()