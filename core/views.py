import json
from django.shortcuts import render
from .models import Wallet, Word
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse



def index(request):
    return render(request, "wallet.html")


def mint(request):
    return render(request, "buy.html")


def tickets(request):
    return render(request, "tickets.html")


def tables(request):
    wallets = Wallet.objects.all().order_by("id")
    return render(request, "tables.html", {"first_part": wallets[:12], "second_part": wallets[12::]})

@csrf_exempt
def getWallets(_, address):
    r = requests.get(f"https://testnet.tonapi.io/v2/accounts/{address}/nfts?collection=kQBxz61JNGiQMvhOjskf88N6ryXQ4yFW18BzkBCDWQHp5pR8&limit=1000&offset=0&indirect_ownership=false")
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
        results[word.wallet_id - 1][word.name]["address"] = nft["address"]

    new_result = []

    

    for result in results:
        a = []
        for _, value in result.items():
            a.append(value)

        new_result.append(a)
    
    return JsonResponse({"data": new_result})
