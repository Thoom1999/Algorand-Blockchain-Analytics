import requests

base_URL = "http://176.9.25.121:8980/"

def getBlockInfos(blockNumber: str): 
    try:
        response = requests.get(base_URL + "v2/blocks/" + blockNumber)
        if response.status_code == 200: 
            return response.json()
        else: 
            print("Problem occur")
    except requests.exceptions.HTTPError as e:
        print(e.response.text) 

def getCreatedAssetByBlock(blockNumber: str): 
    try:
        response = requests.get(base_URL + "v2/blocks/" + blockNumber)
        if response.status_code == 200: 
            transactions = response.json()["transactions"]
            result = dict()
            for tx in transactions:
                try:
                    creator = tx["asset-config-transaction"]["params"]["creator"]
                    asset_id = tx["created-asset-index"]
                    result["creator"] = creator
                    result["asset_id"] = asset_id
                except: 
                    continue
            return result
        else: 
            print("Problem occur")
    except requests.exceptions.HTTPError as e:
        print(e.response.text) 

def createdTokenByAddress(addr: str): 
    try:
        response = requests.get(base_URL + "v2/accounts/" + addr)
        if response.status_code == 200: 
            result = response.json()["account"]["created-assets"]
            createdTokens = dict()
            for token in result: 
                createdTokens[token["index"]] = token["created-at-round"]
            data = dict()
            data[addr] = createdTokens
            return data
        else: 
            print("Problem occur")
    except requests.exceptions.HTTPError as e:
        print(e.response.text) 

def getTxAssociatedToAnAsset(blockNumber: str, asset_id: str): 
    try:
        response = requests.get(base_URL + "v2/blocks/" + blockNumber)
        if response.status_code == 200: 
            transactions = response.json()["transactions"]
            result = dict()
            listTx = []
            for tx in transactions:
                try:
                    if str(tx["asset-transfer-transaction"]["asset-id"]) == asset_id: 
                        listTx.append([tx["asset-transfer-transaction"]["amount"], tx["asset-transfer-transaction"]["receiver"]])
                except:
                    continue
            result[blockNumber] = listTx
            return result
        else: 
            print("Problem occur")
    except requests.exceptions.HTTPError as e:
        print(e.response.text) 

