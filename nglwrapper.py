# coding=utf-8
"""
Ngl wrapper module.
"""
from cloudscraper import create_scraper
from colorama import Style, Fore
from uuid import uuid4


class NGLWrapper(object):
    """
    NGLWrapper class.
    """

    def __init__(self, username='', timeout=0):
        """
        :param username: str | unicode
        :param timeout: int
        """
        self.__scrapper = create_scraper()  # type CloudScraper
        # self.__scrapper.ssl_context = create_default_context(Purpose.SERVER_AUTH, cafile=where(), capath=None)
        # self.__scrapper.verify = False  # Bypasses the SSL verification check.
        self.__submitUrl = 'https://ngl.link/api/submit'  # type: str
        self.__username = username  # type: str
        self.__timeout = timeout  # type: int
        self.__counter = 0  # type: int

    @staticmethod
    def error(message):
        """
        :param message: str | unicode
        :return:
        """
        print(Fore.RED + message + Style.RESET_ALL)

    @staticmethod
    def success(message):
        """
        :param message: str | unicode
        :return:
        """
        print(Fore.GREEN + message + Style.RESET_ALL)

    @staticmethod
    def info(message):
        """
        :param message: str | unicode
        :return:
        """
        print(Fore.BLUE + message + Style.RESET_ALL)

    def setUsername(self, username):
        """
        :param username: str | unicode
        :return:
        """
        self.__username = username  # type: str

    def username(self):
        """
        :return: str | unicode
        """
        return self.__username

    def setTimeout(self, timeout):
        """
        :param timeout: int
        :return:
        """
        self.__timeout = timeout  # type: int

    def timeout(self):
        """
        :return: int
        """
        return self.__timeout

    def sendQuestion(self, question):
        """
        :param question: str | unicode
        :return: bool
        """
        if not self.__username:
            self.error('You must set a username before sending a question.')
            return False
        if self.__timeout:
            r = self.__scrapper.post(
                self.__submitUrl, data={
                    'username': self.__username, 'question': question, 'deviceId': uuid4().__str__(), 'gameSlug': '',
                    'referrer': ''}, timeout=self.__timeout)
        else:
            r = self.__scrapper.post(
                self.__submitUrl, data={
                    'username': self.__username, 'question': question, 'deviceId': uuid4().__str__(), 'gameSlug': '',
                    'referrer': ''})
        if r.status_code == 200:
            self.__counter += 1
            self.success("[{}] Question sent! Question: {}".format(self.__counter, question))
            return True
        self.error('Error sending question. Status code: {}'.format(r.status_code))
        self.error('Text: {}'.format(r.text))
        return False

    def isValidUser(self, vicName=''):
        """
        :param vicName: str | unicode
        :return: bool
        """
        if not vicName:
            vicName = self.__username  # type: str
        # Navigate to ngl.link sent to load cookies.
        response = self.__scrapper.get('https://ngl.link/{}'.format(vicName))
        return response.status_code != 404
