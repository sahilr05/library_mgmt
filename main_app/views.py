from rest_framework import serializers
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from main_app import services


class CheckoutAPI(APIView):
    class InputSerializer(serializers.Serializer):
        book_id = serializers.IntegerField()
        member_id = serializers.IntegerField()

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        circulation_obj = services.checkout_book(**serializer.data)
        response = {"response": f"Your checkout_id: {circulation_obj.id}"}
        return Response(status=status.HTTP_201_CREATED, data=response)


class ReturnBookAPI(APIView):
    class InputSerializer(serializers.Serializer):
        circulation_id = serializers.IntegerField()
        book_id = serializers.IntegerField()
        member_id = serializers.IntegerField()

    def put(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.return_book(**serializer.data)
        return Response(status=status.HTTP_200_OK)


class ReserveBookAPI(APIView):
    class InputSerializer(serializers.Serializer):
        book_id = serializers.IntegerField()
        member_id = serializers.IntegerField()

    def post(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reservation_obj = services.reserve_book(**serializer.data)
        return Response(
            status=status.HTTP_201_CREATED,
            data={"response": f"Your reservation slot id: {reservation_obj.id}"},
        )


class FulfillBookAPI(APIView):
    class InputSerializer(serializers.Serializer):
        book_id = serializers.IntegerField()

    def put(self, request):
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        circulation_obj = services.fulfill_book(**serializer.data)
        response = {
            "data": f"Book request fulfilled for member :: {circulation_obj.member_id}"
        }
        return Response(status=status.HTTP_200_OK, data=response)
