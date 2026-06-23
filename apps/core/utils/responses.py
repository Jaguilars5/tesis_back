from rest_framework.response import Response
from rest_framework import status


def ok_response(data=None, msg="OK", status_code=status.HTTP_200_OK):
    return Response({"ok": True, "data": data, "msg": msg}, status=status_code)


def error_response(msg="Error", data=None, status_code=status.HTTP_400_BAD_REQUEST):
    return Response({"ok": False, "data": data, "msg": msg}, status=status_code)