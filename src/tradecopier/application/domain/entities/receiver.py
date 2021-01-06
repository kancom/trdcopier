from collections import defaultdict
from datetime import datetime
from typing import Mapping
from uuid import UUID

from domain.entities.customer import Customer
from pydantic import BaseModel, Field


class AddressEntry(BaseModel):
    customer: Customer
    updated_at: datetime = datetime.now()


class Receiver(BaseModel):
    routing_table: Mapping[UUID, AddressEntry] = defaultdict(AddressEntry)

    def add_entry(self, uuid: UUID, customer: Customer):
        assert uuid not in self.routing_table, "uuid is already routed"
        self.routing_table[uuid].customer = customer

    def get_customer(self, uuid: UUID) -> Customer:
        return self.routing_table.get(uuid).customer

    def is_routed(self, uuid: UUID) -> bool:
        return uuid in self.routing_table

    def remove_entry(self, uuid: UUID):
        assert uuid in self.routing_table, "uuid is not found"
        del self.routing_table[uuid]

    def update_entry_ts(self, uuid: UUID):
        assert uuid in self.routing_table, "uuid is not found"
        self.routing_table[uuid].updated_at = datetime.now()
