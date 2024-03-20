from django.shortcuts import render
from tonsdk.contract.token.nft import NFTCollection, NFTItem
from tonsdk.contract import Address
from tonsdk.utils import to_nano, bytes_to_b64str
from tonsdk.contract.wallet import Wallets, WalletVersionEnum
import requests
from pathlib import Path
from pytonlib import TonlibClient
from .models import Wallet, Word
from django.conf import settings

datas = ['https://gateway.irys.xyz/nG8TR8NKBZ0Cqj1BQ16zY0EXar58VbZr-DV_28-0vzI', 'https://gateway.irys.xyz/GMezoftxgRuyPc4wKlos9V0pseP4LeDNHDqgPnM7fHs', 'https://gateway.irys.xyz/QjAVeDozR5ONOSzbR-Q_Oajb1f__Qj6cv9GUILOTRqo', 'https://gateway.irys.xyz/aRU1b8_lgf5BkCFDnxnEWmS3uRxkcQ6uIgizrAn8dIs', 'https://gateway.irys.xyz/mzvC9BMbjN4CK7niJohdGWJBAkQuIMH6OyHtFkWkdAY', 'https://gateway.irys.xyz/VCwX34pI4_1d3Ma32n7rVsmQs_REWKAsl1zSydo7a_I', 'https://gateway.irys.xyz/kdENR7zOMX6bdpHkWdkBep5rEsWgL7iNjNaZGCyeBsk', 'https://gateway.irys.xyz/kwiOxmojdmtPbyTasHLmU-mFZL4Up65kzR5hCGTBsQI', 'https://gateway.irys.xyz/RkTXtsK8A3MStPgcV1Pz2ziAWP5xInjgN8x4cYiJIJM', 'https://gateway.irys.xyz/xaCPdPBDLATirfAUvFTEWqBt8Oqih2EJLRdMg_TgRSA', 'https://gateway.irys.xyz/DkmiB4SYHU__MIqnPJUIsuvL_IIip8o5v3P4_Nr13Pw', 'https://gateway.irys.xyz/YAAFnkCDB3Jh3T3NQT_H89wxi3ETkgsGdQUX_ZdrgZk', 'https://gateway.irys.xyz/YhmkOc4bz86EFJ4D1QaMresQHYQ5Xs_-A5ZPYFkP5lo', 'https://gateway.irys.xyz/a6U8JZYATlZrkmkCS_kehTr2fDe2NX0jbJMoizDZI7s', 'https://gateway.irys.xyz/KML2EPZJfbscMrpj8sL74b36JTmgpj3jgIiN_wGWxYo', 'https://gateway.irys.xyz/ICTHwS2VxzNxFDE05xShRkC6cFc__to_pfUJyv0vUHE', 'https://gateway.irys.xyz/OocPeaylPnRoHb4Ku_Ly7fGkMqXBKudei2ZIPt8nK0g', 'https://gateway.irys.xyz/zVR-wvHeZkuyYQnsx_G6ynrQgU8eexlFeSXytM_gmYU', 'https://gateway.irys.xyz/qolJg5sc3ME_7_oMi8YVo1FwxZKbwoBjT2Bv44cHTq8', 'https://gateway.irys.xyz/e60W0Tf1surpexb8H3qJBJQiqNEBZLlBsimAb-z8vX4', 'https://gateway.irys.xyz/bPafwuEp02l3IpXpfmJYu_0IOuGnRrKowIQ-9POl0Ic', 'https://gateway.irys.xyz/26Fq42PkzJXQ0EjsJNP24VXynOUEYsG4dQfVfy2gQZ4', 'https://gateway.irys.xyz/Ng4RMl5qNtPA8PsSH9ZPA6q9_XWQE68BsyZVkfSXN18', 'https://gateway.irys.xyz/O27v5Kam3WB8wRJEZl6JCRHkkXk1YeNMvnTPc9eIbpo']


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

    _, pub_k, priv_k, wallet = Wallets.from_mnemonics(mnemonics=settings.mnemonics, version=WalletVersionEnum.v4r2,
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



def index(request):
    return render(request, "wallet.html", {"wallets": Wallet.objects.all().order_by("id")})


def mint(request):
    if request.method == "POST":
        pass
    words = Word.objects.filter(index = None)
    return render(request, "buy.html", {"words_quantity": len(words)})


def tickets(request):
    return render(request, "tickets.html")