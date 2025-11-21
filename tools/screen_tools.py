import uiautomator2 as u2
from typing import Optional
import asyncio


def register_screen_tools(mcp):
    """Register all screen control related tools with the MCP server."""

    @mcp.tool(
        name="screen_on",
        description="Turn the device screen on. Useful when the device has gone to sleep during automated testing."
    )
    def screen_on(device_id: Optional[str] = None) -> bool:
        """Turn on the device screen if it is currently off.

        This function wakes up the device and turns on the display,
        allowing UI automation to continue.

        Args:
            device_id: Optional device identifier. If not provided, uses the first available device

        Returns:
            bool: True if the screen was turned on successfully, False otherwise
        """
        try:
            d = u2.connect(device_id)
            d.screen_on()
            return True
        except Exception as e:
            print(f"Failed to turn screen on: {str(e)}")
            return False

    @mcp.tool(
        name="screen_off",
        description="Turn the device screen off. Useful for testing how apps behave when device goes to sleep."
    )
    def screen_off(device_id: Optional[str] = None) -> bool:
        """Turn off the device screen.

        This function turns off the device display, putting it in sleep mode.

        Args:
            device_id: Optional device identifier. If not provided, uses the first available device

        Returns:
            bool: True if the screen was turned off successfully, False otherwise
        """
        try:
            d = u2.connect(device_id)
            d.screen_off()
            return True
        except Exception as e:
            print(f"Failed to turn screen off: {str(e)}")
            return False

    @mcp.tool(
        name="unlock_screen",
        description="Unlock the device screen. This will wake the device if it's asleep and attempt to unlock it using the default method (swipe up or press home button)."
    )
    def unlock_screen(device_id: Optional[str] = None) -> bool:
        """Unlock the device screen if it is locked.

        This function will turn on the screen if it's off and attempt to unlock
        the device using the standard unlock method.

        Args:
            device_id: Optional device identifier. If not provided, uses the first available device

        Returns:
            bool: True if the screen was unlocked successfully, False otherwise

        Note:
            This may not work with complex security methods like PIN, pattern,
            password, or biometric authentication.
        """
        try:
            d = u2.connect(device_id)
            if not d.info["screenOn"]:
                d.screen_on()
            d.unlock()
            return True
        except Exception as e:
            print(f"Failed to unlock screen: {str(e)}")
            return False

    @mcp.tool(
        name="wait_for_screen_on",
        description="Wait until the device screen is turned on. Useful for asynchronous operations where screen activation is expected."
    )
    async def wait_for_screen_on(device_id: str) -> str:
        """Asynchronously wait for the device screen to turn on.

        This function polls the device screen state and returns when the screen
        becomes active. Useful for scenarios where the screen state change
        might take time.

        Args:
            device_id: The device identifier to connect to

        Returns:
            str: Message confirming that the screen is now on

        Note:
            This is an async function that checks every second for the screen to turn on.
            It may wait indefinitely if the screen never turns on.
        """
        d = u2.connect(device_id)
        while not d.screen_on():
            await asyncio.sleep(1)
        return "Screen is now on"