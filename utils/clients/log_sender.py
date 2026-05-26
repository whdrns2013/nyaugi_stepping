# from core.settings import settings
# from clients import Requestor
# from schemas.client_log_sender import LogSenderRequest

# class LogSender:
#     def __init__(self):
#         self.api_url = settings.LOGGING.API_URL
#         self.method = "post"
#         self.component_name = settings.LOGGING.COMPONENT_NAME
#         self.log_level = settings.LOGGING.LOG_LEVEL
#         self.expire_day = settings.LOGGING.RETENTION_PERIOD
#         self.requestor = Requestor()    
    
#     def log_send(self, message:str):
#         headers = {"Content-Type" : "application/json"}
#         body = LogSenderRequest(
#             component_name = self.component_name,
#             log_message = message
#         )
#         response = self.requestor.request(url = self.api_url,
#                                      method = self.method,
#                                      headers = headers,
#                                      body = body.model_dump())
#         return response.json()