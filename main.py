import os 
from utils import *
import json

# files = os.listdir("./tx_data/tx_data")

# initial_count = 0
# dir = "./tx_data/tx_data"
# for path in os.listdir(dir):
#     if os.path.isfile(os.path.join(dir, path)):
#         initial_count += 1

# i = 0

# for f in files: 
    
#     i += 1
#     print(f"{i}/{initial_count}")
#     try: 
#         fn = "./tx_data/tx_data/" + f
#         with open(fn) as jsonFile:
#             print(fn)
#             j = json.load(jsonFile)
#             jsonFile.close()
            
#         poolAddr = j["pool_address"]
#         startRound = j["first_liquidity_round"]
#         result = calculateProfit(poolAddr, startRound)
#         fr = "./results/" + poolAddr + ".json"
#         with open(fr, 'w') as jsonFile: 
#             json.dump(result, jsonFile, indent=4)
#             jsonFile.close()
#     except: 
#         print("Problem")
#         continue

files = os.listdir("./results")

activityOfAddresses = dict()

for f in files: 
    fn = "./results/" + f
    with open(fn) as jsonFile:
        j = json.load(jsonFile)
        jsonFile.close()

    for element in j: 
        k = j.keys()
        listKey = []
        for key in k: 
            if key not in listKey: 
                listKey.append(key)

    for element in listKey: 
        d = dict()
        d["interactions"] = 0
        d["pools"] = []
        activityOfAddresses[element] = d

for f in files: 
    fn = "./results/" + f
    with open(fn) as jsonFile:
        j = json.load(jsonFile)
        jsonFile.close()

    for element in j: 
        k = j.keys()
        for key in k:
            # print(key)
            activityOfAddresses[key]["interactions"] += 1
            index = f.rfind(".")
            if f[:index] not in activityOfAddresses[key]["pools"]: 
                activityOfAddresses[key]["pools"].append(f[:index])
            
               

# print(activityOfAddresses)
with open("results.json", "w") as jsonFile: 
    json.dump(activityOfAddresses, jsonFile, indent=4)