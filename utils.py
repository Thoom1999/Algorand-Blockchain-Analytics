from typing import Callable
import requests
import json
from functools import reduce

base_URL = "http://176.9.25.121:8980"

def flat(list_of_lists: list) -> list:
    return reduce(list.__add__, list_of_lists)

def flatMap(fn: Callable, iter: list) -> list:
    return flat(map(fn, iter))

def prettyPrint(obj):
    print(json.dumps(obj, indent=4, sort_keys=True))

def getJSON(url: str):
    try:
        response = requests.get(url)
        if response.status_code == 200: 
            return response.json()
        else: 
            print(f"[{response.status_code}]", response.json()['message'])
    except requests.exceptions.HTTPError as e:
        print(e.response.text) 

def getBlockInfos(block_number: int): 
    return getJSON(f"{base_URL}/v2/blocks/{str(block_number)}")

def getAccountInfo(addr: str):
    return getJSON(f"{base_URL}/v2/accounts/{str(addr)}")

def getCreatedAssetByBlock(block_number: int): 
    block = getBlockInfos(block_number)
    return list(map(
        lambda tx: {
            "creator": tx["asset-config-transaction"]["params"]["creator"],
            "asset_id":  tx["created-asset-index"]
        },
        filter(
            lambda tx: "asset-config-transaction" in tx 
                and "created-asset-index" in tx, 
            block['transactions']
        )
    ))

def createdTokenByAddress(addr: str): 
    return getAccountInfo(addr)["account"]["created-assets"]
    
def getAssetTxInBlock(block_number: int, asset_id: int): 
    block = getBlockInfos(block_number)
    return list(filter(
        lambda tx: "asset-transfer-transaction" in tx 
            and str(tx["asset-transfer-transaction"]["asset-id"]) == str(asset_id),
        block['transactions']
    ))

def getAssetTxInRange(start_block: int, end_block: int, asset_id: int):
    return flatMap(
        lambda block_n: getAssetTxInBlock(block_n, asset_id),
        range(start_block, end_block)
    )

