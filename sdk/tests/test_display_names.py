"""The ratified geometry display-name registry (R1): no raw slug on camera."""

import unittest

from chief_engineer.display_names import display_name


class DisplayNameTests(unittest.TestCase):
    def test_ratified_bodies_resolve_by_filename(self):
        self.assertEqual(display_name("b52.stl"), "B-52 Stratofortress-class airframe")
        self.assertEqual(display_name("motorBike.obj"),
                         "Motorcycle with rider — highway configuration")
        self.assertEqual(display_name("naca4412_wing.stl"), "NACA 4412 finite wing")
        self.assertEqual(display_name("naca0012_wing.stl"), "NACA 0012 finite wing")

    def test_ratified_bodies_resolve_by_bare_key(self):
        self.assertEqual(display_name("b52"), "B-52 Stratofortress-class airframe")
        self.assertEqual(display_name("motorbike"),
                         "Motorcycle with rider — highway configuration")
        self.assertEqual(display_name("valve"),
                         "Idealized trileaflet aortic valve — systolic configuration")
        self.assertEqual(display_name("aortic_valve"),
                         "Idealized trileaflet aortic valve — systolic configuration")

    def test_lookup_is_case_and_separator_insensitive(self):
        self.assertEqual(display_name("B52"), display_name("b52"))
        self.assertEqual(display_name("Ahmed-25"), display_name("ahmed_25"))
        self.assertEqual(display_name("AHMED_35.STL".lower()), display_name("ahmed_35"))

    def test_ahmed_bodies_carry_their_slant_angle(self):
        self.assertIn("25°", display_name("ahmed_25"))
        self.assertIn("35°", display_name("ahmed_35"))

    def test_canonical_calibration_bodies(self):
        for shape in ("sphere", "cube", "cylinder"):
            self.assertEqual(display_name(shape), f"Canonical calibration body — {shape}")
        self.assertEqual(display_name("flat_plate"), "Canonical calibration body — plate")

    def test_airliner_and_valve_workflow_keys_resolve(self):
        self.assertEqual(display_name("aircraft-optimization"),
                         "300-passenger twin-aisle airliner — planform study")
        self.assertEqual(display_name("valve-study"),
                         "Idealized trileaflet aortic valve — systolic configuration")

    def test_unregistered_body_falls_back_to_a_name_not_a_path(self):
        shown = display_name("some_new_body.stl")
        self.assertNotIn("/", shown)
        self.assertNotIn("\\", shown)
        self.assertNotIn(".stl", shown)
        self.assertNotIn("_", shown)
        self.assertEqual(shown, "Some new body")

    def test_empty_input_never_crashes_or_leaks_none(self):
        self.assertEqual(display_name(None), "Unnamed body")
        self.assertEqual(display_name(""), "Unnamed body")

    def test_never_returns_a_raw_dotted_filename(self):
        for key in ("b52.stl", "motorBike.obj", "naca4412_wing.stl", "unknown_thing.obj"):
            shown = display_name(key)
            self.assertNotIn(".stl", shown.lower())
            self.assertNotIn(".obj", shown.lower())


if __name__ == "__main__":
    unittest.main()
