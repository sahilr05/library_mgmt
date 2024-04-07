from datetime import datetime

from django.db import models

from .types import CirculationStatus
from .types import ReservationStatus
from .types import states_as_list


class BaseModel(models.Model):
    """
    Base model for all models in the application.

    Attributes:
        created_at (datetime): The datetime when the object was created.
        modified_at (datetime): The datetime when the object was last modified.
    """

    created_at: datetime = models.DateTimeField(auto_now_add=True)
    modified_at: datetime = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Books(BaseModel):
    book_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    copies = models.IntegerField()


class Members(BaseModel):
    member_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200)


class Circulation(BaseModel):
    book = models.ForeignKey(
        Books, related_name="circulation_book", on_delete=models.CASCADE
    )
    member = models.ForeignKey(
        Members, related_name="circulation_member", on_delete=models.CASCADE
    )
    status = models.CharField(choices=states_as_list(CirculationStatus), max_length=50)
    issued_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        index_together = [["book", "member", "status"]]


class Reservation(BaseModel):
    book = models.ForeignKey(
        Books, related_name="reservation_book", on_delete=models.CASCADE
    )
    member = models.ForeignKey(
        Members, related_name="reservation_member", on_delete=models.CASCADE
    )
    status = models.CharField(choices=states_as_list(ReservationStatus), max_length=50)
    reserved_at = models.DateTimeField(auto_now_add=True, db_index=True)
    fulfilled_at = models.DateTimeField(null=True, blank=True)
