from django.shortcuts import render, redirect
from .tasks import deploy
from .models import Wallet, Word
from random import randint

datas = ['https://gateway.irys.xyz/nG8TR8NKBZ0Cqj1BQ16zY0EXar58VbZr-DV_28-0vzI', 'https://gateway.irys.xyz/GMezoftxgRuyPc4wKlos9V0pseP4LeDNHDqgPnM7fHs', 'https://gateway.irys.xyz/QjAVeDozR5ONOSzbR-Q_Oajb1f__Qj6cv9GUILOTRqo', 'https://gateway.irys.xyz/aRU1b8_lgf5BkCFDnxnEWmS3uRxkcQ6uIgizrAn8dIs', 'https://gateway.irys.xyz/mzvC9BMbjN4CK7niJohdGWJBAkQuIMH6OyHtFkWkdAY', 'https://gateway.irys.xyz/VCwX34pI4_1d3Ma32n7rVsmQs_REWKAsl1zSydo7a_I', 'https://gateway.irys.xyz/kdENR7zOMX6bdpHkWdkBep5rEsWgL7iNjNaZGCyeBsk', 'https://gateway.irys.xyz/kwiOxmojdmtPbyTasHLmU-mFZL4Up65kzR5hCGTBsQI', 'https://gateway.irys.xyz/RkTXtsK8A3MStPgcV1Pz2ziAWP5xInjgN8x4cYiJIJM', 'https://gateway.irys.xyz/xaCPdPBDLATirfAUvFTEWqBt8Oqih2EJLRdMg_TgRSA', 'https://gateway.irys.xyz/DkmiB4SYHU__MIqnPJUIsuvL_IIip8o5v3P4_Nr13Pw', 'https://gateway.irys.xyz/YAAFnkCDB3Jh3T3NQT_H89wxi3ETkgsGdQUX_ZdrgZk', 'https://gateway.irys.xyz/YhmkOc4bz86EFJ4D1QaMresQHYQ5Xs_-A5ZPYFkP5lo', 'https://gateway.irys.xyz/a6U8JZYATlZrkmkCS_kehTr2fDe2NX0jbJMoizDZI7s', 'https://gateway.irys.xyz/KML2EPZJfbscMrpj8sL74b36JTmgpj3jgIiN_wGWxYo', 'https://gateway.irys.xyz/ICTHwS2VxzNxFDE05xShRkC6cFc__to_pfUJyv0vUHE', 'https://gateway.irys.xyz/OocPeaylPnRoHb4Ku_Ly7fGkMqXBKudei2ZIPt8nK0g', 'https://gateway.irys.xyz/zVR-wvHeZkuyYQnsx_G6ynrQgU8eexlFeSXytM_gmYU', 'https://gateway.irys.xyz/qolJg5sc3ME_7_oMi8YVo1FwxZKbwoBjT2Bv44cHTq8', 'https://gateway.irys.xyz/e60W0Tf1surpexb8H3qJBJQiqNEBZLlBsimAb-z8vX4', 'https://gateway.irys.xyz/bPafwuEp02l3IpXpfmJYu_0IOuGnRrKowIQ-9POl0Ic', 'https://gateway.irys.xyz/26Fq42PkzJXQ0EjsJNP24VXynOUEYsG4dQfVfy2gQZ4', 'https://gateway.irys.xyz/Ng4RMl5qNtPA8PsSH9ZPA6q9_XWQE68BsyZVkfSXN18', 'https://gateway.irys.xyz/O27v5Kam3WB8wRJEZl6JCRHkkXk1YeNMvnTPc9eIbpo']



def index(request):
    return render(request, "wallet.html", {"wallets": Wallet.objects.all().order_by("id")})


def mint(request):
    if request.method == "POST":
        words = Word.objects.filter(index = None)  & Word.objects.filter(stage = 1)
        if len(words) == 0:
            words = Word.objects.filter(index = None)  & Word.objects.filter(stage = 2)
        if len(words) == 0:
            words = Word.objects.filter(index = None)  & Word.objects.filter(stage = 3)
        tasks = []
        index = 13824 - len(words)
        for i in range(int(request.POST["quantity"])):
            word = words[randint(0, len(words)-1)]
            tasks.append({'index': index, 'content': datas[word.wallet_id-1], 'address': request.POST["address"]})
            word.index = index
            word.save()
            index -= 1

        deploy.delay(tasks)
        
        

        return redirect(tickets)
            

    words = Word.objects.filter(index = None)
    return render(request, "buy.html", {"words_quantity": len(words)})


def tickets(request):
    return render(request, "tickets.html")