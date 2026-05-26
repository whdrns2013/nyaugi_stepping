from abc import ABC, abstractmethod
from utils.tests.test_case import TestCase

@abstractmethod
class TestRunner(ABC):
    def run_tests(self, test_cases:list[TestCase]):
        results = [test_case().run() for test_case in test_cases]
        for result in results:
            print(result)
        success_message="모든 테스트가 완료되었습니다."
        print(success_message)
        

