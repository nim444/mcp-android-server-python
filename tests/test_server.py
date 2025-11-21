import pytest
from unittest.mock import MagicMock


def test_server_can_be_imported():
    """Test that the main server can be imported."""
    try:
        import server

        assert hasattr(server, "mcp")
        assert server.mcp.name == "Android Device Operator"
    except ImportError as e:
        pytest.fail(f"Failed to import server: {e}")


def test_tools_package_can_be_imported():
    """Test that the tools package can be imported."""
    try:
        from tools import register_all_tools

        assert callable(register_all_tools)
    except ImportError as e:
        pytest.fail(f"Failed to import tools package: {e}")


def test_all_tool_modules_can_be_imported():
    """Test that all tool modules can be imported without errors."""
    try:
        from tools import (
            device_tools,
            app_tools,
            screen_tools,
            input_tools,
            inspection_tools,
            advanced_tools,
        )

        # Test that each module has the register function
        assert hasattr(device_tools, "register_device_tools")
        assert hasattr(app_tools, "register_app_tools")
        assert hasattr(screen_tools, "register_screen_tools")
        assert hasattr(input_tools, "register_input_tools")
        assert hasattr(inspection_tools, "register_inspection_tools")
        assert hasattr(advanced_tools, "register_advanced_tools")
    except ImportError as e:
        pytest.fail(f"Failed to import tool modules: {e}")


def test_tool_registration_functions():
    """Test that tool registration functions are callable."""
    from tools import (
        device_tools,
        app_tools,
        screen_tools,
        input_tools,
        inspection_tools,
        advanced_tools,
    )

    # Test that all registration functions are callable
    assert callable(device_tools.register_device_tools)
    assert callable(app_tools.register_app_tools)
    assert callable(screen_tools.register_screen_tools)
    assert callable(input_tools.register_input_tools)
    assert callable(inspection_tools.register_inspection_tools)
    assert callable(advanced_tools.register_advanced_tools)


def test_register_all_tools_function():
    """Test the register_all_tools convenience function."""
    from tools import register_all_tools

    # Create a mock MCP server
    mock_mcp = MagicMock()

    # This should not raise any exceptions
    try:
        register_all_tools(mock_mcp)
        # The mock should have been called by the register functions
        assert True  # If we get here, everything worked
    except Exception as e:
        pytest.fail(f"register_all_tools failed: {e}")


def test_server_has_mcp_instance():
    """Test that the server has a valid MCP instance."""
    import server

    # Verify the MCP instance exists
    assert server.mcp is not None
    assert server.mcp.name == "Android Device Operator"


def test_server_instructions_exist():
    """Test that server has proper instructions for the AI."""
    import server

    assert server.mcp.instructions is not None
    assert len(server.mcp.instructions) > 0
    assert "Android" in server.mcp.instructions
    assert "automation" in server.mcp.instructions


def test_mcp_server_creation():
    """Test that MCP server can be created successfully."""
    from fastmcp import FastMCP

    # Create a test MCP server similar to our main server
    test_mcp = FastMCP(name="Test Server")

    # Should be able to register a simple test tool
    @test_mcp.tool(name="test_tool", description="Test tool")
    def test_tool():
        return "test"

    assert test_mcp is not None
    assert test_mcp.name == "Test Server"


def test_tool_module_structure():
    """Test that tool modules have the expected structure."""
    from tools import device_tools, app_tools, screen_tools

    # Test that modules have expected imports
    assert hasattr(device_tools, "register_device_tools")
    assert hasattr(app_tools, "register_app_tools")
    assert hasattr(screen_tools, "register_screen_tools")

    # Test that they have proper docstrings
    assert device_tools.register_device_tools.__doc__ is not None
    assert app_tools.register_app_tools.__doc__ is not None
    assert screen_tools.register_screen_tools.__doc__ is not None


def test_server_py_syntax():
    """Test that server.py has valid Python syntax."""

    try:
        # Try to compile the server.py file
        with open("server.py", "r") as f:
            server_code = f.read()

        # This will raise SyntaxError if there are syntax issues
        compile(server_code, "server.py", "exec")

    except SyntaxError as e:
        pytest.fail(f"server.py has syntax error: {e}")
    except FileNotFoundError:
        pytest.fail("server.py not found")
    except Exception as e:
        pytest.fail(f"Unexpected error checking server.py: {e}")


def test_tools_modules_syntax():
    """Test that all tool modules have valid Python syntax."""

    tool_modules = [
        "tools/__init__.py",
        "tools/device_tools.py",
        "tools/app_tools.py",
        "tools/screen_tools.py",
        "tools/input_tools.py",
        "tools/inspection_tools.py",
        "tools/advanced_tools.py",
    ]

    for module_path in tool_modules:
        try:
            # Try to compile each module file
            with open(module_path, "r") as f:
                module_code = f.read()

            # This will raise SyntaxError if there are syntax issues
            compile(module_code, module_path, "exec")

        except SyntaxError as e:
            pytest.fail(f"{module_path} has syntax error: {e}")
        except FileNotFoundError:
            pytest.fail(f"{module_path} not found")
        except Exception as e:
            pytest.fail(f"Unexpected error checking {module_path}: {e}")
