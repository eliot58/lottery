from django.db import models

class Wallet(models.Model):
    address = models.CharField(max_length = 300)
    prize = models.FloatField(null = True, blank = True)
    winner = models.CharField(max_length = 500, null = True, blank = True)

    class Meta:
        verbose_name = 'Кошелек'
        verbose_name_plural = 'Кошельки'

    def __str__(self):
        return self.address


class Word(models.Model):
    name = models.CharField(max_length = 20)
    index = models.PositiveIntegerField(null = True, blank = True, unique = True)
    wallet = models.ForeignKey(Wallet, on_delete = models.CASCADE)
    no = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Слово'
        verbose_name_plural = 'Слова'

    def __str__(self):
        return self.name
