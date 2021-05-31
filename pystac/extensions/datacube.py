"""Implements the Datacube extension.

https://github.com/stac-extensions/datacube
"""

from abc import ABC
from typing import Any, Dict, Generic, List, Optional, Set, TypeVar, Union, cast

from pydantic.tools import parse_obj_as

import pystac
from pystac.extensions.base import (
    ExtensionManagementMixin,
    PropertiesExtension,
)
from pystac.extensions.hooks import ExtensionHooks
from pystac.utils import get_required, map_opt

T = TypeVar("T", pystac.Collection, pystac.Item, pystac.Asset)

SCHEMA_URI = "https://stac-extensions.github.io/datacube/v1.0.0/schema.json"

DIMENSIONS_PROP = "cube:dimensions"
VARIABLES_PROP = "cube:variables"

# Dimension properties
DIM_TYPE_PROP = "type"
DIM_DESC_PROP = "description"
DIM_AXIS_PROP = "axis"
DIM_EXTENT_PROP = "extent"
DIM_VALUES_PROP = "values"
DIM_STEP_PROP = "step"
DIM_REF_SYS_PROP = "reference_system"
DIM_UNIT_PROP = "unit"

VAR_TYPE_PROP = "type"
VAR_DESC_PROP = "description"
VAR_DIMS_PROP = "dimensions"
VAR_VALUES_PROP = "values"
VAR_EXTENT_PROP = "extent"
VAR_STEP_PROP = "step"
VAR_UNIT_PROP = "unit"
VAR_SHAPE_PROP = "shape"
VAR_CHUNKS_PROP = "chunks"
VAR_ATTRS_PROP = "attrs"


class Dimension(ABC):
    def __init__(self, properties: Dict[str, Any]) -> None:
        self.properties = properties

    @property
    def dim_type(self) -> str:
        return get_required(
            self.properties.get(DIM_TYPE_PROP), "cube:dimension", DIM_TYPE_PROP
        )

    @dim_type.setter
    def dim_type(self, v: str) -> None:
        self.properties[DIM_TYPE_PROP] = v

    @property
    def description(self) -> Optional[str]:
        return self.properties.get(DIM_DESC_PROP)

    @description.setter
    def description(self, v: Optional[str]) -> None:
        if v is None:
            self.properties.pop(DIM_DESC_PROP, None)
        else:
            self.properties[DIM_DESC_PROP] = v

    def to_dict(self) -> Dict[str, Any]:
        return self.properties

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Dimension":
        dim_type = d.get(DIM_TYPE_PROP)
        if dim_type is None:
            raise pystac.RequiredPropertyMissing("cube_dimension", DIM_TYPE_PROP)
        if dim_type == "spatial":
            axis = d.get(DIM_AXIS_PROP)
            if axis is None:
                raise pystac.RequiredPropertyMissing("cube_dimension", DIM_AXIS_PROP)
            if axis == "z":
                return VerticalSpatialDimension(d)
            else:
                return HorizontalSpatialDimension(d)
        elif dim_type == "temporal":
            # The v1.0.0 spec says that AdditionalDimensions can have
            # type 'temporal', but it is unclear how to differentiate that
            # from a temporal dimension. Just key off of type for now.
            # See https://github.com/stac-extensions/datacube/issues/5
            return TemporalDimension(d)
        else:
            return AdditionalDimension(d)


class HorizontalSpatialDimension(Dimension):
    @property
    def axis(self) -> str:
        return get_required(
            self.properties.get(DIM_AXIS_PROP), "cube:dimension", DIM_AXIS_PROP
        )

    @axis.setter
    def axis(self, v: str) -> None:
        self.properties[DIM_TYPE_PROP] = v

    @property
    def extent(self) -> List[float]:
        return get_required(
            self.properties.get(DIM_EXTENT_PROP), "cube:dimension", DIM_EXTENT_PROP
        )

    @extent.setter
    def extent(self, v: List[float]) -> None:
        self.properties[DIM_EXTENT_PROP] = v

    @property
    def values(self) -> Optional[List[float]]:
        return self.properties.get(DIM_VALUES_PROP)

    @values.setter
    def values(self, v: Optional[List[float]]) -> None:
        if v is None:
            self.properties.pop(DIM_VALUES_PROP, None)
        else:
            self.properties[DIM_VALUES_PROP] = v

    @property
    def step(self) -> Optional[float]:
        return self.properties.get(DIM_STEP_PROP)

    @step.setter
    def step(self, v: Optional[float]) -> None:
        self.properties[DIM_STEP_PROP] = v

    def clear_step(self) -> None:
        """Setting step to None sets it to the null value,
        which means irregularly spaced steps. Use clear_step
        to remove it from the properties."""
        self.properties.pop(DIM_STEP_PROP, None)

    @property
    def reference_system(self) -> Optional[Union[str, float, Dict[str, Any]]]:
        return self.properties.get(DIM_REF_SYS_PROP)

    @reference_system.setter
    def reference_system(self, v: Optional[Union[str, float, Dict[str, Any]]]) -> None:
        if v is None:
            self.properties.pop(DIM_REF_SYS_PROP, None)
        else:
            self.properties[DIM_REF_SYS_PROP] = v


class VerticalSpatialDimension(Dimension):
    @property
    def axis(self) -> str:
        return get_required(
            self.properties.get(DIM_AXIS_PROP), "cube:dimension", DIM_AXIS_PROP
        )

    @axis.setter
    def axis(self, v: str) -> None:
        self.properties[DIM_TYPE_PROP] = v

    @property
    def extent(self) -> Optional[List[Optional[float]]]:
        return self.properties.get(DIM_EXTENT_PROP)

    @extent.setter
    def extent(self, v: Optional[List[Optional[float]]]) -> None:
        if v is None:
            self.properties.pop(DIM_EXTENT_PROP, None)
        else:
            self.properties[DIM_EXTENT_PROP] = v

    @property
    def values(self) -> Optional[Union[List[float], List[str]]]:
        return self.properties.get(DIM_VALUES_PROP)

    @values.setter
    def values(self, v: Optional[Union[List[float], List[str]]]) -> None:
        if v is None:
            self.properties.pop(DIM_VALUES_PROP, None)
        else:
            self.properties[DIM_VALUES_PROP] = v

    @property
    def step(self) -> Optional[float]:
        return self.properties.get(DIM_STEP_PROP)

    @step.setter
    def step(self, v: Optional[float]) -> None:
        self.properties[DIM_STEP_PROP] = v

    def clear_step(self) -> None:
        """Setting step to None sets it to the null value,
        which means irregularly spaced steps. Use clear_step
        to remove it from the properties."""
        self.properties.pop(DIM_STEP_PROP, None)

    @property
    def unit(self) -> Optional[str]:
        return self.properties.get(DIM_UNIT_PROP)

    @unit.setter
    def unit(self, v: Optional[str]) -> None:
        if v is None:
            self.properties.pop(DIM_UNIT_PROP, None)
        else:
            self.properties[DIM_UNIT_PROP] = v

    @property
    def reference_system(self) -> Optional[Union[str, float, Dict[str, Any]]]:
        return self.properties.get(DIM_REF_SYS_PROP)

    @reference_system.setter
    def reference_system(self, v: Optional[Union[str, float, Dict[str, Any]]]) -> None:
        if v is None:
            self.properties.pop(DIM_REF_SYS_PROP, None)
        else:
            self.properties[DIM_REF_SYS_PROP] = v


class TemporalDimension(Dimension):
    @property
    def extent(self) -> Optional[List[Optional[str]]]:
        return self.properties.get(DIM_EXTENT_PROP)

    @extent.setter
    def extent(self, v: Optional[List[Optional[str]]]) -> None:
        if v is None:
            self.properties.pop(DIM_EXTENT_PROP, None)
        else:
            self.properties[DIM_EXTENT_PROP] = v

    @property
    def values(self) -> Optional[List[str]]:
        return self.properties.get(DIM_VALUES_PROP)

    @values.setter
    def values(self, v: Optional[List[str]]) -> None:
        if v is None:
            self.properties.pop(DIM_VALUES_PROP, None)
        else:
            self.properties[DIM_VALUES_PROP] = v

    @property
    def step(self) -> Optional[str]:
        return self.properties.get(DIM_STEP_PROP)

    @step.setter
    def step(self, v: Optional[str]) -> None:
        self.properties[DIM_STEP_PROP] = v

    def clear_step(self) -> None:
        """Setting step to None sets it to the null value,
        which means irregularly spaced steps. Use clear_step
        to remove it from the properties."""
        self.properties.pop(DIM_STEP_PROP, None)


class AdditionalDimension(Dimension):
    @property
    def extent(self) -> Optional[List[Optional[float]]]:
        return self.properties.get(DIM_EXTENT_PROP)

    @extent.setter
    def extent(self, v: Optional[List[Optional[float]]]) -> None:
        if v is None:
            self.properties.pop(DIM_EXTENT_PROP, None)
        else:
            self.properties[DIM_EXTENT_PROP] = v

    @property
    def values(self) -> Optional[Union[List[str], List[float]]]:
        return self.properties.get(DIM_VALUES_PROP)

    @values.setter
    def values(self, v: Optional[Union[List[str], List[float]]]) -> None:
        if v is None:
            self.properties.pop(DIM_VALUES_PROP, None)
        else:
            self.properties[DIM_VALUES_PROP] = v

    @property
    def step(self) -> Optional[float]:
        return self.properties.get(DIM_STEP_PROP)

    @step.setter
    def step(self, v: Optional[float]) -> None:
        self.properties[DIM_STEP_PROP] = v

    def clear_step(self) -> None:
        """Setting step to None sets it to the null value,
        which means irregularly spaced steps. Use clear_step
        to remove it from the properties."""
        self.properties.pop(DIM_STEP_PROP, None)

    @property
    def unit(self) -> Optional[str]:
        return self.properties.get(DIM_UNIT_PROP)

    @unit.setter
    def unit(self, v: Optional[str]) -> None:
        if v is None:
            self.properties.pop(DIM_UNIT_PROP, None)
        else:
            self.properties[DIM_UNIT_PROP] = v

    @property
    def reference_system(self) -> Optional[Union[str, float, Dict[str, Any]]]:
        return self.properties.get(DIM_REF_SYS_PROP)

    @reference_system.setter
    def reference_system(self, v: Optional[Union[str, float, Dict[str, Any]]]) -> None:
        if v is None:
            self.properties.pop(DIM_REF_SYS_PROP, None)
        else:
            self.properties[DIM_REF_SYS_PROP] = v


class Variable:  # ABC?
    def __init__(self, properties: Dict[str, Any]) -> None:
        self.properties = properties

    @property
    def var_type(self) -> str:
        return get_required(
            self.properties.get(VAR_TYPE_PROP), "cube:variables", VAR_TYPE_PROP
        )

    @var_type.setter
    def var_type(self, v: str) -> None:
        self.properties[VAR_TYPE_PROP] = v

    @property
    def description(self) -> Optional[str]:
        return self.properties.get(VAR_DESC_PROP)

    @description.setter
    def description(self, v: Optional[str]) -> None:
        if v is None:
            self.properties.pop(VAR_DESC_PROP, None)
        else:
            self.properties[VAR_DESC_PROP] = v

    def to_dict(self) -> Dict[str, Any]:
        return self.properties

    @property
    def dimensions(self) -> List[Dimension]:
        return get_required(
            self.properties.get(VAR_DIMS_PROP, "cube:dimensions", VAR_DIMS_PROP)
        )

    @dimensions.setter
    def dimensions(self, v: List[Dimension]) -> None:
        self.properties[VAR_DIMS_PROP] = v

    @property
    def values(self):
        return self.properties.get(DIM_UNIT_PROP)

    @property
    def extent(self) -> Optional[List[Optional[Union[str, float]]]]:
        return self.properties.get(VAR_EXTENT_PROP)

    @extent.setter
    def extent(self, v: Optional[List[Optional[Union[str, float]]]]) -> None:
        if v is None:
            self.properties.pop(VAR_EXTENT_PROP, None)
        else:
            self.properties[VAR_EXTENT_PROP] = v

    @property
    def step(self) -> Optional[float]:
        return self.properties.get(VAR_STEP_PROP)

    @step.setter
    def step(self, v: Optional[float]) -> None:
        self.properties[VAR_STEP_PROP] = v

    @property
    def unit(self) -> Optional[str]:
        return self.properties.get(VAR_UNIT_PROP)

    @unit.setter
    def unit(self, v: Optional[str]) -> None:
        if v is None:
            self.properties.pop(VAR_UNIT_PROP, None)
        else:
            self.properties[VAR_UNIT_PROP] = v

    @property
    def shape(self) -> Optional[List[int]]:
        return self.properties.get(VAR_SHAPE_PROP)

    @shape.setter
    def shape(self, v: Optional[List[int]]) -> None:
        if v is None:
            self.properties.pop(VAR_SHAPE_PROP, None)
        else:
            self.properties[VAR_SHAPE_PROP] = v

    @property
    def chunks(self) -> Optional[List[int]]:
        return self.properties.get(VAR_CHUNKS_PROP)

    @chunks.setter
    def chunks(self, v: Optional[List[int]]) -> None:
        if v is None:
            self.properties.pop(VAR_CHUNKS_PROP, None)
        else:
            self.properties[VAR_CHUNKS_PROP] = v

    @property
    def attrs(self) -> Optional[Dict[str, Any]]:
        return self.properties.get(VAR_ATTRS_PROP)

    @attrs.setter
    def attrs(self, v: Optional[Dict[str, Any]]) -> None:
        if v is None:
            self.properties.pop(VAR_ATTRS_PROP, None)
        else:
            self.properties[VAR_ATTRS_PROP] = v

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Variable":
        return cls(d)

    # @staticmethod
    # def from_dict(d: Dict[str, Any]) -> "Dimension":
    #     dim_type = d.get(DIM_TYPE_PROP)
    #     if dim_type is None:
    #         raise pystac.RequiredPropertyMissing("cube_dimension", DIM_TYPE_PROP)
    #     if dim_type == "spatial":
    #         axis = d.get(DIM_AXIS_PROP)
    #         if axis is None:
    #             raise pystac.RequiredPropertyMissing("cube_dimension", DIM_AXIS_PROP)
    #         if axis == "z":
    #             return VerticalSpatialDimension(d)
    #         else:
    #             return HorizontalSpatialDimension(d)
    #     elif dim_type == "temporal":
    #         # The v1.0.0 spec says that AdditionalDimensions can have
    #         # type 'temporal', but it is unclear how to differentiate that
    #         # from a temporal dimension. Just key off of type for now.
    #         # See https://github.com/stac-extensions/datacube/issues/5
    #         return TemporalDimension(d)
    #     else:
    #         return AdditionalDimension(d)


class DatacubeExtension(
    Generic[T],
    PropertiesExtension,
    ExtensionManagementMixin[Union[pystac.Collection, pystac.Item]],
):
    def apply(self, dimensions: Dict[str, Dimension]) -> None:
        self.dimensions = dimensions

    @property
    def dimensions(self) -> Dict[str, Dimension]:
        return get_required(
            map_opt(
                lambda d: {k: Dimension.from_dict(v) for k, v in d.items()},
                self._get_property(DIMENSIONS_PROP, Dict[str, Any]),
            ),
            self,
            DIMENSIONS_PROP,
        )

    @dimensions.setter
    def dimensions(self, v: Dict[str, Dimension]) -> None:
        self._set_property(DIMENSIONS_PROP, {k: dim.to_dict() for k, dim in v.items()})

    @property
    def variables(self) -> Dict[str, Variable]:
        return get_required(
            map_opt(
                lambda d: {k: Variable.from_dict(v) for k, v in d.items()},
                self._get_property(VARIABLES_PROP, Dict[str, Any]),
            ),
            self,
            VARIABLES_PROP,
        )

    @variables.setter
    def variables(self, v: Dict[str, Variable]) -> None:
        self._set_property(VARIABLES_PROP, {k: dim.to_dict() for k, dim in v.items()})


    @classmethod
    def get_schema_uri(cls) -> str:
        return SCHEMA_URI

    @staticmethod
    def ext(obj: T) -> "DatacubeExtension[T]":
        if isinstance(obj, pystac.Collection):
            return cast(DatacubeExtension[T], CollectionDatacubeExtension(obj))
        if isinstance(obj, pystac.Item):
            return cast(DatacubeExtension[T], ItemDatacubeExtension(obj))
        elif isinstance(obj, pystac.Asset):
            return cast(DatacubeExtension[T], AssetDatacubeExtension(obj))
        else:
            raise pystac.ExtensionTypeError(
                f"Datacube extension does not apply to type {type(obj)}"
            )


class CollectionDatacubeExtension(DatacubeExtension[pystac.Collection]):
    def __init__(self, collection: pystac.Collection):
        self.collection = collection
        self.properties = collection.extra_fields

    def __repr__(self) -> str:
        return "<CollectionDatacubeExtension Item id={}>".format(self.collection.id)


class ItemDatacubeExtension(DatacubeExtension[pystac.Item]):
    def __init__(self, item: pystac.Item):
        self.item = item
        self.properties = item.properties

    def __repr__(self) -> str:
        return "<ItemDatacubeExtension Item id={}>".format(self.item.id)


class AssetDatacubeExtension(DatacubeExtension[pystac.Asset]):
    def __init__(self, asset: pystac.Asset):
        self.asset_href = asset.href
        self.properties = asset.properties
        if asset.owner and isinstance(asset.owner, pystac.Item):
            self.additional_read_properties = [asset.owner.properties]

    def __repr__(self) -> str:
        return "<AssetDatacubeExtension Item id={}>".format(self.asset_href)


class DatacubeExtensionHooks(ExtensionHooks):
    schema_uri: str = SCHEMA_URI
    prev_extension_ids: Set[str] = set(["datacube"])
    stac_object_types: Set[pystac.STACObjectType] = set(
        [pystac.STACObjectType.COLLECTION, pystac.STACObjectType.ITEM]
    )


DATACUBE_EXTENSION_HOOKS: ExtensionHooks = DatacubeExtensionHooks()
