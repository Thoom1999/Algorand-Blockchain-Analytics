from concurrent.futures import thread
from typing import Callable
from matplotlib.pyplot import get
import requests
import json
from functools import reduce
import pandas as pd
from sympy import limit
from tinyman.v1.contracts import get_pool_logicsig
import threading
import time

base_URL = "http://176.9.25.121:8980"

def flat(list_of_lists: list) -> list:
    return reduce(list.__add__, list_of_lists)

def flatMap(fn: Callable, iter: list) -> list:
    return flat(map(fn, iter))

def prettyPrint(obj):
    print(json.dumps(obj, indent=4, sort_keys=True))

def getJSON(url: str, cnt = 0):
    """
    Returns the json repsonse of the api call. 
    """
    try:
        response = requests.get(url)
        if response.status_code == 200: 
            return response.json()
        elif cnt <= 3 & 'timeout' in response.json()['message']: 
            time.sleep(3)
            cnt += 1
            getJSON(url, cnt)
        else:
            print(f"[{response.status_code}]", response.json()['message'])
    except requests.exceptions.HTTPError as e:
        print(e.response.text) 

def getBlockInfos(block_number: int): 
    """
    Returns all available information regarding one specific block.
    """
    return getJSON(f"{base_URL}/v2/blocks/{str(block_number)}")

def getAccountInfo(addr: str):
    """
    Returns all available information regarding one specific address.
    """
    return getJSON(f"{base_URL}/v2/accounts/{str(addr)}")

def getCreatedAssetByBlock(block_number: int): 
    """
    Returns all created assets and their information in one specific block.
    """
    blockinfo = list(filter(lambda tx: "asset-config-transaction" in tx 
                    and "created-asset-index" in tx, 
                getBlockInfos(block_number)["transactions"]))

    assets_in_block = list()
    for tx in blockinfo:
        temp_dict = {
            "asset_id":  tx["created-asset-index"], 
            "creator": tx["asset-config-transaction"]["params"]["creator"],
            "manager": "None", 
            "reserve": "None", 
            "freeze": "None",
            "total": tx["asset-config-transaction"]["params"]["total"], 
            "decimals": tx["asset-config-transaction"]["params"]["decimals"],
        }
        if "manager" in tx["asset-config-transaction"]["params"].keys(): 
            temp_dict["manager"] = tx["asset-config-transaction"]["params"]["manager"]
        if "reserve" in tx["asset-config-transaction"]["params"].keys():
            temp_dict["reserve"] = tx["asset-config-transaction"]["params"]["reserve"]
        if "freeze" in tx["asset-config-transaction"]["params"].keys():
            temp_dict["freeze"] = tx["asset-config-transaction"]["params"]["freeze"]
        
        assets_in_block.append(temp_dict)
        del temp_dict
    
    return(assets_in_block)

def createdTokenByAddress(addr: str): 
    """
    Returns all tokens/assets created by one address.
    """
    return getAccountInfo(addr)["account"]["created-assets"]
    
def getAssetTxInBlock(block_number: int, asset_id: int):
    """
    Returns all asset txs in a specific block.
    """ 
    block = getBlockInfos(block_number)
    return list(filter(
        lambda tx: "asset-transfer-transaction" in tx 
            and str(tx["asset-transfer-transaction"]["asset-id"]) == str(asset_id),
        block['transactions']
    ))

def getAssetTxInRange(start_block: int, end_block: int, asset_id: int, amt_gt: int, pool_addr: str):
    """
    Returns all asset txs in a certain range where pool_address is involved and amount >= min_amt. 
    """
    query = f"{base_URL}/v2/assets/{asset_id}/transactions?address={pool_addr}&min-round={start_block}&max-round={end_block}&currency-greater-than={amt_gt}"
    try:
        return(getJSON(query)['transactions'])
    except TypeError:
        pass

def getCreatedTokensInRangeCSV(start, end, outpath, savestep): 
    """
    Goes through all blocks from end to start and saves the information as a .csv after savestep number of blocks
    """
    df = pd.DataFrame(columns=['asset_id', 'creator', 'manager', 'reserve', 'freeze', 'total', 'decimals', 'block'])
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
            df = pd.DataFrame(columns=['asset_id', 'creator', 'manager', 'reserve', 'freeze', 'total', 'decimals', 'block'])
    
    with open(outpath, "a") as f:
                df.to_csv(f, header=False, index=False)
    
    return(df)

def getPoolCreationRound(asset1_id, asset2_id = 0): 
    """
    Returns the round at which the pool is created for the asset pair asset1_id and ALGO (asset_id = 0)
    """

    MAINNET_VALIDATOR_APP_ID = 552635992
    try:
        pool_logicsig = get_pool_logicsig(MAINNET_VALIDATOR_APP_ID, asset1_id, asset2_id)
        acc_info = getAccountInfo(pool_logicsig.address())
        creation_round = acc_info["account"]["created-assets"][0]["created-at-round"]
        return(creation_round)
    except:
        return(-1)

def getPoolAddr(asset1_id, asset2_id = 0): 
    """
    Returns the liquidity pool's address. 
    """
    MAINNET_VALIDATOR_APP_ID = 552635992
    try:
        pool_logicsig = get_pool_logicsig(MAINNET_VALIDATOR_APP_ID, asset1_id, asset2_id)
        return(pool_logicsig.address())
    except:
        return("None")

def checkIfTxIsExternal(tx, asset_info): 
    """
    Checks if:\n 
    - the sender or receiver address of the tx is not the manager, reserve or freeze address of the pool\n
    - and if the sender or receiver of the tx is the pool address\n 
    - and the tx amount is > 0\n
    \n
    External Txs: Txs which are not connected to the controlling entities of the pool.\n
    Internal Txs: Txs where the receiver or sender address is either the manager, reserve and/or freeze address.\n
    \n
    Parameters
    ----------
    - tx: dict
        A dictionary with all the tx info, i.e. the output from getAssetTxInRange().\n
    - asset_info: dict
        A dictionary with all the info about the asset, i.e. creator, manager, reserve & freeze address, total, decimals, block, pool_creation_round and pool_address.\n
    Returns
    -------
    - True/False
        True: if tx is external and 
        False: if tx is internal
    """
    if tx["asset-transfer-transaction"]["receiver"] in [asset_info['creator'], asset_info['manager'], asset_info['reserve'], asset_info['freeze']] or\
        tx["sender"] in [asset_info['creator'], asset_info['manager'], asset_info['reserve'], asset_info['freeze']]: 
        return(False)
    elif tx["asset-transfer-transaction"]["receiver"] != asset_info['pool_address'] and\
        tx["sender"] != asset_info['pool_address']:
        return(False)
    elif tx["asset-transfer-transaction"]["amount"] <= 0: 
        return(False)
    else: 
        return(True)

def checkIfBuy(tx, asset_info): 
    """
    Checks if address in external tx buys tokens from the pool or if the address sells tokens to the pool.\n
    - tx: dict with all the tx infos
    - asset_info: dict with all the asset infos
    """    
    if tx["sender"] == asset_info['pool_address']: 
        return(True)
    else: 
        return(False)

def getTxOfAddr(account_id, start_round = None, end_round = None, asset_id = None, N = None , amt_gt = 0, amt_lt = None, tx_type = None):
    """
    Gets txs between start_round and end_round of the the account_id where the amount is greater than amt_gt
    and lower than amt_lt.\n
    Parameters
    ----------
    - amt_gt: int (Default = 0);
        Results should have an amount greater than this value. MicroAlgos are the default currency unless an asset-id is provided, in which case the asset will be used.\n
    - amt_lt: int (Default = None);
        Results should have an amount less than this value.\n
    """
    add_args = {'min-round':start_round, 'max-round':end_round, 'asset-id':asset_id, 'limit':N, 'currency-greater-than':amt_gt, 'currency-less-than':amt_lt, 'tx-type': tx_type}

    cnt = 0
    base_query = f"{base_URL}/v2/accounts/{account_id}/transactions"
    for arg in add_args.keys(): 
        if add_args[arg] is not None:
            if cnt == 0: 
                base_query += "?"+arg+"="+str(add_args[arg])
                cnt += 1
            else: 
                base_query += "&"+arg+"="+str(add_args[arg])
        else: 
            continue

    try: 
        req = getJSON(f"{base_query}")
        next = req['next-token']
        while len(getJSON(base_query+"&next="+str(next))['transactions'])>0:
            req['transactions'] += getJSON(base_query+"&next="+str(next))['transactions']
            next = getJSON(base_query+"&next="+str(next))['next-token']
        return(req['transactions'])
    except: 
        return(None)


def tokenDictLookup(tokendict, assetid): 
    """
    Looks up the asset_id in the tokendict and returns the dict with the information regarding this token.
    """
    for token in tokendict:
        if token['asset_id'] == assetid: 
            return(token)
        else: 
            continue

def getMatchingBuySellTxs(txs_lst, similarity = 0.05): 
    """
    Returns the account addresses of those accounts in the external txs_list which bought AND sold a similar amount of tokens within the given txs_lst.\n
    
    Parameters
    ----------
    - txs_list: list of dict; with one dict of the txs info per txs including the key 'type'\n
    - similarity: double; buy_sell_ratio <= similarity\n
    
    Returns
    ----------
    - list of addresses
    """
    filtered_txs = dict()
    for txs in txs_lst: 
        tx_type = txs['type']
        amt = txs['asset-transfer-transaction']['amount']

        if tx_type == 'buy': 
            bs_addr = txs['asset-transfer-transaction']['receiver']
        else: 
            bs_addr = txs['sender']

        if bs_addr not in filtered_txs.keys(): 
            filtered_txs[bs_addr] = [0, 0] # [bough amount, sold amount]
        if tx_type == 'buy': 
            filtered_txs[bs_addr][0] += amt
        else: 
            filtered_txs[bs_addr][1] += amt

    detected_addr = list()
    for addr, bs in filtered_txs.items():
        if min(bs) == 0: 
            continue
        else:
            buy_sell_ratio = max(bs)/min(bs) - 1 # How much % were bought/sold more 
            if buy_sell_ratio <= similarity: 
                detected_addr.append(addr)
            else: 
                continue
    
    return(detected_addr)

def createChunk(start: int, end: int, size: int) -> list:
    """Divide a range of numbers in chunks of size 'size'"""
    result: list = []
    end += 1
    step: int = int((end - start) / size)
    for i in range(step): 
        result.append(list(range(start + i * size, start + (i + 1) * size)))
    if start + step * size != end: 
        result.append(list(range(start + step * size, end)))
    return result

def createAndExecuteThreads(nbr: int, func) -> None: 
    threads: list = []
    for i in range(nbr): 
        t = threading.Thread(target=func)
        t.start()
        threads.append(t)
    for thread in threads: 
        thread.join()

def addLiquidityForFirstTime(poolAddr: str, liquidityToken: int): 
    query = getJSON(f"{base_URL}/v2/accounts/{poolAddr}/transactions")
    txs = list(filter(lambda tx: "asset-transfer-transaction" in tx,
                query["transactions"]))
    r = {}
    for tx in txs: 
        if tx["asset-transfer-transaction"]["asset-id"] == liquidityToken: 
            r = tx["confirmed-round"]
    print(r)

def getLiquidityToken(asset_id, asset2_id = 0): 
    """
    Get the liquidity token (pool token) of the asset_id
    """
    MAINNET_VALIDATOR_APP_ID = 552635992
    try: 
        pool_logicsig = get_pool_logicsig(MAINNET_VALIDATOR_APP_ID, asset_id, asset2_id)
        acc_info = getAccountInfo(pool_logicsig.address())['account']['assets']
        for ass in acc_info: 
            if ass['asset-id'] != asset_id: 
                return(ass['asset-id'])
            else: 
                continue
    except:
        return(-1)     


# def oneFuncToRuleThemAll(token_dict_path, txs_range):
# If Peters dict does not include pool creation round or pool creation address 
token_dict_path = "assetinfos_20000000_21000000.json"
with open(token_dict_path, "r") as fin: 
        token_dict = json.load(fin)

tokens_w_pool = list()
for token in token_dict: 
    for acc in ['manager', 'reserve', 'freeze', 'creator']: 
        if acc not in token.keys(): 
            token[acc] = 'None'
    token['pool_creation_round'] = getPoolCreationRound(token['asset_id'])
    if token['pool_creation_round'] != -1: 
        token['pool_address'] = getPoolAddr(token['asset_id'])
        tokens_w_pool.append(token)
    else: 
        continue

###############################
token_dict_w_ext_txs = []
for asset in token_dict: 
    asset['external_txs'] = list()
    # Add asset['pool_liquidity_add'] with function
    # and change getAssetTxInRange to get all txs which interact with the liquidity pool without the 
    token_txs_in_range = getTxOfAddr(asset['pool_address'], asset["pool_creation_round"], asset["pool_creation_round"] + txs_range, asset_id = asset['asset_id'])
    algo_txs_in_range = getTxOfAddr(asset['pool_address'], asset["pool_creation_round"], asset["pool_creation_round"] + txs_range, asset_id = 0)
    # txs_in_range = getAssetTxInRange(, , asset["asset_id"], 0, asset['pool_address'])
    # ########## Change below
    for txs in txs_in_range: 
        if checkIfTxIsExternal(txs, asset): 
            if checkIfBuy(txs, asset): 
                txs['type'] = 'buy'
                asset['external_txs'].append(txs)
            else: 
                txs['type'] = 'sell'
                asset['external_txs'].append(txs)
        else: 
            continue
    if len(asset['external_txs']) >= 2: 
        token_dict_w_ext_txs.append(asset)
    #  to here

