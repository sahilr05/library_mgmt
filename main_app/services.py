from datetime import datetime

import environ
from django.core.cache import cache
from django.db import transaction
from django.db.models import F
from django_redis import get_redis_connection

from .models import Books
from .models import Circulation
from .models import Reservation
from .types import CirculationStatus
from .types import ReservationStatus
from library_mgmt.exception import ValidationException

env = environ.Env()
environ.Env.read_env()

con = get_redis_connection("default")
cache_timeout = 60 * 60


@transaction.atomic
def checkout_book(*, book_id: int, member_id: int) -> Circulation:
    validate_user_issued_already(book_id=book_id, member_id=member_id)
    if not is_book_available(book_id=book_id):
        raise ValidationException("Book is not available, reserve it instead")
    decrement_book_qty(book_id=book_id)
    cache_key = f"{book_id}-{member_id}-issued"
    cache.set(cache_key, 1, timeout=60 * 60)
    return Circulation.objects.create(
        book_id=book_id, member_id=member_id, status=CirculationStatus.CHECKOUT
    )


@transaction.atomic
def return_book(
    *,
    circulation_id: int,
    book_id: int,
    member_id: int,
):
    validate_book_checkout(
        book_id=book_id, member_id=member_id, circulation_id=circulation_id
    )
    increment_book_qty(book_id=book_id)
    circulation_obj = Circulation.objects.get(id=circulation_id)
    circulation_obj.status = CirculationStatus.RETURN
    circulation_obj.returned_at = datetime.now()
    circulation_obj.save()


@transaction.atomic
def reserve_book(
    book_id: int,
    member_id: int,
) -> Reservation:
    validate_user_issued_already(book_id=book_id, member_id=member_id)
    validate_user_reserved_already(book_id=book_id, member_id=member_id)
    if is_book_available(book_id=book_id):
        raise ValidationException("Book is available to checkout")
    cache_key = f"{book_id}-{member_id}-reserved"
    cache.set(cache_key, 1, timeout=60 * 60)
    return Reservation.objects.create(
        book_id=book_id, member_id=member_id, status=ReservationStatus.RESERVED
    )


@transaction.atomic
def fulfill_book(
    book_id: int,
):
    book_copies = is_book_available(book_id=book_id)
    if not book_copies:
        raise ValidationException("Book is not available to fulfill")

    latest_reservation = (
        Reservation.objects.filter(book_id=book_id).order_by("reserved_at").first()
    )

    latest_reservation.status = ReservationStatus.FULFILLED
    latest_reservation.fulfilled_at = datetime.now()
    latest_reservation.save()
    decrement_book_qty(book_id=book_id)
    return Circulation.objects.create(
        book_id=book_id,
        member_id=latest_reservation.member_id,
        status=CirculationStatus.CHECKOUT,
    )


def validate_user_issued_already(*, book_id, member_id):
    cache_key = f"{book_id}-{member_id}-issued"
    data = cache.get(cache_key)
    if data:
        raise ValidationException("You've already issued this book")
    if circulation_obj := Circulation.objects.filter(
        book_id=book_id, member_id=member_id, status=CirculationStatus.CHECKOUT
    ):
        cache.set(cache_key, circulation_obj.count(), timeout=cache_timeout)
        raise ValidationException("You've already issued this book")


def validate_user_reserved_already(*, book_id, member_id):
    cache_key = f"{book_id}-{member_id}-reserved"
    data = cache.get(cache_key)
    if data:
        raise ValidationException("You've already reserved this book")

    if reservation_obj := Reservation.objects.filter(
        book_id=book_id, member_id=member_id, status=ReservationStatus.RESERVED
    ):
        cache.set(cache_key, reservation_obj.count(), timeout=cache_timeout)
        raise ValidationException("You've already reserved this book")


def is_book_available(*, book_id):
    cache_key = f"{book_id}-count"
    if data := cache.get(cache_key):
        return data
    book = Books.objects.get(book_id=book_id)
    book_copies = book.copies
    cache.set(cache_key, book_copies, timeout=60 * 60)
    return book_copies


def validate_book_checkout(*, book_id, member_id, circulation_id):
    circulation_obj = Circulation.objects.get(
        id=circulation_id,
    )
    if circulation_obj.status == CirculationStatus.RETURN:
        raise ValidationException("Book is already returned")

    if circulation_obj.book_id != book_id or circulation_obj.member_id != member_id:
        raise ValidationException("Invalid book <> member checkout")


def increment_book_qty(*, book_id):
    cache_key = f"{book_id}-count"
    Books.objects.filter(book_id=book_id).update(copies=F("copies") + 1)
    cache.delete(cache_key)


def decrement_book_qty(*, book_id):
    cache_key = f"{book_id}-count"
    Books.objects.filter(book_id=book_id).update(copies=F("copies") - 1)
    cache.delete(cache_key)
