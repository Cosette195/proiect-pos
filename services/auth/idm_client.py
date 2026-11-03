import grpc
import IDM_pb2
import IDM_pb2_grpc
import os


class IDMClient:

    def __init__(self, address = None, timeout = 5):
        if address is None:
            address = os.environ.get("IDM_ADDRESS", "127.0.0.1:50051")
        self.channel = grpc.insecure_channel(address)
        self.stub = IDM_pb2_grpc.IDMStub(self.channel)
        self.timeout = timeout

    def auth(self, username, password):
        request = IDM_pb2.AuthRequest(username = username, password = password)
        response = self.stub.Auth(request, timeout = self.timeout)
        return response.token

    def list_accounts(self, token):
        request = IDM_pb2.ListRequest(token = token)
        response = self.stub.ListAccounts(request, timeout = self.timeout)
        accounts = []
        for account in response.accounts:
            accounts.append({"uid": account.uid, "username": account.username,
                             "role": account.role, "is_active": account.is_active})
        return accounts

    def create_account(self, token, username, role):
        request = IDM_pb2.CreateRequest(token = token, username = username, role = role)
        response = self.stub.CreateAccount(request, timeout = self.timeout)
        return response.success

    def deactivate_account(self, token, username):
        request = IDM_pb2.DeactivateRequest(token = token, username = username)
        response = self.stub.DeactivAccount(request, timeout = self.timeout)
        return response.success

    def activate_account(self, username, password):
        request = IDM_pb2.ActivateRequest(username = username, password = password)
        response = self.stub.ActivateAccount(request, timeout = self.timeout)
        return response.success

    def validate_token(self, token):
        request = IDM_pb2.ValidRequest(token = token)
        response = self.stub.ValidToken(request, timeout = self.timeout)
        return response.sub, response.role

    def delete_token(self, token):
        request = IDM_pb2.DelRequest(token = token)
        response = self.stub.DelToken(request, timeout = self.timeout)
        return response.success

    def close(self):
        self.channel.close()