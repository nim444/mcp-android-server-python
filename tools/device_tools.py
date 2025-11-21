import uiautomator2 as u2
from typing import Optional, Dict, Any
import shutil
import subprocess


def register_device_tools(mcp):
    """Register all device management related tools with the MCP server."""

    @mcp.tool(name="mcp_health", description="Simple health check tool to verify MCP server is running")
    def mcp_health() -> str:
        """Check if the MCP server is running and responsive.

        Returns:
            A greeting message confirming the server is operational
        """
        return "Hello, world! MCP Android Device Operator server is running."

    @mcp.tool(
        name="get_device_status",
        description="Get complete device status including connection, ADB availability, and basic device info. This is the recommended first step to ensure everything is working before performing other operations."
    )
    def get_device_status() -> Dict[str, Any]:
        """Get comprehensive device status and connectivity information.

        This tool performs a complete check of the Android device setup including:
        - ADB availability and system status
        - Connected devices enumeration
        - Device connection and basic information
        - Screen state and readiness for automation

        Returns:
            Dictionary containing complete status information:
                - adb_available: Boolean indicating if ADB is accessible
                - connected_devices: List of available device IDs
                - device_connected: Boolean indicating if device connection succeeded
                - device_info: Basic device information (if connected)
                - screen_on: Boolean indicating if device screen is on
                - error: Any error messages (if applicable)
                - ready_for_automation: Boolean indicating if device is ready

        This is the perfect starting point for any Android automation workflow.
        It will guide you through any connection issues and provide clear next steps.
        """
        try:
            # Check ADB availability directly
            adb_path = shutil.which("adb")
            if not adb_path:
                return {
                    "adb_available": False,
                    "connected_devices": [],
                    "device_connected": False,
                    "device_info": {},
                    "screen_on": False,
                    "error": "ADB not available in PATH. Please install Android SDK platform-tools.",
                    "ready_for_automation": False
                }

            # Check for connected devices
            try:
                result = subprocess.run([adb_path, "devices"], capture_output=True, text=True, check=True)
                lines = result.stdout.strip().splitlines()
                devices = []
                for line in lines[1:]:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2 and parts[1] == "device":
                            devices.append(parts[0])
            except Exception as e:
                return {
                    "adb_available": True,
                    "connected_devices": [],
                    "device_connected": False,
                    "device_info": {},
                    "screen_on": False,
                    "error": f"Failed to check connected devices: {str(e)}",
                    "ready_for_automation": False
                }

            status = {
                "adb_available": True,
                "connected_devices": devices,
                "device_connected": False,
                "device_info": {},
                "screen_on": False,
                "error": None,
                "ready_for_automation": False
            }

            if not devices:
                status["error"] = "No devices connected. Please connect device and enable USB debugging."
                return status

            # Try to connect and get basic info
            try:
                d = u2.connect()
                info = d.info
                device_info = {
                    "manufacturer": info.get("manufacturer", ""),
                    "model": info.get("model", ""),
                    "serial": info.get("serial", ""),
                    "version": info.get("version", {}).get("release", ""),
                    "sdk": info.get("version", {}).get("sdk", 0),
                }

                status["device_connected"] = True
                status["device_info"] = device_info

                # Check screen state
                status["screen_on"] = d.screen_on()
                status["ready_for_automation"] = True

            except Exception as e:
                status["error"] = f"Device connection failed: {str(e)}"

            return status
        except Exception as e:
            return {
                "adb_available": False,
                "connected_devices": [],
                "device_connected": False,
                "device_info": {},
                "screen_on": False,
                "error": f"Status check failed: {str(e)}",
                "ready_for_automation": False
            }

    @mcp.tool(
        name="connect_device",
        description="Connect to an Android device using uiautomator2 and return comprehensive device information. If device_id is not provided, automatically connects to the first available device."
    )
    def connect_device(device_id: Optional[str] = None) -> Dict[str, Any]:
        """Connect to an Android device and retrieve detailed device information.

        This function establishes a connection to an Android device using uiautomator2
        and gathers comprehensive device information useful for automation and testing.
        If no device_id is provided, it will automatically connect to the first available device.

        Args:
            device_id: Optional device identifier (serial number). If not provided, connects to the first available device.

        Returns:
            Dictionary containing device details and connection status:
                - success: Boolean indicating if connection was successful
                - device_info: Dictionary with device details (if successful)
                - error: Error message (if connection failed)
                - device_id: The device ID that was connected to

        Device Info includes:
                - manufacturer: Device manufacturer (e.g., "Samsung", "Google")
                - model: Device model name (e.g., "Pixel 7", "Galaxy S23")
                - serial: Device serial number
                - version: Android version string (e.g., "13", "14")
                - sdk: Android SDK level (e.g., 33, 34)
                - display: Display density information
                - product: Product name identifier

        Note:
            - If no device_id is provided, connects to the first available device
            - Automatically checks ADB availability
            - Returns detailed success/failure information for debugging
        """
        try:
            # Check ADB availability directly (not calling MCP tool)
            adb_path = shutil.which("adb")
            if not adb_path:
                return {
                    "success": False,
                    "device_info": {},
                    "error": "ADB is not available in PATH",
                    "device_id": device_id
                }

            # Check for connected devices directly
            try:
                result = subprocess.run([adb_path, "devices"], capture_output=True, text=True, check=True)
                lines = result.stdout.strip().splitlines()
                devices = []
                for line in lines[1:]:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2 and parts[1] == "device":
                            devices.append(parts[0])

                if not devices:
                    return {
                        "success": False,
                        "device_info": {},
                        "error": "No Android devices connected. Please connect a device and ensure USB debugging is enabled.",
                        "device_id": device_id
                    }
            except:
                return {
                    "success": False,
                    "device_info": {},
                    "error": "Failed to check connected devices via ADB",
                    "device_id": device_id
                }

            # Connect to device
            d = u2.connect(device_id)
            info = d.info
            device_info = {
                "manufacturer": info.get("manufacturer", ""),
                "model": info.get("model", ""),
                "serial": info.get("serial", ""),
                "version": info.get("version", {}).get("release", ""),
                "sdk": info.get("version", {}).get("sdk", 0),
                "display": info.get("display", {}).get("density", ""),
                "product": info.get("productName", ""),
            }

            return {
                "success": True,
                "device_info": device_info,
                "error": None,
                "device_id": d.serial or device_id
            }
        except Exception as e:
            return {
                "success": False,
                "device_info": {},
                "error": f"Failed to connect to device: {str(e)}",
                "device_id": device_id
            }

    @mcp.tool(
        name="get_device_info",
        description="Get comprehensive device information including serial number, screen resolution, Android version, SDK level, battery status, WiFi IP address, manufacturer, model, and current screen state"
    )
    def get_device_info(device_id: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve detailed information about the connected Android device.

        This function provides extensive device information useful for debugging,
        automation scripting, and device status monitoring.

        Args:
            device_id: Optional device identifier. If not provided, uses the first available device.

        Returns:
            Dictionary containing comprehensive device information:
                - success: Boolean indicating if operation was successful
                - device_info: Dictionary with device details (if successful)
                - error: Error message (if operation failed)
                - device_id: The device ID that was used

            Device info includes:
                - serial: Device serial number
                - resolution: Screen resolution as "WIDTHxHEIGHT" string
                - version: Android version number
                - sdk: Android SDK level
                - battery: Battery information dictionary (level, health, status)
                - wifi_ip: Device's WiFi IP address
                - manufacturer: Device manufacturer
                - model: Device model name
                - is_screen_on: Boolean indicating if screen is currently on
                - product: Product name

        Note:
            Returns error information if unable to retrieve device information.
        """
        try:
            d = u2.connect(device_id)
            info = d.info
            display = d.window_size()

            device_info = {
                "serial": d.serial,
                "resolution": f"{display[0]}x{display[1]}",
                "version": info.get("version", {}).get("release", ""),
                "sdk": info.get("version", {}).get("sdk", 0),
                "battery": d.battery_info,
                "wifi_ip": d.wlan_ip,
                "manufacturer": info.get("manufacturer", ""),
                "model": info.get("model", ""),
                "is_screen_on": d.screen_on(),
                "product": info.get("productName", ""),
            }

            return {
                "success": True,
                "device_info": device_info,
                "error": None,
                "device_id": d.serial or device_id
            }
        except Exception as e:
            return {
                "success": False,
                "device_info": {},
                "error": f"Failed to get device info: {str(e)}",
                "device_id": device_id
            }

    @mcp.tool(
        name="check_adb_and_list_devices",
        description="Check if ADB (Android Debug Bridge) is available in the system PATH and list all connected Android devices with their status"
    )
    def check_adb_and_list_devices() -> Dict[str, Any]:
        """Verify ADB availability and enumerate connected Android devices.

        This utility function checks if ADB is properly installed and accessible,
        then lists all Android devices currently connected via USB or network.

        Returns:
            Dictionary containing:
                - adb_exists: Boolean indicating if ADB command is found in PATH
                - devices: List of device serial numbers that are ready for automation
                - error: Error message if ADB check fails, None otherwise

        The devices list only includes devices with "device" status (ready for commands).
        Devices in "unauthorized" or other states are excluded.
        """
        adb_path = shutil.which("adb")
        if not adb_path:
            return {
                "adb_exists": False,
                "devices": [],
                "error": "adb command not found in PATH",
            }
        try:
            result = subprocess.run(
                [adb_path, "devices"], capture_output=True, text=True, check=True
            )
            lines = result.stdout.strip().splitlines()
            devices = []
            for line in lines[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2 and parts[1] == "device":
                        devices.append(parts[0])
            return {"adb_exists": True, "devices": devices, "error": None}
        except Exception as e:
            return {"adb_exists": True, "devices": [], "error": str(e)}