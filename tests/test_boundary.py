import importlib.util, pathlib, unittest
from unittest.mock import patch

p = pathlib.Path(__file__).resolve().parents[1] / "app/broker.py"
spec = importlib.util.spec_from_file_location("broker", p)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.c = {
            "labs": {
                "sandbox": {"gpu": "g0", "sandbox": True, "users": [{"name": "demo"}]},
                **{
                    str(i): {"gpu": "g" + str(i), "users": [{"name": "existing"}]}
                    for i in [5, 6, 7]
                },
            },
            "write_labs": ["sandbox"],
            "write_gpus": ["g0"],
        }

    def test_existing_labs_rejected_before_any_command(self):
        for lab in ["5", "6", "7"]:
            for action in [
                "create",
                "start",
                "stop",
                "recreate",
                "password",
                "gpu_test",
                "grow",
            ]:
                with (
                    self.subTest(lab=lab, action=action),
                    patch.object(b, "config", return_value=self.c),
                    patch.object(b, "run") as run,
                    patch.object(b, "inspect") as inspect,
                ):
                    with self.assertRaises(PermissionError):
                        b.operate(
                            dict(action=action, lab=lab, confirm=lab, user="existing")
                        )
                    run.assert_not_called()
                    inspect.assert_not_called()

    def test_gpu_gate_independent_of_lab_gate(self):
        self.c["write_labs"].append("5")
        with self.assertRaises(PermissionError):
            b.authorize(self.c, "stop", "5")

    def test_cross_lab_and_path_injection(self):
        for user in ["existing", "../../etc", "demo;reboot"]:
            with self.assertRaises(PermissionError):
                b.authorize(self.c, "password", "sandbox", user)

    def test_unsupported_action(self):
        with self.assertRaises(ValueError):
            b.authorize(self.c, "shell", "sandbox")

    def test_no_creation_or_recreation(self):
        for action in ["create", "recreate"]:
            with self.assertRaises(PermissionError):
                b.authorize(self.c, action, "sandbox", "demo")

    def test_allowed_sandbox(self):
        for action in ["start", "stop", "password", "gpu_test", "grow"]:
            self.assertTrue(b.authorize(self.c, action, "sandbox", "demo")["sandbox"])


if __name__ == "__main__":
    unittest.main()
