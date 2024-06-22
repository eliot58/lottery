import json
from .models import Wallet
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


@csrf_exempt
def getWallets(_, address):
    r = requests.get(f"https://tonapi.io/v2/accounts/{address}/nfts?collection=EQA4SnGyqOHqI01xDKHalYYF_o-ELlxUyBVcMkhG-MSEOnLm&limit=1000&offset=0&indirect_ownership=false")
    results = {}

    nfts = json.loads(r.text)["nft_items"]

    user_index = [nft["index"] for nft in nfts]

    users_nft_info = {nft["index"]: {"content": nft["metadata"]["content_url"], "address": nft["address"]} for nft in nfts}


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

    return JsonResponse({"data": results, "pieces": len(user_index)})
