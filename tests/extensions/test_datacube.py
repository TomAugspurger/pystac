from pystac.errors import RequiredPropertyMissing
import unittest
import pystac
from pystac import ExtensionTypeError
from pystac.extensions.datacube import DatacubeExtension, VerticalSpatialDimension

from tests.utils import TestCases


class DatacubeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.example_uri = TestCases.get_path("data-files/datacube/item.json")

    def test_validate_datacube(self) -> None:
        item = pystac.Item.from_file(self.example_uri)
        item.validate()

    def test_extension_not_implemented(self) -> None:
        # Should raise exception if Item does not include extension URI
        item = pystac.Item.from_file(self.example_uri)
        item.stac_extensions.remove(DatacubeExtension.get_schema_uri())

        with self.assertRaises(pystac.ExtensionNotImplemented):
            _ = DatacubeExtension.ext(item)

        # Should raise exception if owning Item does not include extension URI
        asset = item.assets["data"]

        with self.assertRaises(pystac.ExtensionNotImplemented):
            _ = DatacubeExtension.ext(asset)

        # Should succeed if Asset has no owner
        ownerless_asset = pystac.Asset.from_dict(asset.to_dict())
        _ = DatacubeExtension.ext(ownerless_asset)

    def test_item_ext_add_to(self) -> None:
        item = pystac.Item.from_file(self.example_uri)
        item.stac_extensions.remove(DatacubeExtension.get_schema_uri())
        self.assertNotIn(DatacubeExtension.get_schema_uri(), item.stac_extensions)

        _ = DatacubeExtension.ext(item, add_if_missing=True)

        self.assertIn(DatacubeExtension.get_schema_uri(), item.stac_extensions)

    def test_asset_ext_add_to(self) -> None:
        item = pystac.Item.from_file(self.example_uri)
        item.stac_extensions.remove(DatacubeExtension.get_schema_uri())
        self.assertNotIn(DatacubeExtension.get_schema_uri(), item.stac_extensions)
        asset = item.assets["data"]

        _ = DatacubeExtension.ext(asset, add_if_missing=True)

        self.assertIn(DatacubeExtension.get_schema_uri(), item.stac_extensions)

    def test_should_raise_exception_when_passing_invalid_extension_object(
        self,
    ) -> None:
        self.assertRaisesRegex(
            ExtensionTypeError,
            r"^Datacube extension does not apply to type 'object'$",
            DatacubeExtension.ext,
            object(),
        )

    def test_clear_step(self) -> None:
        item = pystac.Item.from_file(self.example_uri)
        ext = DatacubeExtension.ext(item)
        dim = ext.dimensions["pressure_levels"]
        assert isinstance(dim, VerticalSpatialDimension)

        assert dim.step == 100
        dim.step = None
        assert "step" in dim.properties
        dim.clear_step()
        assert "step" not in dim.properties

    def test_variable(self) -> None:
        item = pystac.Item.from_file(self.example_uri)
        ext = DatacubeExtension.ext(item)
        self.assertEqual(
            sorted(ext.variables), ["lambert_conformal_conic", "lat", "tmax"]
        )

        var = ext.variables["lambert_conformal_conic"]
        self.assertEqual(var.description, "A dimensionless variable")
        self.assertEqual(var.var_type, "auxiliary")
        self.assertEqual(var.dimensions, [])
        self.assertIs(var.extent, None)
        self.assertIs(var.unit, None)
        self.assertIs(var.values, None)

        lat = ext.variables["lat"]
        self.assertEqual(lat.var_type, "auxiliary")
        self.assertEqual(lat.dimensions, ["y", "x"])
        self.assertEqual(lat.extent, [37.48803556, 37.613537207])

        tmax = ext.variables["tmax"]
        self.assertEqual(tmax.var_type, "data")
        self.assertEqual(tmax.dimensions, ["time", "y", "x", "pressure_levels"])
        self.assertEqual(tmax.description, "Maximum temperature")
        self.assertEqual(tmax.unit, "degrees C")
        self.assertEqual(tmax.extent, [0, 100])
        self.assertEqual(tmax.values, [0, 10, 100])

    def test_set_variable(self) -> None:
        item = pystac.Item.from_file(self.example_uri)
        ext = DatacubeExtension.ext(item)

        var = ext.variables["tmax"]
        var.dimensions = None  # type: ignore
        self.assertIn("dimensions", var.properties)
        with self.assertRaises(RequiredPropertyMissing):
            var.dimensions

        var.var_type = None  # type: ignore
        self.assertIn("dimensions", var.properties)
        with self.assertRaises(RequiredPropertyMissing):
            var.var_type

        for attr in ["description", "extent", "values", "unit"]:
            setattr(var, attr, None)
            self.assertNotIn(attr, var.properties)
