
from django.db import models
from django_mongodb_backend.fields import ObjectIdAutoField


class Service(models.Model):
    id = ObjectIdAutoField(primary_key=True)

    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    price_cents = models.PositiveIntegerField()
    duration_minutes = models.PositiveIntegerField(default=30)

    class Meta:
        db_table = "services"

    def __str__(self):
        return self.name

    @property
    def price_dollars(self):
        return self.price_cents / 100
