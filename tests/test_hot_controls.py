import pathlib, sys, tempfile, json, unittest
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "app"))
import hotops


class HotControlTests(unittest.TestCase):
    def test_protected_lab_has_no_docker_command(self):
        with (
            patch.object(
                hotops, "cfg", return_value={"labs": {"prod": {}}, "write_labs": []}
            ),
            patch.object(hotops, "run") as run,
        ):
            with self.assertRaises(PermissionError):
                hotops.authorize({"lab": "prod"})
            run.assert_not_called()

    def test_all_gpu_request_rejected(self):
        c = {
            "labs": {"test": {"prefix": "x-", "users": [{"name": "u"}]}},
            "write_labs": ["test"],
            "write_gpus": ["g0"],
        }
        with (
            patch.object(hotops, "cfg", return_value=c),
            patch.object(
                hotops,
                "obj",
                return_value={"HostConfig": {"DeviceRequests": [{"Count": -1}]}},
            ),
        ):
            with self.assertRaises(PermissionError):
                hotops.authorize(dict(lab="test", user="u", confirm="test"))

    def test_readonly_account_cannot_be_modified(self):
        with (
            patch.object(
                hotops,
                "authorize",
                return_value=({}, {}, {}, {"HostConfig": {"ReadonlyRootfs": True}}),
            ),
            patch.object(hotops, "run") as run,
        ):
            with self.assertRaises(ValueError):
                hotops.dispatch(dict(action="adduser"))
            run.assert_not_called()

    def test_running_memory_reduction_rejected(self):
        obj = {"HostConfig": {"Memory": 8 * 1073741824}, "State": {"Running": True}}
        with (
            patch.object(hotops, "authorize", return_value=({}, {}, {}, obj)),
            patch.object(hotops, "run") as run,
        ):
            with self.assertRaises(ValueError):
                hotops.dispatch(dict(action="resources", cpu=2, ram=4))
            run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
