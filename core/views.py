import json
from django.shortcuts import render
import openpyxl
from .models import Wallet, Word
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from random import randint, choice



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
    r = requests.get(f"https://testnet.tonapi.io/v2/accounts/{address}/nfts?collection=EQA4SnGyqOHqI01xDKHalYYF_o-ELlxUyBVcMkhG-MSEOnLm&limit=1000&offset=0&indirect_ownership=false")
    results = {}

    nfts = json.loads(r.text)["nft_items"]



    # nfts = []

    # wb = openpyxl.load_workbook('json.xlsx', data_only=True)

    # sheet = wb["json v2"]
    # for i in range(1, 3001):
    #     nfts.append({"index": int(sheet[f"K{i}"].value) - 1})


    # for i in range(len(nfts)):
    #     nfts[i]["metadata"] = {}
    #     nfts[i]["metadata"]["content_url"] = "https://ipfs.io/ipfs/QmfH18WREYt2KcoaFvHdLCVQJwVQ12EeirDyGRfqauQwtF/srp_s1_24.png"
    #     nfts[i]["address"] = "0:b4027af7e9cfc555ac403999fdd7392994979319bec86b6e463212bd92a334f9"



    user_index = [nft["index"] for nft in nfts]

    users_nft_info = {nft["index"]: {"content": nft["metadata"]["content_url"], "address": nft["address"]} for nft in nfts}

    sum_of_tickets = 0

    for wallet in Wallet.objects.all().order_by("id"):
        results[wallet.id] = {}
        k = 0
        for word in wallet.word_set.values_list("name", "index"):
            if word[0] in results[wallet.id] and word[1] in user_index:
                results[wallet.id][word[0]]["quantity"] += 1
            elif word[0] not in results[wallet.id] and word[1] in user_index:
                results[wallet.id][word[0]] = {}
                results[wallet.id][word[0]]["quantity"] = 1
                results[wallet.id][word[0]]["content"] = users_nft_info[word[1]]["content"]
                results[wallet.id][word[0]]["address"] = users_nft_info[word[1]]["address"]
                k += 1
            elif word[0] not in results[wallet.id] and word[1] not in user_index:
                results[wallet.id][word[0]] = {}
                results[wallet.id][word[0]]["quantity"] = 0


        sum_of_tickets += k

        if k == 24:
            if wallet.winner == None:
                results[wallet.id] = {"seed": " ".join(wallet.word_set.values_list("name", flat = True).distinct()), "prize": wallet.prize}
                wallet.winner = address
                wallet.save()
            else:
                if wallet.winner == address:
                    results[wallet.id] = {"seed": " ".join(wallet.word_set.values_list("name", flat = True).distinct()), "prize": wallet.prize}
                else:
                    results[wallet.id] = {"address": wallet.winner[:10:] + "............" + wallet.winner[-10::]}
        else:
            if wallet.winner == None:
                i = 1
                new = {}
                for _, value in results[wallet.id].items():
                    new[i] = value
                    i += 1

                results[wallet.id] = new
            else:
                results[wallet.id] = {"address": wallet.winner[:10:] + "............" + wallet.winner[-10::]}

    return JsonResponse({"data": results, "pieces": sum_of_tickets})
