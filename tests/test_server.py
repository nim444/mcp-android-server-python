import pytest
from unittest.mock import patch, MagicMock, PropertyMock
import asyncio
from server import (
    mcp_health,
    connect_device,
    DeviceInfo,
    get_installed_apps,
    get_current_app,
    start_app,
    stop_app,
    AppInfo,
    stop_all_apps,
    screen_on,
    screen_off,
    get_device_info,
    press_key,
    unlock_screen,
    check_adb_and_list_devices,
    wait_for_screen_on,
    click,
    send_text,
    get_element_info,
    ElementInfo,
    swipe,
    wait_for_element,
    screenshot,
    long_click,
    scroll_to,
    drag,
    get_toast,
    clear_app_data,
    wait_activity,
    dump_hierarchy,
)
from typing import List, Dict, Any


def test_mcp_health():
    assert mcp_health() == "Hello, world!"


@patch("server.u2.connect")
def test_connect_device_success(mock_connect):
    # Mock the device object and its info attribute
    mock_device = MagicMock()
    mock_device.info = {
        "manufacturer": "TestManufacturer",
        "model": "TestModel",
        "serial": "testserial123",
        "version": {"release": "10", "sdk": 29},
        "display": {"density": "xhdpi"},
        "productName": "TestProduct",
    }
    mock_connect.return_value = mock_device

    expected_info: DeviceInfo = {
        "manufacturer": "TestManufacturer",
        "model": "TestModel",
        "serial": "testserial123",
        "version": "10",
        "sdk": 29,
        "display": "xhdpi",
        "product": "TestProduct",
    }
    assert connect_device("testserial123") == expected_info
    mock_connect.assert_called_once_with("testserial123")


@patch("server.u2.connect")
def test_connect_device_failure(mock_connect):
    mock_connect.side_effect = Exception("Test connection error")

    with pytest.raises(ConnectionError) as excinfo:
        connect_device("testserial123")
    assert (
        "Failed to connect to device with ID 'testserial123': Test connection error"
        in str(excinfo.value)
    )
    mock_connect.assert_called_once_with("testserial123")


@patch("server.u2.connect")
def test_get_installed_apps_success(mock_connect):
    mock_device = MagicMock()
    mock_apps_list = [
        {
            "package_name": "com.example.app1",
            "version_name": "1.0",
            "version_code": 1,
            "first_install_time": "2023-01-01",
            "last_update_time": "2023-01-02",
        },
        {
            "package_name": "com.example.app2",
            "version_name": "2.0",
            "version_code": 2,
            "first_install_time": "2023-02-01",
            "last_update_time": "2023-02-02",
        },
    ]
    mock_device.app_list.return_value = mock_apps_list
    mock_connect.return_value = mock_device

    expected_apps: List[AppInfo] = [
        {
            "package_name": "com.example.app1",
            "version_name": "1.0",
            "version_code": 1,
            "first_install_time": "2023-01-01",
            "last_update_time": "2023-01-02",
        },
        {
            "package_name": "com.example.app2",
            "version_name": "2.0",
            "version_code": 2,
            "first_install_time": "2023-02-01",
            "last_update_time": "2023-02-02",
        },
    ]
    assert get_installed_apps("testdevice") == expected_apps
    mock_connect.assert_called_once_with("testdevice")
    mock_device.app_list.assert_called_once()


@patch("server.u2.connect")
def test_get_current_app_success(mock_connect):
    mock_device = MagicMock()
    mock_current_app = {
        "package_name": "com.example.current",
        "version_name": "1.5",
        "version_code": 15,
        "first_install_time": "2023-03-01",
        "last_update_time": "2023-03-05",
    }
    mock_device.app_current.return_value = mock_current_app
    mock_connect.return_value = mock_device

    expected_app: AppInfo = {
        "package_name": "com.example.current",
        "version_name": "1.5",
        "version_code": 15,
        "first_install_time": "2023-03-01",
        "last_update_time": "2023-03-05",
    }
    assert get_current_app("testdevice") == expected_app
    mock_connect.assert_called_once_with("testdevice")
    mock_device.app_current.assert_called_once()


@patch("server.u2.connect")
def test_start_app_success_with_wait(mock_connect):
    mock_device = MagicMock()
    mock_device.app_wait.return_value = 12345  # PID
    mock_connect.return_value = mock_device

    assert start_app("com.example.app", device_id="testdevice", wait=True) == True
    mock_connect.assert_called_once_with("testdevice")
    mock_device.app_start.assert_called_once_with("com.example.app")
    mock_device.app_wait.assert_called_once_with("com.example.app", front=True)


@patch("server.u2.connect")
def test_start_app_success_without_wait(mock_connect):
    mock_device = MagicMock()
    mock_connect.return_value = mock_device

    assert start_app("com.example.app", device_id="testdevice", wait=False) == True
    mock_connect.assert_called_once_with("testdevice")
    mock_device.app_start.assert_called_once_with("com.example.app")
    mock_device.app_wait.assert_not_called()


@patch("server.u2.connect")
def test_start_app_failure(mock_connect):
    mock_device = MagicMock()
    mock_device.app_start.side_effect = Exception("Failed to start")
    mock_connect.return_value = mock_device

    assert start_app("com.example.app", device_id="testdevice") == False
    mock_connect.assert_called_once_with("testdevice")
    mock_device.app_start.assert_called_once_with("com.example.app")


@patch("server.u2.connect")
def test_stop_app_success(mock_connect):
    mock_device = MagicMock()
    mock_connect.return_value = mock_device

    assert stop_app("com.example.app", device_id="testdevice") == True
    mock_connect.assert_called_once_with("testdevice")
    mock_device.app_stop.assert_called_once_with("com.example.app")


@patch("server.u2.connect")
def test_stop_app_failure(mock_connect):
    mock_device = MagicMock()
    mock_device.app_stop.side_effect = Exception("Failed to stop")
    mock_connect.return_value = mock_device

    assert stop_app("com.example.app", device_id="testdevice") == False
    mock_connect.assert_called_once_with("testdevice")
    mock_device.app_stop.assert_called_once_with("com.example.app")


@patch("server.u2.connect")
def test_stop_all_apps_success(mock_connect):
    mock_device = MagicMock()
    mock_connect.return_value = mock_device

    assert stop_all_apps(device_id="testdevice") == True
    mock_connect.assert_called_once_with("testdevice")
    mock_device.app_stop_all.assert_called_once()


@patch("server.u2.connect")
def test_stop_all_apps_failure(mock_connect):
    mock_device = MagicMock()
    mock_device.app_stop_all.side_effect = Exception("Failed to stop all apps")
    mock_connect.return_value = mock_device

    assert stop_all_apps(device_id="testdevice") == False
    mock_connect.assert_called_once_with("testdevice")
    mock_device.app_stop_all.assert_called_once()


@patch("server.u2.connect")
def test_screen_on_success(mock_connect):
    mock_device = MagicMock()
    mock_connect.return_value = mock_device

    assert screen_on(device_id="testdevice") == True
    mock_connect.assert_called_once_with("testdevice")
    mock_device.screen_on.assert_called_once()


@patch("server.u2.connect")
def test_screen_on_failure(mock_connect):
    mock_device = MagicMock()
    mock_device.screen_on.side_effect = Exception("Failed to turn screen on")
    mock_connect.return_value = mock_device

    assert screen_on(device_id="testdevice") == False
    mock_connect.assert_called_once_with("testdevice")
    mock_device.screen_on.assert_called_once()


@patch("server.u2.connect")
def test_screen_off_success(mock_connect):
    mock_device = MagicMock()
    mock_connect.return_value = mock_device

    assert screen_off(device_id="testdevice") == True
    mock_connect.assert_called_once_with("testdevice")
    mock_device.screen_off.assert_called_once()


@patch("server.u2.connect")
def test_screen_off_failure(mock_connect):
    mock_device = MagicMock()
    mock_device.screen_off.side_effect = Exception("Failed to turn screen off")
    mock_connect.return_value = mock_device

    assert screen_off(device_id="testdevice") == False
    mock_connect.assert_called_once_with("testdevice")
    mock_device.screen_off.assert_called_once()


@patch("server.u2.connect")
def test_get_device_info_success(mock_connect):
    mock_device = MagicMock()
    mock_device.info = {
        "version": {"release": "11", "sdk": 30},
        "manufacturer": "Google",
        "model": "Pixel 5",
    }
    mock_device.serial = "testserial"
    mock_device.window_size.return_value = (1080, 2340)
    mock_device.battery_info = {"level": 90, "status": 2}
    mock_device.wlan_ip = "192.168.1.100"
    mock_device.screen_on.return_value = True
    mock_connect.return_value = mock_device

    expected_info: Dict[str, Any] = {
        "serial": "testserial",
        "resolution": "1080x2340",
        "version": "11",
        "sdk": 30,
        "battery": {"level": 90, "status": 2},
        "wifi_ip": "192.168.1.100",
        "manufacturer": "Google",
        "model": "Pixel 5",
        "is_screen_on": True,
    }
    assert get_device_info(device_id="testdevice") == expected_info
    mock_connect.assert_called_once_with("testdevice")


@patch("server.u2.connect")
def test_get_device_info_failure(mock_connect):
    mock_device = MagicMock()
    info_property_mock = PropertyMock(side_effect=Exception("Failed to get info"))
    type(mock_device).info = info_property_mock
    mock_connect.return_value = mock_device

    assert get_device_info(device_id="testdevice") == {}
    mock_connect.assert_called_once_with("testdevice")


@patch("server.u2.connect")
def test_press_key_success(mock_connect):
    mock_device = MagicMock()
    mock_connect.return_value = mock_device

    assert press_key("home", device_id="testdevice") == True
    mock_connect.assert_called_once_with("testdevice")
    mock_device.press.assert_called_once_with("home")


@patch("server.u2.connect")
def test_press_key_failure(mock_connect):
    mock_device = MagicMock()
    mock_device.press.side_effect = Exception("Failed to press key")
    mock_connect.return_value = mock_device

    assert press_key("home", device_id="testdevice") == False
    mock_connect.assert_called_once_with("testdevice")
    mock_device.press.assert_called_once_with("home")


@patch("server.u2.connect")
def test_unlock_screen_success_screen_off(mock_connect):
    mock_device = MagicMock()
    mock_device.info = {"screenOn": False}
    mock_connect.return_value = mock_device

    assert unlock_screen(device_id="testdevice") == True
    mock_connect.assert_called_once_with("testdevice")
    mock_device.screen_on.assert_called_once()
    mock_device.unlock.assert_called_once()


@patch("server.u2.connect")
def test_unlock_screen_success_screen_on(mock_connect):
    mock_device = MagicMock()
    mock_device.info = {"screenOn": True}
    mock_connect.return_value = mock_device

    assert unlock_screen(device_id="testdevice") == True
    mock_connect.assert_called_once_with("testdevice")
    mock_device.screen_on.assert_not_called()
    mock_device.unlock.assert_called_once()


@patch("server.u2.connect")
def test_unlock_screen_failure(mock_connect):
    mock_device = MagicMock()
    mock_device.info = {"screenOn": False}
    mock_device.unlock.side_effect = Exception("Unlock failed")
    mock_connect.return_value = mock_device

    assert unlock_screen(device_id="testdevice") == False
    mock_connect.assert_called_once_with("testdevice")


@patch("server.shutil.which")
@patch("server.subprocess.run")
def test_check_adb_and_list_devices_success(mock_subprocess_run, mock_shutil_which):
    mock_shutil_which.return_value = "/usr/bin/adb"
    mock_process = MagicMock()
    mock_process.stdout = (
        "List of devices attached\nemulator-5554\tdevice\n192.168.1.101:5555\tdevice\n"
    )
    mock_subprocess_run.return_value = mock_process

    expected_result = {
        "adb_exists": True,
        "devices": ["emulator-5554", "192.168.1.101:5555"],
        "error": None,
    }
    assert check_adb_and_list_devices() == expected_result
    mock_shutil_which.assert_called_once_with("adb")
    mock_subprocess_run.assert_called_once_with(
        ["/usr/bin/adb", "devices"], capture_output=True, text=True, check=True
    )


@patch("server.shutil.which")
def test_check_adb_not_found(mock_shutil_which):
    mock_shutil_which.return_value = None
    expected_result = {
        "adb_exists": False,
        "devices": [],
        "error": "adb command not found in PATH",
    }
    assert check_adb_and_list_devices() == expected_result
    mock_shutil_which.assert_called_once_with("adb")


@patch("server.shutil.which")
@patch("server.subprocess.run")
def test_check_adb_subprocess_error(mock_subprocess_run, mock_shutil_which):
    mock_shutil_which.return_value = "/usr/bin/adb"
    mock_subprocess_run.side_effect = Exception("ADB error")

    expected_result = {"adb_exists": True, "devices": [], "error": "ADB error"}
    assert check_adb_and_list_devices() == expected_result


@pytest.mark.asyncio
@patch("server.u2.connect")
async def test_wait_for_screen_on_success(mock_connect):
    mock_device = MagicMock()
    # Simulate screen turning on after a few checks
    mock_device.screen_on.side_effect = [False, False, True]
    mock_connect.return_value = mock_device

    # We need to patch asyncio.sleep to avoid actual sleeping during tests
    with patch("asyncio.sleep", new_callable=MagicMock) as mock_sleep:
        mock_sleep.return_value = asyncio.Future()  # Make it awaitable
        mock_sleep.return_value.set_result(None)
        result = await wait_for_screen_on(device_id="testdevice")

    assert result == "Screen is now on"
    assert mock_device.screen_on.call_count == 3
    mock_connect.assert_called_once_with("testdevice")


@patch("server.u2.connect")
def test_click_success(mock_connect):
    mock_device = MagicMock()
    mock_element = MagicMock()
    mock_element.exists = True
    # Make the selector call return the mock_element
    mock_device.return_value.wait.return_value = (
        mock_element  # e.g. d(text=selector).wait(...)
    )
    mock_connect.return_value = mock_device

    assert (
        click(selector="TestButton", selector_type="text", device_id="testdevice")
        == True
    )
    mock_connect.assert_called_once_with("testdevice")
    mock_device.assert_called_once_with(text="TestButton")
    mock_device.return_value.wait.assert_called_once_with(timeout=10.0)
    mock_element.click.assert_called_once()


@patch("server.u2.connect")
def test_click_element_not_found(mock_connect):
    mock_device = MagicMock()
    mock_element = MagicMock()
    mock_element.exists = False  # Simulate element not found
    mock_device.return_value.wait.return_value = mock_element
    mock_connect.return_value = mock_device

    assert (
        click(
            selector="NonExistent", selector_type="resourceId", device_id="testdevice"
        )
        == False
    )
    mock_connect.assert_called_once_with("testdevice")
    mock_device.assert_called_once_with(resourceId="NonExistent")
    mock_device.return_value.wait.assert_called_once_with(timeout=10.0)
    mock_element.click.assert_not_called()


@patch("server.u2.connect")
def test_click_failure(mock_connect):
    mock_device = MagicMock()
    mock_device.return_value.wait.side_effect = Exception("Click failed")
    mock_connect.return_value = mock_device

    assert (
        click(
            selector="ErrorButton", selector_type="description", device_id="testdevice"
        )
        == False
    )
    mock_connect.assert_called_once_with("testdevice")


@patch("server.u2.connect")
def test_send_text_success(mock_connect):
    mock_device = MagicMock()
    mock_connect.return_value = mock_device

    assert send_text("Hello", clear=True, device_id="testdevice") == True
    mock_connect.assert_called_once_with("testdevice")
    mock_device.send_keys.assert_called_once_with("Hello", clear=True)


@patch("server.u2.connect")
def test_send_text_failure(mock_connect):
    mock_device = MagicMock()
    mock_device.send_keys.side_effect = Exception("Send keys failed")
    mock_connect.return_value = mock_device

    assert send_text("World", device_id="testdevice") == False
    mock_connect.assert_called_once_with("testdevice")


@patch("server.u2.connect")
def test_get_element_info_success(mock_connect):
    mock_device = MagicMock()
    mock_element = MagicMock()
    mock_element.exists = True
    mock_element.info = {
        "text": "Sample Text",
        "resourceId": "com.example:id/sample",
        "contentDescription": "Sample Description",
        "className": "android.widget.TextView",
        "enabled": True,
        "clickable": True,
        "bounds": {"left": 0, "top": 0, "right": 100, "bottom": 100},
        "selected": False,
        "focused": False,
    }
    mock_device.return_value.wait.return_value = mock_element
    mock_connect.return_value = mock_device

    expected_info: ElementInfo = {
        "text": "Sample Text",
        "resourceId": "com.example:id/sample",
        "description": "Sample Description",
        "className": "android.widget.TextView",
        "enabled": True,
        "clickable": True,
        "bounds": {"left": 0, "top": 0, "right": 100, "bottom": 100},
        "selected": False,
        "focused": False,
    }
    assert (
        get_element_info(
            selector="Sample Text", selector_type="text", device_id="testdevice"
        )
        == expected_info
    )
    mock_connect.assert_called_once_with("testdevice")


@patch("server.u2.connect")
def test_get_element_info_not_found(mock_connect):
    mock_device = MagicMock()
    mock_element = MagicMock()
    mock_element.exists = False
    mock_device.return_value.wait.return_value = mock_element
    mock_connect.return_value = mock_device

    assert get_element_info(selector="NotFound", device_id="testdevice") == {}
    mock_connect.assert_called_once_with("testdevice")


@patch("server.u2.connect")
def test_swipe_success(mock_connect):
    mock_device = MagicMock()
    mock_connect.return_value = mock_device

    assert swipe(0.1, 0.2, 0.8, 0.9, duration=0.2, device_id="testdevice") == True
    mock_connect.assert_called_once_with("testdevice")
    mock_device.swipe.assert_called_once_with(0.1, 0.2, 0.8, 0.9, duration=0.2)


@patch("server.u2.connect")
def test_swipe_failure(mock_connect):
    mock_device = MagicMock()
    mock_device.swipe.side_effect = Exception("Swipe failed")
    mock_connect.return_value = mock_device

    assert swipe(0.1, 0.2, 0.8, 0.9, device_id="testdevice") == False
    mock_connect.assert_called_once_with("testdevice")


@patch("server.u2.connect")
def test_wait_for_element_success(mock_connect):
    mock_device = MagicMock()
    # d(text=selector).wait(timeout=timeout) returns True if element appears
    mock_device.return_value.wait.return_value = True
    mock_connect.return_value = mock_device

    assert (
        wait_for_element(
            selector="MyElement",
            selector_type="text",
            timeout=5.0,
            device_id="testdevice",
        )
        == True
    )
    mock_connect.assert_called_once_with("testdevice")
    mock_device.assert_called_once_with(text="MyElement")
    mock_device.return_value.wait.assert_called_once_with(timeout=5.0)


@patch("server.u2.connect")
def test_wait_for_element_description_success(mock_connect):
    mock_device = MagicMock()
    mock_element = MagicMock()
    mock_element.exists = True
    mock_device.return_value.wait.return_value = (
        mock_element  # For description selector
    )
    mock_connect.return_value = mock_device

    assert (
        wait_for_element(
            selector="MyDesc",
            selector_type="description",
            timeout=3.0,
            device_id="testdevice",
        )
        == True
    )
    mock_connect.assert_called_once_with("testdevice")
    mock_device.assert_called_once_with(description="MyDesc")
    mock_device.return_value.wait.assert_called_once_with(timeout=3.0)


@patch("server.u2.connect")
def test_wait_for_element_failure(mock_connect):
    mock_device = MagicMock()
    mock_device.return_value.wait.side_effect = Exception(
        "Wait failed"
    )  # Or return False
    mock_connect.return_value = mock_device

    assert wait_for_element(selector="MyElement", device_id="testdevice") == False
    mock_connect.assert_called_once_with("testdevice")


@patch("server.u2.connect")
def test_screenshot_success(mock_connect):
    mock_device = MagicMock()
    mock_connect.return_value = mock_device

    assert screenshot("test_image.png", device_id="testdevice") == True
    mock_connect.assert_called_once_with("testdevice")
    mock_device.screenshot.assert_called_once_with("test_image.png")


@patch("server.u2.connect")
def test_screenshot_failure(mock_connect):
    mock_device = MagicMock()
    mock_device.screenshot.side_effect = Exception("Screenshot failed")
    mock_connect.return_value = mock_device

    assert screenshot("test_image.png", device_id="testdevice") == False
    mock_connect.assert_called_once_with("testdevice")


@patch("server.u2.connect")
def test_long_click_success(mock_connect):
    mock_device = MagicMock()
    mock_element = MagicMock()
    mock_element.exists = True
    mock_device.return_value = mock_element  # e.g. d(text=selector)
    mock_connect.return_value = mock_device

    assert (
        long_click(
            selector="LongPress",
            selector_type="text",
            duration=1.5,
            device_id="testdevice",
        )
        == True
    )
    mock_connect.assert_called_once_with("testdevice")
    mock_device.assert_called_once_with(text="LongPress")
    mock_element.long_click.assert_called_once_with(duration=1.5)


@patch("server.u2.connect")
def test_long_click_element_not_found(mock_connect):
    mock_device = MagicMock()
    mock_element = MagicMock()
    mock_element.exists = False
    mock_device.return_value = mock_element
    mock_connect.return_value = mock_device

    assert long_click(selector="NotFound", device_id="testdevice") == False
    mock_connect.assert_called_once_with("testdevice")
    mock_element.long_click.assert_not_called()


@patch("server.u2.connect")
def test_scroll_to_success(mock_connect):
    mock_device = MagicMock()
    # d(scrollable=True).scroll.to(text=selector) returns True on success
    mock_device.return_value.scroll.to.return_value = True
    mock_connect.return_value = mock_device

    assert (
        scroll_to(selector="TargetItem", selector_type="text", device_id="testdevice")
        == True
    )
    mock_connect.assert_called_once_with("testdevice")
    mock_device.assert_called_once_with(scrollable=True)
    mock_device.return_value.scroll.to.assert_called_once_with(text="TargetItem")


@patch("server.u2.connect")
def test_scroll_to_description_success(mock_connect):
    mock_device = MagicMock()
    mock_element = MagicMock()
    mock_element.exists = True
    mock_device.return_value.scroll.to.return_value = (
        mock_element  # For description selector
    )
    mock_connect.return_value = mock_device

    assert (
        scroll_to(
            selector="TargetDesc", selector_type="description", device_id="testdevice"
        )
        == True
    )
    mock_connect.assert_called_once_with("testdevice")
    mock_device.assert_called_once_with(scrollable=True)
    mock_device.return_value.scroll.to.assert_called_once_with(description="TargetDesc")


@patch("server.u2.connect")
def test_scroll_to_failure(mock_connect):
    mock_device = MagicMock()
    mock_device.return_value.scroll.to.side_effect = Exception(
        "Scroll failed"
    )  # Or return False
    mock_connect.return_value = mock_device

    assert scroll_to(selector="TargetItem", device_id="testdevice") == False
    mock_connect.assert_called_once_with("testdevice")


@patch("server.u2.connect")
def test_drag_success(mock_connect):
    mock_device = MagicMock()
    mock_element = MagicMock()
    mock_element.exists = True
    mock_device.return_value = mock_element  # e.g. d(text=selector)
    mock_connect.return_value = mock_device

    assert (
        drag(
            selector="Draggable",
            selector_type="resourceId",
            to_x=100,
            to_y=200,
            device_id="testdevice",
        )
        == True
    )
    mock_connect.assert_called_once_with("testdevice")
    mock_device.assert_called_once_with(resourceId="Draggable")
    mock_element.drag_to.assert_called_once_with(100, 200)


@patch("server.u2.connect")
def test_drag_element_not_found(mock_connect):
    mock_device = MagicMock()
    mock_element = MagicMock()
    mock_element.exists = False
    mock_device.return_value = mock_element
    mock_connect.return_value = mock_device

    assert (
        drag(
            selector="NotFound",
            selector_type="text",
            to_x=100,
            to_y=200,
            device_id="testdevice",
        )
        == False
    )
    mock_connect.assert_called_once_with("testdevice")
    mock_element.drag_to.assert_not_called()


@patch("server.u2.connect")
def test_get_toast_success(mock_connect):
    mock_device = MagicMock()
    mock_device.toast.get_message.return_value = "Test Toast Message"
    mock_connect.return_value = mock_device

    assert get_toast(device_id="testdevice") == "Test Toast Message"
    mock_connect.assert_called_once_with("testdevice")
    mock_device.toast.get_message.assert_called_once_with(10.0)


@patch("server.u2.connect")
def test_get_toast_no_message(mock_connect):
    mock_device = MagicMock()
    mock_device.toast.get_message.return_value = None  # Simulate no toast
    mock_connect.return_value = mock_device

    assert get_toast(device_id="testdevice") == ""
    mock_connect.assert_called_once_with("testdevice")


@patch("server.u2.connect")
def test_clear_app_data_success(mock_connect):
    mock_device = MagicMock()
    mock_connect.return_value = mock_device

    assert clear_app_data("com.example.app", device_id="testdevice") == True
    mock_connect.assert_called_once_with("testdevice")
    mock_device.app_clear.assert_called_once_with("com.example.app")


@patch("server.u2.connect")
def test_clear_app_data_failure(mock_connect):
    mock_device = MagicMock()
    mock_device.app_clear.side_effect = Exception("Clear data failed")
    mock_connect.return_value = mock_device

    assert clear_app_data("com.example.app", device_id="testdevice") == False
    mock_connect.assert_called_once_with("testdevice")


@patch("server.u2.connect")
def test_wait_activity_success(mock_connect):
    mock_device = MagicMock()
    # d.wait_activity(activity, timeout=timeout) returns True on success
    mock_device.wait_activity.return_value = True
    mock_connect.return_value = mock_device

    assert wait_activity(".MainActivity", timeout=5.0, device_id="testdevice") == True
    mock_connect.assert_called_once_with("testdevice")
    mock_device.wait_activity.assert_called_once_with(".MainActivity", timeout=5.0)


@patch("server.u2.connect")
def test_wait_activity_failure(mock_connect):
    mock_device = MagicMock()
    mock_device.wait_activity.side_effect = Exception(
        "Wait activity failed"
    )  # Or return False
    mock_connect.return_value = mock_device

    assert wait_activity(".MainActivity", device_id="testdevice") == False
    mock_connect.assert_called_once_with("testdevice")


@patch("server.u2.connect")
def test_dump_hierarchy_success(mock_connect):
    mock_device = MagicMock()
    mock_device.dump_hierarchy.return_value = "<node><child></child></node>"
    mock_connect.return_value = mock_device

    result = dump_hierarchy(device_id="testdevice")

    assert result == "<node><child></child></node>"
    mock_connect.assert_called_once_with("testdevice")
    mock_device.dump_hierarchy.assert_called_once_with(
        compressed=False, pretty=True, max_depth=50
    )


@patch("server.u2.connect")
def test_dump_hierarchy_with_options(mock_connect):
    mock_device = MagicMock()
    mock_device.dump_hierarchy.return_value = "<node></node>"
    mock_connect.return_value = mock_device

    result = dump_hierarchy(
        compressed=True, pretty=False, max_depth=10, device_id="testdevice"
    )

    assert result == "<node></node>"
    mock_connect.assert_called_once_with("testdevice")
    mock_device.dump_hierarchy.assert_called_once_with(
        compressed=True, pretty=False, max_depth=10
    )


@patch("server.u2.connect")
def test_dump_hierarchy_failure(mock_connect):
    mock_device = MagicMock()
    mock_device.dump_hierarchy.side_effect = Exception("Failed to dump hierarchy")
    mock_connect.return_value = mock_device

    result = dump_hierarchy(device_id="testdevice")

    assert result == ""
    mock_connect.assert_called_once_with("testdevice")


# Add more tests here for other functions
