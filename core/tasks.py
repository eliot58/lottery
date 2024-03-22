import asyncio
from tonsdk.contract.token.nft import NFTCollection, NFTItem
from tonsdk.contract import Address
from tonsdk.utils import to_nano
from tonsdk.contract.wallet import Wallets, WalletVersionEnum
import requests
from pathlib import Path
from pytonlib import TonlibClient
from celery import shared_task
import os


async def get_client():
    url = 'https://ton.org/testnet-global.config.json'

    config = requests.get(url).json()

    keystore_dir = '/tmp/ton_keystore'
    Path(keystore_dir).mkdir(parents=True, exist_ok=True)

    client = TonlibClient(ls_index=2, config=config, keystore=keystore_dir, tonlib_timeout=300)

    await client.init()

    return client


async def get_seqno(client: TonlibClient, address: str):
    data = await client.raw_run_method(method='seqno', stack_data=[], address=address)
    return int(data['stack'][0][1], 16)


def create_collection():
    royalty_base = 1000
    royalty_factor = 55

    collection = NFTCollection(royalty_base=royalty_base,
                               royalty=royalty_factor,
                               royalty_address=Address('UQBQMnbLeZPWxWWIMWSvT2imuWcJFiXe1emPwJVgCK93k6Di'),
                               owner_address=Address('UQBQMnbLeZPWxWWIMWSvT2imuWcJFiXe1emPwJVgCK93k6Di'),
                               collection_content_uri='https://node1.irys.xyz/EEDnSsi9iLRlhuEx4BbuQsi6jR357Ug3eniXSAuZG30',
                               nft_item_content_base_uri='https://node1.irys.xyz/',
                               nft_item_code_hex=NFTItem.code)
    
    return collection

def create_nft_mint_body(address, content, index):
    collection = create_collection()

    body = collection.create_mint_body(item_index=index,
                                       new_owner_address=Address(address),
                                       item_content_uri=content,
                                       amount=to_nano(0.02, 'ton'))

    return body


async def deploy_item(address, content, index):

    _, pub_k, priv_k, wallet = Wallets.from_mnemonics(mnemonics=os.getenv('mnemonics').split(), version=WalletVersionEnum.v4r2,
                                                          workchain=0)
    
    client = await get_client()

    seqno = await get_seqno(client, wallet.address.to_string(True, True, True, True))
    
    
    body = create_nft_mint_body(address, content, index)
    collection = create_collection()

    query = wallet.create_transfer_message(to_addr=collection.address.to_string(),
                                        amount=to_nano(0.04, 'ton'),
                                        seqno=seqno,
                                        payload=body)
    

    await client.raw_send_message(query['message'].to_boc(False))


@shared_task(bind=True)
def deploy(self, items):
    for item in items:
        asyncio.get_event_loop().run_until_complete(deploy_item(item["address"], item["content"], item["index"]))
