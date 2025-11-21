import uiautomator2 as u2
from typing import Optional


def register_input_tools(mcp):
    """Register all input and gesture related tools with the MCP server."""

    @mcp.tool(
        name="press_key",
        description="Press a hardware or software key on the device. Common keys include: home, back, menu, volume_up, volume_down, power, enter, delete"
    )
    def press_key(key: str, device_id: Optional[str] = None) -> bool:
        """Simulate pressing a key on the Android device.

        This function sends a key event to the device, simulating both hardware
        button presses and software key presses.

        Args:
            key: The key to press. Common values include:
                - 'home': Home button
                - 'back': Back button
                - 'menu': Menu button
                - 'volume_up', 'volume_down': Volume buttons
                - 'power': Power button
                - 'enter': Enter key
                - 'delete': Delete/backspace key
            device_id: Optional device identifier. If not provided, uses the first available device

        Returns:
            bool: True if the key press was sent successfully, False otherwise

        Examples:
            >>> press_key("home")  # Press home button
            >>> press_key("back")  # Go back
        """
        try:
            d = u2.connect(device_id)
            d.press(key)
            return True
        except Exception as e:
            print(f"Failed to press key {key}: {str(e)}")
            return False

    @mcp.tool(
        name="click",
        description="Click on a UI element identified by text, resource ID, or content description. Supports multiple selector types for flexible element targeting."
    )
    def click(
        selector: str,
        selector_type: str = "text",
        timeout: float = 10.0,
        device_id: Optional[str] = None,
    ) -> bool:
        """Click on a UI element on the device screen using various selector types.

        This function finds and clicks on UI elements using different identification
        methods. It's one of the most commonly used automation actions.

        Args:
            selector: The value to search for (text, resource ID, or content description)
            selector_type: The type of selector to use:
                - 'text': Search by visible text on the element
                - 'resourceId': Search by Android resource ID (e.g., "com.app:id/button")
                - 'description': Search by content description/accessibility label
            timeout: Maximum time in seconds to wait for the element to appear (default: 10.0)
            device_id: Optional device identifier. If not provided, uses the first available device

        Returns:
            bool: True if the element was found and clicked successfully, False otherwise

        Examples:
            >>> click("Submit", "text")  # Click element with text "Submit"
            >>> click("com.app:id/login_btn", "resourceId")  # Click by resource ID
            >>> click("Login button", "description")  # Click by content description

        Raises:
            ValueError: If an invalid selector_type is provided
        """
        try:
            d = u2.connect(device_id)
            if selector_type == "text":
                el = d(text=selector).wait(timeout=timeout)
            elif selector_type == "resourceId":
                el = d(resourceId=selector).wait(timeout=timeout)
            elif selector_type == "description":
                el = d(description=selector).wait(timeout=timeout)
            else:
                raise ValueError(f"Invalid selector_type: {selector_type}")

            if el and el.exists:
                el.click()
                return True
            return False
        except Exception as e:
            print(f"Failed to click element {selector}: {str(e)}")
            return False

    @mcp.tool(
        name="long_click",
        description="Perform a long click (press and hold) on a UI element. Useful for context menus, drag operations, or long press actions."
    )
    def long_click(
        selector: str,
        selector_type: str = "text",
        duration: float = 1.0,
        device_id: Optional[str] = None,
    ) -> bool:
        """Perform a long click gesture on a UI element.

        This function simulates pressing and holding an element for a specified duration,
        which can trigger context menus, activate drag modes, or perform other long-press actions.

        Args:
            selector: The value to search for (text, resource ID, or content description)
            selector_type: The type of selector ('text', 'resourceId', or 'description')
            duration: Duration of the long click in seconds (default: 1.0)
            device_id: Optional device identifier. If not provided, uses the first available device

        Returns:
            bool: True if the long click was performed successfully, False otherwise

        Examples:
            >>> long_click("Item", "text", 2.0)  # Long click for 2 seconds
            >>> long_click("com.app:id/draggable", "resourceId")  # Long click by ID
        """
        try:
            d = u2.connect(device_id)
            if selector_type == "text":
                el = d(text=selector)
            elif selector_type == "resourceId":
                el = d(resourceId=selector)
            elif selector_type == "description":
                el = d(description=selector)
            else:
                raise ValueError(f"Invalid selector_type: {selector_type}")

            if el and el.exists:
                el.long_click(duration=duration)
                return True
            return False
        except Exception as e:
            print(f"Failed to long click element {selector}: {str(e)}")
            return False

    @mcp.tool(
        name="swipe",
        description="Perform a swipe gesture from one coordinate to another. Useful for scrolling, paging, or custom swipe actions."
    )
    def swipe(
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        duration: float = 0.5,
        device_id: Optional[str] = None,
    ) -> bool:
        """Perform a swipe gesture on the device screen.

        This function simulates a finger swipe from a start point to an end point,
        with control over the swipe duration for natural movement.

        Args:
            start_x: Starting X coordinate (0 to screen width)
            start_y: Starting Y coordinate (0 to screen height)
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration: Swipe duration in seconds (default: 0.5)
            device_id: Optional device identifier. If not provided, uses the first available device

        Returns:
            bool: True if the swipe was performed successfully, False otherwise

        Examples:
            >>> swipe(100, 500, 100, 100)  # Swipe up
            >>> swipe(100, 100, 500, 100, 0.3)  # Swipe right quickly
            >>> swipe(300, 400, 300, 1000, 1.0)  # Slow swipe down

        Note:
            Coordinates are relative to the device screen resolution.
            Use (0, 0) for top-left corner.
        """
        try:
            d = u2.connect(device_id)
            d.swipe(start_x, start_y, end_x, end_y, duration=duration)
            return True
        except Exception as e:
            print(f"Failed to perform swipe: {str(e)}")
            return False

    @mcp.tool(
        name="drag",
        description="Drag a specific UI element to a target location on the screen. Useful for drag-and-drop operations, reordering items, or custom interactions."
    )
    def drag(
        selector: str,
        selector_type: str,
        to_x: int,
        to_y: int,
        device_id: Optional[str] = None,
    ) -> bool:
        """Drag a UI element to a specific location on the screen.

        This function finds an element and drags it to the specified coordinates,
        useful for drag-and-drop operations and custom UI interactions.

        Args:
            selector: The value to identify the element to drag
            selector_type: The type of selector ('text', 'resourceId', or 'description')
            to_x: Target X coordinate to drag the element to
            to_y: Target Y coordinate to drag the element to
            device_id: Optional device identifier. If not provided, uses the first available device

        Returns:
            bool: True if the drag operation was successful, False otherwise

        Examples:
            >>> drag("Item", "text", 200, 300)  # Drag text "Item" to coordinates (200, 300)
            >>> drag("com.app:id/card", "resourceId", 100, 100)  # Drag by resource ID
        """
        try:
            d = u2.connect(device_id)
            if selector_type == "text":
                el = d(text=selector)
            elif selector_type == "resourceId":
                el = d(resourceId=selector)
            elif selector_type == "description":
                el = d(description=selector)
            else:
                raise ValueError(f"Invalid selector_type: {selector_type}")

            if el and el.exists:
                el.drag_to(to_x, to_y)
                return True
            return False
        except Exception as e:
            print(f"Failed to drag element {selector}: {str(e)}")
            return False

    @mcp.tool(
        name="send_text",
        description="Send text input to the currently focused UI element. Can optionally clear existing text before sending. Perfect for form filling, search boxes, and text fields."
    )
    def send_text(text: str, clear: bool = True, device_id: Optional[str] = None) -> bool:
        """Send text to the currently focused input element on the device.

        This function types text into whatever UI element currently has focus,
        such as text fields, search boxes, or forms.

        Args:
            text: The text to send to the focused element
            clear: Whether to clear any existing text before sending (default: True)
            device_id: Optional device identifier. If not provided, uses the first available device

        Returns:
            bool: True if the text was sent successfully, False otherwise

        Examples:
            >>> send_text("Hello World")  # Clear field and type "Hello World"
            >>> send_text("additional text", clear=False)  # Append to existing text
            >>> send_text("user@example.com")  # Type an email address

        Note:
            Make sure the target text field is focused before calling this function.
            Use click() to focus a text field if needed.
        """
        try:
            d = u2.connect(device_id)
            d.send_keys(text, clear=clear)
            return True
        except Exception as e:
            print(f"Failed to send text: {str(e)}")
            return False