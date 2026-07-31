from __future__ import annotations

import pathlib
import typing

import annotated_types
import pydantic

from datamodel import unittests_nested
from utils import util_pydantic

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).parent


def walk_model_paths_(model: object, prefix: str = "") -> None:
    print(f"**** {model.Title} ***")
    if not hasattr(model, "model_fields"):
        print(prefix)
        return

    for field_name in model.model_fields:
        value = getattr(model, field_name)
        path = f"{prefix}/{field_name}"
        walk_model_paths(value, path)


def walk_model_paths(model: pydantic.BaseModel, prefix: str = "") -> None:
    assert issubclass(model, pydantic.BaseModel)

    for field_name, field_info in model.model_fields.items():
        path = f"{prefix}/{field_name}"
        annotation = field_info.annotation
        if (annotation is list) or (typing.get_origin(annotation) is list):

            def get_annotation[T: annotated_types.BaseMetadata](
                annotated_type: type[T],
            ) -> T:
                for j in field_info.metadata:
                    if isinstance(j, annotated_type):
                        return j
                raise NotImplementedError()

            min_length = get_annotation(annotated_types.MinLen).min_length
            max_length = get_annotation(annotated_types.MaxLen).max_length
            assert min_length == max_length
            (item_type,) = typing.get_args(
                annotation
            )  # -> datamodel.unittests_simple.ModelPidController
            for i in range(min_length):
                walk_model_paths(item_type, f"{path}/{i}")
            continue
        if issubclass(annotation, pydantic.BaseModel):
            walk_model_paths(annotation, path)
            continue
        print(path)


def test_datamodel_nested_dual() -> None:
    model_dual = unittests_nested.ModelSystemDual()
    model_dual.first.i_param = 5
    (DIRECTORY_OF_THIS_FILE / "schema_model_dual.py").write_text(
        repr(model_dual.model_json_schema())
    )
    print(model_dual.model_json_schema())

    print("*******")
    walk_model_paths(model=unittests_nested.ModelSystemDual)
    print("+++")
    pass


class ModelHierarchy(dict[str, util_pydantic.FieldInfoIter]):
    @staticmethod
    def factory(model: pydantic.BaseModel) -> ModelHierarchy:
        mh = ModelHierarchy()

        def walk_model_paths(model: pydantic.BaseModel, prefix: str = "") -> None:
            assert issubclass(model, pydantic.BaseModel)

            for field in util_pydantic.FieldInfoIter.iter_model(model):
                path = f"{prefix}/{field.field_name}"
                annotation = field.field_info.annotation
                if (annotation is list) or (typing.get_origin(annotation) is list):

                    def get_annotation[T: annotated_types.BaseMetadata](
                        annotated_type: type[T],
                    ) -> T:
                        for j in field.field_info.metadata:
                            if isinstance(j, annotated_type):
                                return j
                        raise NotImplementedError()

                    min_length = get_annotation(annotated_types.MinLen).min_length
                    max_length = get_annotation(annotated_types.MaxLen).max_length
                    assert min_length == max_length
                    (item_type,) = typing.get_args(
                        annotation
                    )  # -> datamodel.unittests_simple.ModelPidController
                    for i in range(min_length):
                        walk_model_paths(item_type, f"{path}/{i}")
                    continue
                if issubclass(field.field_info.annotation, pydantic.BaseModel):
                    walk_model_paths(field.field_info.annotation, path)
                    continue
                mh[path] = field

        walk_model_paths(model=model)

        return mh


def test_datamodel_nested_list() -> None:
    model_list = unittests_nested.ModelSystemList()
    (DIRECTORY_OF_THIS_FILE / "schema_model_list.py").write_text(
        repr(model_list.model_json_schema())
    )
    mh = ModelHierarchy.factory(model=unittests_nested.ModelSystemList)

    print("*******")
    walk_model_paths(unittests_nested.ModelSystemList)
    print("+++")
    pass
