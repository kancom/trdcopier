from domain.entities.message import IncomingMessage
from use_case.receiving_message import ReceivingMessageOutputBoundary
from use_case.registering_terminal import RegisterTerminalUseCase


class RegisterPresenter(ReceivingMessageOutputBoundary):
    def __init__(self, uc: RegisterTerminalUseCase):
        self._uc = uc

    def present(self, message: IncomingMessage):
        print("registering", str(message))
        self._uc.execute(message)
