from configs import PASSWORD
from fastapi import HTTPException, Header
import jwt


def auth_middleware(x_auth_token = Header()):
    try:
        #get user token from the headers
        if not x_auth_token:
            # 401 is for authentication error
            raise HTTPException(401, 'No auth token, access denied!')
        # decode the token
        verified_token = jwt.decode(x_auth_token, PASSWORD, ['HS256'])
        
        # decide if it is a valid token (not tampered with)
        if not verified_token:
            raise HTTPException(401, 'Token verification failed, authorisation denied!')
        # get the id from the token (the payload)
        # get user information from postgresql database

        uid = verified_token.get('id')
        return {'uid': uid, 'token': x_auth_token}
    
    except jwt.PyJWTError:
        # entire app will crash without is if there is an invalid token
        raise HTTPException(401, 'Token is not valid, authorisation failed!')