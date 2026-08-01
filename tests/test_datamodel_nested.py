from __future__ import annotations

import pathlib
import typing

import annotated_types
import pydantic
from utils import util_pydantic
from datamodel import unittests_nested

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).parent

def test_datamodel_nested_dual() -> None:
    model_dual = unittests_nested.ModelSystemDual()
    model_dual.first.i_param = 5
    (DIRECTORY_OF_THIS_FILE / "schema_model_dual.py").write_text(
        repr(model_dual.model_json_schema())
    )
    print(model_dual.model_json_schema())

    print("*******")
    mh = util_pydantic. ModelHierarchy.factory(model=unittests_nested.ModelSystemDual)
    mh.dump()
    print("+++")
    pass



def test_datamodel_nested_list() -> None:
    model_list = unittests_nested.ModelSystemList()
    (DIRECTORY_OF_THIS_FILE / "schema_model_list.py").write_text(
        repr(model_list.model_json_schema())
    )

    print("*******")
    mh =util_pydantic. ModelHierarchy.factory(model=unittests_nested.ModelSystemList)
    mh.dump()
    print("+++")
    pass
