import uiautomator2 as u2
from typing import Optional, Dict, Any
import shutil


def register_app_tools(mcp):
    """Register all app management related tools with the MCP server."""

    @mcp.tool(
        name="get_installed_apps",
        description="Get a complete list of all installed applications on your Android device. Automatically connects to the first available device if no device_id is specified. Returns package names for all system and user-installed apps."
    )
    def get_installed_apps(device_id: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve a comprehensive list of all installed applications on the device.

        This function enumerates all applications installed on the Android device,
        including both system pre-installed apps and user-installed applications.
        Automatically handles device connection and validation.

        Args:
            device_id: Optional device identifier. If not provided, connects to the first available device.

        Returns:
            Dictionary containing:
                - success: Boolean indicating if operation was successful
                - apps: List of package names (if successful)
                - count: Total number of installed apps (if successful)
                - error: Error message (if operation failed)
                - device_id: The device ID that was used

        Example output:
            {
                "success": true,
                "apps": ["com.android.settings", "com.example.app", ...],
                "count": 245,
                "error": null,
                "device_id": "ABC123DEF456"
            }

        Note:
            - This may take several seconds on devices with many installed applications
            - Returns package names only, not detailed app information
            - Includes both system apps and user-installed apps
            - Automatically validates device connection before proceeding
        """
        try:
            # Direct ADB check first
            adb_path = shutil.which("adb")
            if not adb_path:
                return {
                    "success": False,
                    "apps": [],
                    "count": 0,
                    "error": "ADB is not available in PATH",
                    "device_id": device_id
                }

            # Connect directly to device
            d = u2.connect(device_id)

            # Get installed apps
            apps = d.app_list()

            return {
                "success": True,
                "apps": apps,
                "count": len(apps),
                "error": None,
                "device_id": d.serial or device_id
            }
        except Exception as e:
            return {
                "success": False,
                "apps": [],
                "count": 0,
                "error": f"Failed to get installed apps: {str(e)}",
                "device_id": device_id
            }

    @mcp.tool(
        name="get_current_app",
        description="Get detailed information about the currently active/foreground application including package name, activity, and version information"
    )
    def get_current_app(device_id: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve information about the application currently in the foreground.

        This function provides details about the app that the user is currently
        interacting with or which is running in the foreground.

        Args:
            device_id: Optional device identifier. If not provided, uses the first available device.

        Returns:
            Dictionary containing app information:
                - package: Package name of the foreground app
                - activity: Current activity name
                - pid: Process ID
                - Other app metadata as provided by uiautomator2
        """
        d = u2.connect(device_id)
        return d.app_current()

    @mcp.tool(
        name="start_app",
        description="Launch an Android application by its package name with optional wait for the app to appear in foreground"
    )
    def start_app(
        package_name: str, device_id: Optional[str] = None, wait: bool = True
    ) -> bool:
        """Start an Android application using its package name.

        This function launches the specified app and optionally waits for it
        to appear in the foreground before returning.

        Args:
            package_name: The package name of the application to start (e.g., "com.example.app")
            device_id: Optional device identifier. If not provided, uses the first available device
            wait: Whether to wait for the app to come to the foreground (default: True)

        Returns:
            bool: True if the app was started successfully, False otherwise.
                  When wait=True, returns True only if the app appears in foreground.

        Examples:
            >>> start_app("com.android.chrome")  # Launch Chrome and wait
            >>> start_app("com.example.app", wait=False)  # Launch immediately, don't wait
        """
        try:
            d = u2.connect(device_id)
            d.app_start(package_name)
            if wait:
                pid = d.app_wait(package_name, front=True)
                return pid is not None
            return True
        except Exception as e:
            print(f"Failed to start app {package_name}: {str(e)}")
            return False

    @mcp.tool(
        name="stop_app",
        description="Force stop an Android application by its package name. Useful for closing apps that are misbehaving or for testing app restart scenarios."
    )
    def stop_app(package_name: str, device_id: Optional[str] = None) -> bool:
        """Stop a running Android application by its package name.

        This function force-stops the specified application, terminating all
        its processes and clearing it from memory.

        Args:
            package_name: The package name of the application to stop (e.g., "com.example.app")
            device_id: Optional device identifier. If not provided, uses the first available device

        Returns:
            bool: True if the app was stopped successfully, False otherwise

        Note:
            This is equivalent to the "Force Stop" action in Android app settings.
            The app will need to be relaunched to be used again.
        """
        try:
            d = u2.connect(device_id)
            d.app_stop(package_name)
            return True
        except Exception as e:
            print(f"Failed to stop app {package_name}: {str(e)}")
            return False

    @mcp.tool(
        name="stop_all_apps",
        description="Force stop all running applications on the device to free up memory and start with a clean slate for testing"
    )
    def stop_all_apps(device_id: Optional[str] = None) -> bool:
        """Stop all running applications on the Android device.

        This function terminates all user applications running on the device,
        which is useful for testing scenarios that require a clean state.

        Args:
            device_id: Optional device identifier. If not provided, uses the first available device

        Returns:
            bool: True if all apps were stopped successfully, False otherwise

        Note:
            This will not stop essential system services, only user applications.
            The device may take a few seconds to fully close all apps.
        """
        try:
            d = u2.connect(device_id)
            d.app_stop_all()
            return True
        except Exception as e:
            print(f"Failed to stop all apps: {str(e)}")
            return False

    @mcp.tool(
        name="clear_app_data",
        description="Clear all data and cache for a specific app. This is equivalent to 'Clear Data' in Android app settings and will reset the app to its initial state."
    )
    def clear_app_data(package_name: str, device_id: Optional[str] = None) -> bool:
        """Clear all user data and cache for the specified application.

        This function completely resets an app to its initial installed state,
        clearing all preferences, databases, cache, and user data.

        Args:
            package_name: The package name of the application (e.g., "com.example.app")
            device_id: Optional device identifier. If not provided, uses the first available device

        Returns:
            bool: True if app data was cleared successfully, False otherwise

        Warning:
            This action is irreversible and will delete all app data including
            login credentials, preferences, saved files, and databases.
            The app will behave as if freshly installed on next launch.
        """
        try:
            d = u2.connect(device_id)
            d.app_clear(package_name)
            return True
        except Exception as e:
            print(f"Failed to clear app data for {package_name}: {str(e)}")
            return False