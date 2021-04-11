from . import errorhandler
from .constants import *
import requests

class RPCConnector():

    @staticmethod
    def request(endpoint, id, method, params):

        try:
            response = requests.post(
                endpoint, 
                json={
                    ID: id,
                    METHOD: method,
                    PARAMS: params,
                    JSON_RPC: JSON_RPC_VERSION
                }, 
                headers={
                    'Content-type': JSON_CONTENT_TYPE
                }
            )
        except Exception as e:
            raise errorhandler.BadRequestError("Request to client could not be completed: {}".format(str(e)))
        
        try:
            response = response.json()
        except Exception as e:
            raise errorhandler.InternalServerError("Json in client response is not supported: {}".format(str(e)))
        
        if ERROR in response and response[ERROR] is not None:
            raise errorhandler.BadRequestError("Exception occured in server: {}".format(str(response[ERROR])))
        
        return response[RESULT]