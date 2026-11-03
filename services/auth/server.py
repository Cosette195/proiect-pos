import uuid
import grpc
from concurrent import futures
import IDM_pb2
import IDM_pb2_grpc
from database import db
from models import User
from passwords import hash_password, check_password
from jws import create_token, validate_token, blacklist_token
import os

ROLES = ("administrator", "maintainer")


class IDMService(IDM_pb2_grpc.IDMServicer):

    def check_admin(self, token, context):
        payload = validate_token(token)
        if payload is None:
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Token invalid")
        if payload["role"] != "administrator":
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Este necesar rolul de administrator")
        return payload

    def Auth(self, request, context):
        user = User.get_or_none(User.username == request.username)
        if user is None:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Nume de utilizator sau parola invalida")
        if not user.is_active:
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Contul nu este activ")
        if user.password is None or not check_password(request.password, user.password):
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Nume de utilizator sau parola invalida")

        token = create_token(str(user.uid), user.role)

        return IDM_pb2.AuthResponse(token = token)

    def ListAccounts(self, request, context):
        self.check_admin(request.token, context)

        accounts = []
        for user in User.select():
            accounts.append(IDM_pb2.Account(uid = str(user.uid), username = user.username,
                                            role = user.role, is_active = user.is_active))

        return IDM_pb2.ListResponse(accounts = accounts)

    def CreateAccount(self, request, context):
        self.check_admin(request.token, context)

        if not request.username:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Numele de utilizator lipseste")
        if request.role not in ROLES:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Rol invalid")
        if User.get_or_none(User.username == request.username) is not None:
            context.abort(grpc.StatusCode.ALREADY_EXISTS, "Numele de utilizator exista deja")

        User.create(uid = uuid.uuid7(), username = request.username, password = None,
                    role = request.role, is_active = False)

        return IDM_pb2.CreateResponse(success = True)

    def DeactivAccount(self, request, context):
        self.check_admin(request.token, context)

        if User.get_or_none(User.username == request.username) is None:
            context.abort(grpc.StatusCode.NOT_FOUND, "Contul nu exista")

        User.update(is_active = False).where(User.username == request.username).execute()

        return IDM_pb2.DeactivateResponse(success = True)

    def ActivateAccount(self, request, context):
        user = User.get_or_none(User.username == request.username)
        if user is None:
            context.abort(grpc.StatusCode.NOT_FOUND, "Contul nu exista")
        if user.is_active:
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Contul este deja activ")
        if user.password is not None:
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Parola este deja setata")
        if not request.password:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Parola lipseste")

        User.update(password = hash_password(request.password),
                    is_active = True).where(User.username == request.username).execute()

        return IDM_pb2.ActivateResponse(success = True)

    def ValidToken(self, request, context):
        payload = validate_token(request.token)
        if payload is None:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Token invalid sau expirat")

        return IDM_pb2.ValidResponse(sub = payload["sub"], role = payload["role"])

    def DelToken(self, request, context):
        payload = validate_token(request.token)
        if payload is None:
            context.abort(grpc.StatusCode.UNAUTHENTICATED, "Token invalid sau expirat")

        blacklist_token(request.token)

        return IDM_pb2.DelResponse(success = True)


def serve():
    db.connect()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    IDM_pb2_grpc.add_IDMServicer_to_server(IDMService(), server)

    listen_address = os.environ.get("IDM_LISTEN", "127.0.0.1:50051")
    server.add_insecure_port(listen_address)

    server.start()

    print("IDM gRPC server started")
    print("Listening on", listen_address)

    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Shutting down server...")
        server.stop(grace = 2).wait()

if __name__ == "__main__":
    serve()