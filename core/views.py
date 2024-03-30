import json
from django.shortcuts import render, redirect
from .models import Wallet, Word
from random import randint
import asyncio
from tonsdk.contract.token.nft import NFTCollection, NFTItem
from tonsdk.contract import Address
from tonsdk.utils import to_nano
from tonsdk.contract.wallet import Wallets, WalletVersionEnum
import requests
from pathlib import Path
from pytonlib import TonlibClient
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

datas = ['https://gateway.irys.xyz/nG8TR8NKBZ0Cqj1BQ16zY0EXar58VbZr-DV_28-0vzI', 'https://gateway.irys.xyz/GMezoftxgRuyPc4wKlos9V0pseP4LeDNHDqgPnM7fHs', 'https://gateway.irys.xyz/QjAVeDozR5ONOSzbR-Q_Oajb1f__Qj6cv9GUILOTRqo', 'https://gateway.irys.xyz/aRU1b8_lgf5BkCFDnxnEWmS3uRxkcQ6uIgizrAn8dIs', 'https://gateway.irys.xyz/mzvC9BMbjN4CK7niJohdGWJBAkQuIMH6OyHtFkWkdAY', 'https://gateway.irys.xyz/VCwX34pI4_1d3Ma32n7rVsmQs_REWKAsl1zSydo7a_I', 'https://gateway.irys.xyz/kdENR7zOMX6bdpHkWdkBep5rEsWgL7iNjNaZGCyeBsk', 'https://gateway.irys.xyz/kwiOxmojdmtPbyTasHLmU-mFZL4Up65kzR5hCGTBsQI', 'https://gateway.irys.xyz/RkTXtsK8A3MStPgcV1Pz2ziAWP5xInjgN8x4cYiJIJM', 'https://gateway.irys.xyz/xaCPdPBDLATirfAUvFTEWqBt8Oqih2EJLRdMg_TgRSA', 'https://gateway.irys.xyz/DkmiB4SYHU__MIqnPJUIsuvL_IIip8o5v3P4_Nr13Pw', 'https://gateway.irys.xyz/YAAFnkCDB3Jh3T3NQT_H89wxi3ETkgsGdQUX_ZdrgZk', 'https://gateway.irys.xyz/YhmkOc4bz86EFJ4D1QaMresQHYQ5Xs_-A5ZPYFkP5lo', 'https://gateway.irys.xyz/a6U8JZYATlZrkmkCS_kehTr2fDe2NX0jbJMoizDZI7s', 'https://gateway.irys.xyz/KML2EPZJfbscMrpj8sL74b36JTmgpj3jgIiN_wGWxYo', 'https://gateway.irys.xyz/ICTHwS2VxzNxFDE05xShRkC6cFc__to_pfUJyv0vUHE', 'https://gateway.irys.xyz/OocPeaylPnRoHb4Ku_Ly7fGkMqXBKudei2ZIPt8nK0g', 'https://gateway.irys.xyz/zVR-wvHeZkuyYQnsx_G6ynrQgU8eexlFeSXytM_gmYU', 'https://gateway.irys.xyz/qolJg5sc3ME_7_oMi8YVo1FwxZKbwoBjT2Bv44cHTq8', 'https://gateway.irys.xyz/e60W0Tf1surpexb8H3qJBJQiqNEBZLlBsimAb-z8vX4', 'https://gateway.irys.xyz/bPafwuEp02l3IpXpfmJYu_0IOuGnRrKowIQ-9POl0Ic', 'https://gateway.irys.xyz/26Fq42PkzJXQ0EjsJNP24VXynOUEYsG4dQfVfy2gQZ4', 'https://gateway.irys.xyz/Ng4RMl5qNtPA8PsSH9ZPA6q9_XWQE68BsyZVkfSXN18', 'https://gateway.irys.xyz/O27v5Kam3WB8wRJEZl6JCRHkkXk1YeNMvnTPc9eIbpo']

async def get_client():
    url = 'https://ton.org/testnet-global.config.json'

    config = requests.get(url).json()

    keystore_dir = '/tmp/ton_keystore'
    Path(keystore_dir).mkdir(parents=True, exist_ok=True)

    client = TonlibClient(ls_index=2, config=config, keystore=keystore_dir, tonlib_timeout=300)

    await client.init()

    return client


def create_collection():
    royalty_base = 1000
    royalty_factor = 100

    collection = NFTCollection(royalty_base=royalty_base,
                               royalty=royalty_factor,
                               royalty_address=Address('UQDV-ogHM7uqUmSEDl8lSQyq7CX_jkI14rV04sPjydBajAHq'),
                               owner_address=Address('UQDV-ogHM7uqUmSEDl8lSQyq7CX_jkI14rV04sPjydBajAHq'),
                               collection_content_uri='https://node1.irys.xyz/',
                               nft_item_content_base_uri='https://node1.irys.xyz/',
                               nft_item_code_hex=NFTItem.code)

    return collection

def create_batch_nft_mint_body(contents, from_item_index):
    collection = create_collection()

    body = collection.create_batch_mint_body(from_item_index=from_item_index,
                                             contents_and_owners=contents,
                                             amount_per_one=to_nano(0.01, 'ton'))
    return body


async def deploy_batch(recieps):
    mnemonics = "vanish blur damp cave repeat affair total jazz review voyage pen must enlist estate enforce keen clock become orphan teach spike tank endorse spin".split()

    mnemonics, pub_k, priv_k, wallet = Wallets.from_mnemonics(mnemonics=mnemonics, version=WalletVersionEnum('hv2'),
                                                          workchain=0)
    
    client = await get_client()

    query = wallet.create_transfer_message(recipients_list=recieps, query_id=0)
    
    await client.raw_send_message(query['message'].to_boc(False))

    await client.close()



def index(request):
    return render(request, "wallet.html")


def mint(request):
    if request.method == "POST":
        words = Word.objects.filter(index = None) & Word.objects.filter(stage = 1)
        if len(words) == 0:
            words = Word.objects.filter(index = None) & Word.objects.filter(stage = 2)
        if len(words) == 0:
            words = Word.objects.filter(index = None) & Word.objects.filter(stage = 3)

        contents = []
        index = 13824 - len(Word.objects.filter(index = None))
        for i in range(int(request.POST["quantity"])):
            word = words[randint(0, len(words)-1)]

            contents.append(
                (datas[word.wallet_id-1].split("/")[-1], Address(request.POST["address"]))
            )

            word.index = index
            word.save()
            index += 1


        split_contents = [contents[i:i+4] for i in range(0, len(contents), 4)]

        recieps = []

        index = index - int(request.POST["quantity"])

        for content in split_contents:
            body = create_batch_nft_mint_body(content, index)

            recieps.append({
                'address': "EQBxz61JNGiQMvhOjskf88N6ryXQ4yFW18BzkBCDWQHp5i_2",
                'payload': body,
                'amount': to_nano('0.1', 'ton'),
                'send_mode': 3
            })
            index += 4

        

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(deploy_batch(recieps))

        return redirect(tickets)
            

    words = Word.objects.filter(index = None)
    return render(request, "buy.html", {"words_quantity": len(words)})


def tickets(request):
    return render(request, "tickets.html")

def info(request):
    return render(request, "info.html", {"wallets": Wallet.objects.all().order_by("id")})

def tables(request):
    wallets = Wallet.objects.all().order_by("id")
    return render(request, "tables.html", {"first_part": wallets[:12], "second_part": wallets[12::]})

@csrf_exempt
def getWallets(_, address):
    r = requests.get(f"https://testnet.tonapi.io/v2/accounts/{address}/nfts?collection=EQDnZeFWdKkjRZZkbHnVisVzhmws15dbLGCqocEf8DwxiDWN&limit=1000&offset=0&indirect_ownership=false")
    results = []

    for wallet in Wallet.objects.all().order_by("id"):
        d = {}
        for wallet in wallet.word_set.values_list("name", flat = True).distinct():
            d[wallet] = {"quantity": 0, "content": ""}
        results.append(d)

    nfts = json.loads(r.text)["nft_items"]

    for nft in nfts:
        word = Word.objects.get(index = nft["index"])
        results[word.wallet_id - 1][word.name]["quantity"] += 1
        results[word.wallet_id - 1][word.name]["content"] = nft["metadata"]["content_url"]

    new_result = []

    for result in results:
        a = []
        for _, value in result.items():
            a.append(value)

        new_result.append(a)
    
    return JsonResponse({"data": new_result})