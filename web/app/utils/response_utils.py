# app/utils/response_utils.py

def response_dict(status, message, data):
    return {
        'status': status,
        'message': message,
        'data': data
    }