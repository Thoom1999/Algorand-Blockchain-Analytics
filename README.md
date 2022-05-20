# Algorand-Blockchain-Analytics

## Idea
By scanning block it is possible to detect created token and their creator and the block creation.

We can't directly get the tx where a given asset is involved (like the block explorer)
But bots act at the short time after asset creation. So we just have to scan the block following the asset creation to detect bot activity

## TODO
Format of data (list, json, dict ???) I'm using dict for the moment

## Notes

block -> asset-config-transaction return
A priori can't get directly tx associated to an asset ... 