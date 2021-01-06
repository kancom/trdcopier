import abc
from typing import Optional

from tradecopier.application.domain.entities.customer import Customer
from tradecopier.application.domain.value_objects import AccountId, CustomerId


class CustomerRepo(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get(self, customer_id: CustomerId) -> Optional[Customer]:
        pass

    @abc.abstractmethod
    def get_by_account(self, account_id: AccountId) -> Optional[Customer]:
        pass

    @abc.abstractmethod
    def save(self, customer: Customer) -> CustomerId:
        pass
