import importlib
import sys
import types


def _load_space_app(monkeypatch):
    sys.modules.pop("space_app", None)
    monkeypatch.setitem(sys.modules, "gradio", types.ModuleType("gradio"))
    return importlib.import_module("space_app")


def test_build_launch_kwargs_keeps_show_api_for_legacy_gradio(monkeypatch):
    space_app = _load_space_app(monkeypatch)

    def legacy_launch(server_name=None, server_port=None, show_api=None, prevent_thread_lock=None):
        return None

    kwargs = space_app._build_launch_kwargs(legacy_launch, "0.0.0.0", 7860)

    assert kwargs == {
        "server_name": "0.0.0.0",
        "server_port": 7860,
        "prevent_thread_lock": False,
        "show_api": False,
    }


def test_build_launch_kwargs_omits_show_api_for_new_gradio(monkeypatch):
    space_app = _load_space_app(monkeypatch)

    def modern_launch(server_name=None, server_port=None, prevent_thread_lock=None):
        return None

    kwargs = space_app._build_launch_kwargs(modern_launch, "0.0.0.0", 7860)

    assert kwargs == {
        "server_name": "0.0.0.0",
        "server_port": 7860,
        "prevent_thread_lock": False,
    }
