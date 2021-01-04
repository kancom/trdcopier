import itertools
from typing import Optional

from domain.entities.customer import Customer
from domain.entities.terminal import Terminal
from domain.value_objects import AccountId, CustomerId
from infrastructure.repositories.sql_model import (CustomerModel,
                                                   TerminalModel,
                                                   TerminalToCustomerMap)
from sqlalchemy import and_, select
from sqlalchemy.engine import Connection
from sqlalchemy.sql import functions

from repositories.customer_repo import CustomerRepo


class SqlAlchemyCustomerRepo(CustomerRepo):
    def __init__(self, conn: Connection):
        self._conn = conn

    def get(self, customer_id: CustomerId) -> Optional[Customer]:
        db_customer = self._conn.execute(
            CustomerModel.select().where(CustomerModel.c.id == customer_id)
        ).first()
        if not db_customer:
            return None
        customer_dc = Customer(**{k: v for k, v in db_customer._mapping.items()})
        if db_customer.sources_mapping_id is not None:
            terminals = self._conn.execute(
                TerminalModel.select(
                    whereclause=and_(
                        TerminalModel.c.id == TerminalToCustomerMap.c.terminal_id,
                        TerminalToCustomerMap.c.mapping_id
                        == db_customer.sources_mapping_id,
                    )
                )
            ).fetchall()
            for terminal in terminals:
                customer_dc.sources.append(
                    Terminal(**{k: v for k, v in terminal._mapping.items()})
                )
        if db_customer.destinations_mapping_id is not None:
            terminals = self._conn.execute(
                TerminalModel.select(
                    whereclause=and_(
                        TerminalModel.c.id == TerminalToCustomerMap.c.terminal_id,
                        TerminalToCustomerMap.c.mapping_id
                        == db_customer.destinations_mapping_id,
                    )
                )
            ).fetchall()
            for terminal in terminals:
                customer_dc.destinations.append(
                    Terminal(**{k: v for k, v in terminal._mapping.items()})
                )
        return customer_dc

    def get_by_account(self, account_id: AccountId) -> Optional[Customer]:
        db_customer = self._conn.execute(
            CustomerModel.select().where(CustomerModel.c.account_id == account_id)
        ).first()
        if not db_customer:
            return None
        return self.get(db_customer.id)

    def save(self, customer: Customer):
        def update_TTSM(mapping_id, terminal_id, customer_id, set_col):
            self._conn.execute(
                TerminalToCustomerMap.insert(
                    values={
                        TerminalToCustomerMap.c.mapping_id: mapping_id,
                        TerminalToCustomerMap.c.terminal_id: terminal_id,
                        TerminalToCustomerMap.c.customer_id: customer_id,
                    }
                )
            )
            self._conn.execute(
                CustomerModel.update(
                    whereclause=CustomerModel.c.id == customer_id,
                    values={set_col: mapping_id},
                )
            )

        def get_current_mapping_id(curr_id, terminal_id, customer_id):
            if curr_id is None:
                curr_id = self._conn.execute(
                    select(
                        whereclause=and_(
                            TerminalToCustomerMap.c.terminal_id == terminal_id,
                            TerminalToCustomerMap.c.customer_id == customer_id,
                        ),
                        columns=[TerminalToCustomerMap.c.mapping_id],
                    )
                ).first()
                if curr_id is None:
                    (curr_id,) = self._conn.execute(
                        select(
                            columns=[functions.max(TerminalToCustomerMap.c.mapping_id)]
                        )
                    ).first()
                if curr_id is None:
                    curr_id = 1
                else:
                    if not isinstance(curr_id, int):
                        curr_id = curr_id[0]
                    curr_id += 1
            return curr_id

        def get_customer_id(customer_id):
            resulting_cust_id = None
            if customer_id is not None:
                resulting_cust_id = self._conn.execute(
                    select(
                        whereclause=CustomerModel.c.id == customer_id,
                        columns=[CustomerModel.c.id],
                    )
                ).first()
            if resulting_cust_id is None:
                cust_dict = customer.dict()
                del cust_dict["destinations"]
                del cust_dict["sources"]
                insert_res = self._conn.execute(CustomerModel.insert(values=cust_dict))
                resulting_cust_id = insert_res.lastrowid
            else:
                resulting_cust_id = resulting_cust_id[0]
            return resulting_cust_id

        resulting_cust_id = get_customer_id(customer.id)

        curr_id = None
        for terminal in customer.sources:
            curr_id = get_current_mapping_id(curr_id, terminal.id, customer.id)
            update_TTSM(
                curr_id, terminal.id, customer.id, CustomerModel.c.sources_mapping_id
            )
        curr_id = None
        for terminal in customer.destinations:
            curr_id = get_current_mapping_id(curr_id, terminal.id, customer.id)
            update_TTSM(
                curr_id,
                terminal.id,
                customer.id,
                CustomerModel.c.destinations_mapping_id,
            )
        return resulting_cust_id
