from django.contrib import admin
from .models import *


class WordInline(admin.StackedInline):
    model = Word
    extra = 0

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    inlines = [WordInline]
    list_display = ['id', 'address']


@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ['name', 'stage', 'index', 'wallet']