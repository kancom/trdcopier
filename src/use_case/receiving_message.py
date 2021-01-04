import abc

from adapters.connection_adapter import ConnectionHandlerAdapter
from domain.entities.customer import Customer
from domain.entities.message import (AskRegistrationMessage, IncomingMessage,
                                     OutgoingMessage, RegisterMessage,
                                     TradeMessage)
from domain.entities.terminal import Terminal
from domain.value_objects import CustomerType, EntityNotFoundException
from repositories.customer_repo import CustomerRepo
from repositories.rule_repo import RuleRepo
from repositories.terminal_repo import TerminalRepo


class ReceivingMessageOutputBoundary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def present(self, message: IncomingMessage):
        pass


class ReceivingMessageUseCase:
    def __init__(
        self,
        customer_repo: CustomerRepo,
        terminal_repo: TerminalRepo,
        rule_repo: RuleRepo,
        conn_handler: ConnectionHandlerAdapter,
    ):
        self._conn_adapter = conn_handler
        self._customer_repo = customer_repo
        self._terminal_repo = terminal_repo
        self._rule_repo = rule_repo

    def _register_msg_case(self, message: IncomingMessage):
        terminal = self._terminal_repo.get(message.message.terminal_id)
        customer = self._customer_repo.get_by_account(message.message.account_id)
        # both terminal and customer are new
        if terminal is None and customer is None:
            customer = Customer(
                account_id=message.message.account_id,
                customer_type=CustomerType.SILVER
                if message.message.is_cyphered
                else CustomerType.BRONZE,
            )
            customer_id = self._customer_repo.save(customer)
            terminal = Terminal(id=message.message.terminal_id, customer_id=customer_id)
            terminal_id = self._terminal_repo.save(terminal)
        # terminal is new, but account and consequently customer exists
        elif terminal is None:
            customer.customer_type = (
                CustomerType.SILVER
                if message.message.is_cyphered
                else CustomerType.BRONZE
            )
            customer_id = self._customer_repo.save(customer)
            terminal = Terminal(id=message.message.terminal_id, customer_id=customer_id)
            terminal_id = self._terminal_repo.save(terminal)
        # customer is new, but terminal exists and therefore bond to other customer
        elif customer is None:
            raise EntityNotFoundException(
                f"customer is new, but terminal {terminal.id} exists and therefore bond to other customer"
            )

    def _trade_msg_case(self, message: IncomingMessage):
        customer = self._customer_repo.get_by_account(message.message.account_id)
        if len(customer.destinations) == 0:
            return
        src_terminal_id = message.message.terminal_id
        if (src_rule := self._rule_repo.get_by_terminal_id(src_terminal_id)) is None:
            raise EntityNotFoundException(
                f"rule for terminal {src_terminal_id} not found"
            )

        if (src_msg := src_rule.apply(message)) is None:
            return
        for dst_terminal in customer.destinations:
            dst_rule = self._rule_repo.get_by_terminal_id(dst_terminal.id)
            dst_msg = dst_rule.apply(src_msg)
            if dst_msg is not None:
                self._conn_adapter.send_message(
                    dst_terminal.id, OutgoingMessage(message=dst_msg.message)
                )

    def execute(self, message: IncomingMessage):
        if self._conn_adapter.is_new_connection(message.message.terminal_id):
            if isinstance(message.message, RegisterMessage):
                self._register_msg_case(message)
            else:
                self._conn_adapter.send_message(
                    message.message.terminal_id,
                    OutgoingMessage(
                        message=AskRegistrationMessage(
                            terminal_id=message.message.terminal_id,
                        )
                    ),
                )
                self._conn_adapter.disconnect(message.message.terminal_id)
        else:
            if isinstance(message.message, TradeMessage):
                self._trade_msg_case(message)
