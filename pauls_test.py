from utils import getAccountInfo
from utils import getPoolCreationRound
from utils import *
import pandas as pd
import json

"""
Step 1: 
Get all tokens in a certain range and save it as a csv.
"""
# @ Thomas: uncomment here and maybe try some other block range below block 20676722
# tokens = getCreatedTokensInRangeCSV(20676722, 20769721, "test_tokens.csv", 10000)

# @Thomas: comment out to ...
tokens_01 = pd.read_csv("tokes_save_20726722_20769721.csv")
tokens_02 = pd.read_csv("tokes_save_20676722_20726722.csv")

tokens = pd.concat([tokens_01, tokens_02])
tokens = tokens.drop_duplicates()
#  ... here
"""
Step 2: 
- Only take those tokens where total > 1
- Get Pool Creation Round for those tokens
- Only take those tokens where liquidity pool exists (!= -1)
- Get Pool Address fot those tokens

Returns df with columns: 
['asset_id', 'creator', 'manager', 
'reserve', 'freeze', 'total', 
'decimals', 'block', 'pool_creation_round', 'pool_address']
"""
tokens1 = tokens[tokens.total > 1]
tokens1["pool_creation_round"] = tokens1["asset_id"].apply(getPoolCreationRound)
tokens2 = tokens1[tokens1["pool_creation_round"] != -1]
tokens2["pool_address"] = tokens2["asset_id"].apply(getPoolAddr)
print(tokens2.columns)
print(tokens2.head())

# ==============================================
# Above for some tests blocks for faster calculations
# ==============================================
# @Thomas: comment out this part, from here .....
test_blocks = [20722172, 20722033, 20707459, 20701948, 20697358, 20687822, 20685413, 20684275, 20768025, 20763682, 20745892, 20729836]

df = pd.DataFrame(columns=['asset_id', 'creator', 'manager',
                  'reserve', 'freeze', 'total', 'decimals', 'block'])
for i in test_blocks:
    assets = getCreatedAssetByBlock(i)
    assets = [dict(item, **{'block': i}) for item in assets]
    if len(assets) == 0:
        continue
    else:
        df = df.append(assets, ignore_index=True, sort=False)

df = df[df["total"] > 1]
df["pool_creation_round"] = df["asset_id"].apply(getPoolCreationRound)
df["pool_address"] = df["asset_id"].apply(getPoolAddr)
print(df)
#  .... to here.
# ==============================================
# ==============================================

"""
Step 3: 
- Transform pd.DataFrame to a dict
- Append for each token all asset txs in a given block_range after pool 
  creation which are external and add to each external tx the 'type' value 

Returns a list of token dicts, where the token dicts have the information: 
['asset_id', 'creator', 'manager', 'reserve', 'freeze', 'total', 'decimals', 'block', 
'pool_creation_round', 'pool_address', 'external_txs'] and 
'external_txs' is a list of dicts with the keys: 
['asset-transfer-transaction', 'close-rewards', 'closing-amount', 'confirmed-round', 'fee', 'first-valid', 'genesis-hash', 'genesis-id', 'group', 'id', 'intra-round-offset', 'last-valid', 'receiver-rewards', 'round-time', 'sender', 'sender-rewards', 'signature', 'tx-type', 'type']

"""
# @Thomas: comment out this part, from here ...
tokendf = df.copy() # df = test dataframe
# ... to here.

tokendf = tokens2.copy()
block_range = 150 # 150 blocks are approx. 10 minutes
# Start
token_dict = tokendf.to_dict('records')
# 
for asset in token_dict: 
    asset['external_txs'] = list()
    txs_in_range = getAssetTxInRange(asset["pool_creation_round"], asset["pool_creation_round"] + block_range, asset["asset_id"], 0, asset['pool_address'])
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

# Save step beacuse above loop takes quite some time
with open('token_dict_save', 'w') as fout:
    json.dump(token_dict, fout)

"""
Step 4: 
- Subset the dict to only those tokens which have more than 2 txs 
  after certain number of rounds after pool creation
"""
token_dict_w_ext_txs = []
for tokens in token_dict: 
    if len(tokens['external_txs']) >= 2: 
        token_dict_w_ext_txs.append(tokens)
    else: 
        continue 

"""
Step 5: 
- Go thorugh all txs per token and check if 
there are matching Buy & Sell txs of a single account
- Adding those addresses as list to dict 

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! Probably change the getMatchingBuySellTxs 
! function so that it also return the profit per transaction
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

"""
for tokens in token_dict_w_ext_txs: 
    detected_addr = getMatchingBuySellTxs(tokens['external_txs'], similarity = 0)
    tokens['detected_addr'] = detected_addr
    print(tokens['detected_addr'])

"""
Step 6: 
- Only use those tokens where there are detected addresses 
"""
token_dict_det_adr = list()
for tokens in token_dict_w_ext_txs: 
    if len(tokens['detected_addr']) > 0: 
        token_dict_det_adr.append(tokens)
    else: 
        continue