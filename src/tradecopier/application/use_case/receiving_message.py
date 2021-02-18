import abc
from collections import defaultdict
from typing import Iterable, List, Tuple

from tradecopier.application.adapters.connection_adapter import \
    ConnectionHandlerAdapter
from tradecopier.application.domain.entities.message import (
    AskRegistrationMessage, IncomingMessage, InTradeMessage, OutgoingMessage,
    RegisterMessage)
from tradecopier.application.domain.entities.terminal import Terminal
from tradecopier.application.domain.value_objects import (
    CustomerType, EntityNotFoundException, TerminalId, TerminalType)
from tradecopier.application.repositories.route_repo import RouteRepo
from tradecopier.application.repositories.rule_repo import RuleRepo
from tradecopier.application.repositories.terminal_repo import TerminalRepo


class ReceivingMessageBoundary(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def present(self, reply: List[Tuple[Iterable[TerminalId], OutgoingMessage]]):
        pass


class ReceivingMessageUseCase:
    def __init__(
        self,
        *,
        conn_handler: ConnectionHandlerAdapter,
        route_repo: RouteRepo,
        terminal_repo: TerminalRepo,
        rule_repo: RuleRepo,
        outboundary: ReceivingMessageBoundary,
    ):
        self._conn_adapter = conn_handler
        self._route_repo = route_repo
        self._terminal_repo = terminal_repo
        self._rule_repo = rule_repo
        self._out_bound = outboundary

    def _register_msg_case(self, message: RegisterMessage):
        terminal = self._terminal_repo.get(message.terminal_id)
        if terminal is None:
            terminal = Terminal(
                terminal_id=message.terminal_id,
                name=message.name,
                broker=message.broker,
                customer_type=CustomerType.SILVER
                if message.is_cyphered
                else CustomerType.BRONZE,
            )
            self._terminal_repo.save(terminal)

    def _trade_msg_case(self, terminal: Terminal, message: InTradeMessage):
        # if someone wants to create DoS attack, he can create loop between 2 or
        # more terminals and drive trade around them
        src_terminal_id = message.terminal_id
        if terminal is None or not terminal.is_active:
            return
        routes = self._route_repo.get_by_terminal_id(
            src_terminal_id, term_type=TerminalType.SOURCE
        )
        if (src_rule := self._rule_repo.get_by_terminal_id(src_terminal_id)) is None:
            raise EntityNotFoundException(
                f"rule for terminal {src_terminal_id} not found"
            )
        if (src_msg := src_rule.apply(message)) is None:
            return
        destinations = set(
            [route.destination for route in routes if route.destination.is_active]
        )
        out_msgs = defaultdict(set)
        for dst_terminal in destinations:
            if not self._conn_adapter.is_connected(dst_terminal.terminal_id):
                continue
            dst_rule = self._rule_repo.get_by_terminal_id(dst_terminal.terminal_id)
            if not dst_rule:
                continue
            dst_msg = dst_rule.apply(src_msg)
            if dst_msg is not None:
                msg = OutgoingMessage(message=dst_msg)
                out_msgs[msg].add(dst_terminal.terminal_id)
        self._out_bound.present([(v, k) for k, v in out_msgs.items()])

    def execute(self, message: IncomingMessage):
        if (terminal := self._terminal_repo.get(message.message.terminal_id)) is None:
            if isinstance(message.message, RegisterMessage):
                self._register_msg_case(message.message)
            else:
                self._out_bound.present(
                    [
                        (
                            (message.message.terminal_id,),
                            OutgoingMessage(
                                message=AskRegistrationMessage(
                                    terminal_id=message.message.terminal_id,
                                )
                            ),
                        )
                    ]
                )
        else:
            if isinstance(message.message, InTradeMessage):
                self._trade_msg_case(terminal, message.message)
