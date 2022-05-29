from typing import Callable
import requests
import json
from functools import reduce
import pandas as pd

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
            "asset_id":  tx["created-asset-index"], 
            # "name": tx["asset-config-transaction"]["params"]["name"],
            "creator": tx["asset-config-transaction"]["params"]["creator"],
            "total": tx["asset-config-transaction"]["params"]["total"], 
            "decimals": tx["asset-config-transaction"]["params"]["decimals"],
            # "tx_type": tx["tx-type"]
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


# Goes through all blocks from end to start
# and saving the information as a .csv after savestep number of blocks
def getCreatedTokensInRangeCSV(start, end, outpath, savestep): 
    df = pd.DataFrame(columns=['asset_id', 'creator', 'total', 'tx_type', 'block'])
    with open(outpath, "w") as f:
        df.to_csv(f, header=True, index=False)

    cnt = 0
    for i in range(end, start-1, -1):
        cnt += 1
        print(str(cnt)+"/"+str(end-start))
        try: 
            assets = getCreatedAssetByBlock(i)
            assets = [dict(item, **{'block':i}) for item in assets]

            if len(assets) == 0:
                continue
            else:
                df = df.append(assets, ignore_index=True, sort=False)
        except TypeError: 
            continue

        if cnt in list(range(1, end - start, savestep)): 
            with open(outpath, "a") as f:
                df.to_csv(f, header=False, index=False)

            del df
            df = pd.DataFrame(columns=['asset_id', 'creator', 'total', 'tx_type', 'block'])
    
    with open(outpath, "a") as f:
                df.to_csv(f, header=False, index=False)
    

    return(df)
