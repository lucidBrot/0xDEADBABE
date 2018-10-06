import grpc
from flask import current_app
import people_pb2 as people



def login (username, password):
    channel = grpc.insecure_channel("{}:{}".format(
        current_app.config["PEOPLE_API_URL"],          
        current_app.config["PEOPLE_API_PORT"]         
    ))
    
    client = people.PeopleStub(channel)
    metadata = (('authorization', current_app.config["PEOPLE_API_KEY"]),)
    request = people.AuthPersonRequest(username=username, password=password)
    try:
        res = client.AuthEthPerson(request=request, metadata=metadata)
        return res.ok        
    except grpc.RpcError as e:
        if e.code() is grpc.StatusCode.INVALID_ARGUMENT:
            return False
        raise e