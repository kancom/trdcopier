from tradecopier.application import Order
from tradecopier.application.domain.value_objects import (
    type_filter_operation_map, type_transform_operation_map)
from tradecopier.restapi.dto.objects import PermittedRules


def test_permitted_rules():
    result = PermittedRules(
        transform_operation_map={
            f"{str(k)}:{int(k)}": [str(l) for l in v]
            for k, v in type_transform_operation_map.items()
        },
        filter_operation_map={
            str(k): [f"{str(l)}:{int(l)}" for l in v]
            for k, v in type_filter_operation_map.items()
        },
        fields=Order.get_field_type_mapping(),
        enums=Order.get_enums(),
    )
    assert result is not None
    assert "magic" not in result.fields
    assert "position" not in result.fields
    assert "position_by" not in result.fields
    assert result.fields["expiration"] == "float"
