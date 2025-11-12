"""Test custom command functionality"""
import pytest
from unittest.mock import Mock, patch
from jhub_apps.spawner.spawner_creation import subclass_spawner
from jhub_apps.spawner.types import Framework


class MockBaseSpawner:
    """Mock base spawner for testing"""
    def __init__(self):
        self.user_options = {}
        self.user = Mock()
        self.user.name = "testuser"
        self.user.id = 1
        self.name = "test-app"
        self.port = 8888
        self.config = Mock()
        self.config.JAppsConfig.python_exec = "python3"
        self.config.JupyterHub.bind_url = "http://localhost:8000"

    async def start(self):
        return ("localhost", self.port)

    def get_args(self):
        return []

    def get_env(self):
        return {}

    async def load_user_options(self):
        pass


def test_custom_command_basic():
    """Test that custom commands are wrapped in /bin/bash -c"""
    JHubSpawner = subclass_spawner(MockBaseSpawner)
    spawner = JHubSpawner()

    spawner.user_options = {
        "jhub_app": True,
        "framework": Framework.custom.value,
        "custom_command": "python app.py --port {port}",
        "filepath": "",
        "skip_conda": True,
    }

    command_args = spawner._get_app_command_args()

    # Should contain /bin/sh {-}c with the command containing {port}
    assert "/bin/sh" in command_args
    assert "{-}c" in command_args
    # {port} should be intact in the command for jhub-app-proxy to replace
    assert "python app.py --port {port}" in command_args


def test_custom_command_with_shell_operators():
    """Test that custom commands support shell operators like pipes"""
    JHubSpawner = subclass_spawner(MockBaseSpawner)
    spawner = JHubSpawner()

    spawner.user_options = {
        "jhub_app": True,
        "framework": Framework.custom.value,
        "custom_command": "uvicorn main:app --port {port} | tee app.log",
        "filepath": "",
        "skip_conda": True,
    }

    command_args = spawner._get_app_command_args()

    # The command should contain {port} intact for jhub-app-proxy
    assert any("uvicorn main:app --port {port} | tee app.log" in str(arg) for arg in command_args)
    assert "{-}c" in command_args


def test_custom_command_with_cd():
    """Test that custom commands support shell built-ins like cd"""
    JHubSpawner = subclass_spawner(MockBaseSpawner)
    spawner = JHubSpawner()

    spawner.user_options = {
        "jhub_app": True,
        "framework": Framework.custom.value,
        "custom_command": "cd /home/user/app && npm start -- --port {port}",
        "filepath": "",
        "skip_conda": True,
    }

    command_args = spawner._get_app_command_args()

    # Command with cd should contain {port} intact
    assert any("cd /home/user/app && npm start -- --port {port}" in str(arg) for arg in command_args)
    assert "{-}c" in command_args


def test_custom_command_with_conda_env():
    """Test that custom commands can use conda environment when not skipped"""
    JHubSpawner = subclass_spawner(MockBaseSpawner)
    spawner = JHubSpawner()

    spawner.user_options = {
        "jhub_app": True,
        "framework": Framework.custom.value,
        "custom_command": "python app.py --port {port}",
        "filepath": "",
        "conda_env": "myenv",
        "skip_conda": False,
    }

    command_args = spawner._get_app_command_args()

    # Should include --conda-env argument
    assert "--conda-env=myenv" in command_args
    # {port} should be intact in the command
    assert any("{port}" in str(arg) for arg in command_args)
    assert "{-}c" in command_args


def test_custom_command_skip_conda():
    """Test that custom commands skip conda environment when requested"""
    JHubSpawner = subclass_spawner(MockBaseSpawner)
    spawner = JHubSpawner()

    spawner.user_options = {
        "jhub_app": True,
        "framework": Framework.custom.value,
        "custom_command": "python app.py --port {port}",
        "filepath": "",
        "conda_env": "myenv",
        "skip_conda": True,
    }

    command_args = spawner._get_app_command_args()

    # Should NOT include --conda-env argument
    assert not any("--conda-env" in str(arg) for arg in command_args)
    # {port} should be intact in the command
    assert any("{port}" in str(arg) for arg in command_args)
    assert "{-}c" in command_args


def test_custom_command_with_environment_variables():
    """Test that custom commands can use environment variable substitution"""
    JHubSpawner = subclass_spawner(MockBaseSpawner)
    spawner = JHubSpawner()

    spawner.user_options = {
        "jhub_app": True,
        "framework": Framework.custom.value,
        "custom_command": "export MY_VAR=value && python app.py --port $JHUB_APPS_SPAWNER_PORT",
        "filepath": "",
        "skip_conda": True,
    }

    command_args = spawner._get_app_command_args()

    # Command with export should be preserved
    assert any("export MY_VAR=value" in str(arg) for arg in command_args)
