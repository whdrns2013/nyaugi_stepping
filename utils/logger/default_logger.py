# import logging
# from logging.handlers import TimedRotatingFileHandler
# from core.enums import LogLevelType, LogWhen
# import os
# from core.settings import settings

# # logger
# class DefaultLogger():
    
#     def __init__(self,
#                  logger_log_level:LogLevelType = settings.LOGGING.LOGGER_LOG_LEVEL,
#                  file_log_level:LogLevelType = settings.LOGGING.FILE_LOG_LEVEL,
#                  console_log_level:LogLevelType = settings.LOGGING.CONSOLE_LOG_LEVEL,
#                  log_dir:str = settings.LOGGING.LOG_DIR,
#                  log_format:str = settings.LOGGING.LOG_FORMAT,
#                  when:LogWhen = settings.LOGGING.LOG_WHEN,
#                  interval:str|int = settings.LOGGING.LOG_INTERVAL,
#                  retention_period_day:str|int = settings.LOGGING.RETENTION_PERIOD_DAY
#                  ):
#         # logger
#         self.logger = None
#         # log level
#         self.logger_log_level = self._log_level_convert(logger_log_level)
#         self.file_log_level = self._log_level_convert(file_log_level)
#         self.console_log_level = self._log_level_convert(console_log_level)
#         # log dir
#         self.log_dir = log_dir
#         # log format
#         self.log_format = log_format
#         # file ratating setting
#         self.when = when
#         self.interval = int(interval)
#         # log file lifetime
#         self.retention_period_day = int(retention_period_day)
    
#     def _log_level_convert(self, log_level:LogLevelType):
#         return logging._nameToLevel[log_level]
    
#     def check_log_dir(self, log_dir):
#         if not os.path.exists(log_dir):
#             os.makedirs(log_dir)
    
#     def get_logger(self, logger_name:str=settings.LOGGING.LOGGER_NAME,
#                    file_name:str=settings.LOGGING.LOG_FILE_NAME,
#                    encoding:str="utf-8"):
        
#         self.logger = logging.getLogger(logger_name)
#         self.logger.setLevel(self.logger_log_level)
#         self.logger.propagate = False
        
#         # remove existing handlers
#         if self.logger.hasHandlers():
#             self.logger.handlers.clear()
        
#         # setting log_dir path and retention period
#         filename = os.path.join(self.log_dir, file_name)
#         backup_count = 90
#         if self.when == "D":
#             backup_count = int(self.retention_period_day / self.interval)
#         elif self.when == "H":
#             backup_count = int(self.retention_period_day * 24 / self.interval)
#         elif self.when == "M":
#             backup_count = int(self.retention_period_day * 24 * 60 / self.interval)
#         elif self.when == "S":
#             backup_count = int(self.retention_period_day * 24 * 60 * 60 / self.interval)
        
#         # check log dir
#         self.check_log_dir(self.log_dir)
        
#         # handler
#         file_handler = TimedRotatingFileHandler(filename=filename,
#                                                 backupCount=backup_count,
#                                                 encoding=encoding,
#                                                 when=self.when,
#                                                 interval=self.interval)
#         console_handler = logging.StreamHandler()
#         file_handler.setLevel(self.file_log_level)
#         console_handler.setLevel(self.console_log_level)
        
#         # formatter
#         formatter = logging.Formatter(fmt=self.log_format)
#         file_handler.setFormatter(formatter)
#         console_handler.setFormatter(formatter)
        
#         # return logger
#         self.logger.addHandler(file_handler)
#         self.logger.addHandler(console_handler)
        
#         return self.logger

# config = DefaultLogger()
# logger = config.get_logger()

# """
# usage
# # usage(1) : 기본 로깅 설정으로 간편하게
# from logger.default_logger import logger
# logger.info("abc")

# # usage(2) : 로깅 설정 커스텀
# from logger.default_logger import DefaultLogger
# config = DefaultLogger(설정 커스텀...)
# logger = config.get_logger(logger_name, file_name)
# logger.info("abc")

# # logger 사용법
# # DEBUG < INFO < WARNING < ERROR ==> 해당 레벨 이상의 로그만 로깅됨
# logger.debug("message")   : DEBUG 레벨의 메시지를 로깅
# logger.info("message")    : INFO 레벨의 메시지를 로깅
# logger.warning("message") : WARNING 레벨의 메시지를 로깅
# logger.error("message")   : ERROR 레벨의 메시지를 로깅

# """