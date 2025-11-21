import uiautomator2 as u2
from typing import Optional, TypedDict, Dict, Any


# Type definitions for element info
class ElementInfo(TypedDict):
    text: str
    resourceId: str
    description: str
    className: str
    enabled: bool
    clickable: bool
    bounds: Dict[str, Any]
    selected: bool
    focused: bool


def register_inspection_tools(mcp):
    """Register all inspection related tools with the MCP server."""

    @mcp.tool(
        name="get_element_info",
        description="Get detailed information about a UI element including its properties, bounds, text, resource ID, class name, and interaction capabilities."
    )
    def get_element_info(
        selector: str,
        selector_type: str = "text",
        timeout: float = 10.0,
        device_id: Optional[str] = None,
    ) -> ElementInfo:
        """Retrieve detailed information about a UI element.

        This function finds an element and returns comprehensive information about
        its properties, useful for debugging automation scripts or element inspection.

        Args:
            selector: The value to search for (text, resource ID, or content description)
            selector_type: The type of selector ('text', 'resourceId', or 'description')
            timeout: Maximum time in seconds to wait for the element (default: 10.0)
            device_id: Optional device identifier. If not provided, uses the first available device

        Returns:
            ElementInfo dictionary containing:
                - text: Visible text on the element
                - resourceId: Android resource ID
                - description: Content description/accessibility label
                - className: Android class name (e.g., "android.widget.Button")
                - enabled: Whether the element is enabled
                - clickable: Whether the element can be clicked
                - bounds: Element position and size {"left": x, "top": y, "right": x2, "bottom": y2}
                - selected: Whether the element is selected
                - focused: Whether the element has focus

            Returns empty dictionary if element not found.
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
                info = el.info
                return {
                    "text": info.get("text", ""),
                    "resourceId": info.get("resourceId", ""),
                    "description": info.get("contentDescription", ""),
                    "className": info.get("className", ""),
                    "enabled": info.get("enabled", False),
                    "clickable": info.get("clickable", False),
                    "bounds": info.get("bounds", {}),
                    "selected": info.get("selected", False),
                    "focused": info.get("focused", False),
                }
            return {}
        except Exception as e:
            print(f"Failed to get element info for {selector}: {str(e)}")
            return {}

    @mcp.tool(
        name="wait_for_element",
        description="Wait for a UI element to appear on the screen. Essential for handling loading screens, animations, and dynamic content."
    )
    def wait_for_element(
        selector: str,
        selector_type: str = "text",
        timeout: float = 10.0,
        device_id: Optional[str] = None,
    ) -> bool:
        """Wait for a UI element to appear on the device screen.

        This function pauses execution until the specified element becomes visible
        or the timeout is reached. Essential for reliable automation.

        Args:
            selector: The value to search for (text, resource ID, or content description)
            selector_type: The type of selector ('text', 'resourceId', or 'description')
            timeout: Maximum time in seconds to wait (default: 10.0)
            device_id: Optional device identifier. If not provided, uses the first available device

        Returns:
            bool: True if the element appeared within the timeout, False otherwise

        Examples:
            >>> wait_for_element("Loading complete", "text", 30)  # Wait up to 30 seconds
            >>> wait_for_element("com.app:id/result", "resourceId")  # Wait for resource ID
            >>> wait_for_element("Submit button", "description")  # Wait by content description

        Note:
            Use this function when dealing with dynamic content, loading screens,
            or network-dependent elements that may take time to appear.
        """
        try:
            d = u2.connect(device_id)
            if selector_type == "text":
                return d(text=selector).wait(timeout=timeout)
            elif selector_type == "resourceId":
                return d(resourceId=selector).wait(timeout=timeout)
            elif selector_type == "description":
                el = d(description=selector).wait(timeout=timeout)
                return el is not None and el.exists
            else:
                raise ValueError(f"Invalid selector_type: {selector_type}")
        except Exception as e:
            print(f"Failed to wait for element {selector}: {str(e)}")
            return False

    @mcp.tool(
        name="scroll_to",
        description="Scroll to a specific element on the screen. Automatically finds scrollable containers and scrolls until the target element is visible."
    )
    def scroll_to(
        selector: str, selector_type: str = "text", device_id: Optional[str] = None
    ) -> bool:
        """Scroll to make a UI element visible on the screen.

        This function automatically finds scrollable containers and scrolls until
        the target element becomes visible. Useful for long lists and pages.

        Args:
            selector: The value to search for (text, resource ID, or content description)
            selector_type: The type of selector ('text', 'resourceId', or 'description')
            device_id: Optional device identifier. If not provided, uses the first available device

        Returns:
            bool: True if the element was found and scrolled into view, False otherwise

        Examples:
            >>> scroll_to("Settings", "text")  # Scroll to element with text "Settings"
            >>> scroll_to("com.app:id/footer", "resourceId")  # Scroll by resource ID
            >>> scroll_to("Contact Us", "description")  # Scroll by content description

        Note:
            This function will scroll through all scrollable containers on the screen
            to find the target element. It may not work if the element is in a
            non-scrollable area or requires specific scroll directions.
        """
        try:
            d = u2.connect(device_id)
            if selector_type == "text":
                return d(scrollable=True).scroll.to(text=selector)
            elif selector_type == "resourceId":
                return d(scrollable=True).scroll.to(resourceId=selector)
            elif selector_type == "description":
                el = d(scrollable=True).scroll.to(description=selector)
                return el is not None and el.exists
            else:
                raise ValueError(f"Invalid selector_type: {selector_type}")
        except Exception as e:
            print(f"Failed to scroll to element {selector}: {str(e)}")
            return False

    @mcp.tool(
        name="screenshot",
        description="Capture a screenshot of the device screen and save it to the specified file path. Essential for debugging and visual verification."
    )
    def screenshot(filename: str, device_id: Optional[str] = None) -> bool:
        """Take a screenshot of the device screen and save it to a file.

        This function captures the current screen state and saves it as an image file,
        which is useful for debugging automation failures and creating visual documentation.

        Args:
            filename: The file path where the screenshot will be saved (e.g., "screenshot.png")
            device_id: Optional device identifier. If not provided, uses the first available device

        Returns:
            bool: True if the screenshot was saved successfully, False otherwise

        Examples:
            >>> screenshot("login_screen.png")  # Save as PNG
            >>> screenshot("/path/to/screenshots/error.png")  # Save with full path
            >>> screenshot(f"test_{timestamp}.jpg")  # Dynamic filename

        Note:
            Supported formats include PNG, JPG, and other common image formats.
            The directory must exist and be writable.
        """
        try:
            d = u2.connect(device_id)
            d.screenshot(filename)
            return True
        except Exception as e:
            print(f"Failed to take screenshot: {str(e)}")
            return False

    @mcp.tool(
        name="dump_hierarchy",
        description="Dump the complete UI hierarchy of the current screen as XML. Essential for understanding screen structure, finding elements, and debugging automation issues."
    )
    def dump_hierarchy(
        compressed: bool = False,
        pretty: bool = True,
        max_depth: int = 50,
        device_id: Optional[str] = None,
    ) -> str:
        """Export the current screen's UI hierarchy as XML.

        This function provides a complete XML representation of all UI elements
        currently visible on the screen, which is invaluable for:
        - Finding elements for automation
        - Understanding screen structure
        - Debugging automation failures
        - Analyzing app UI changes

        Args:
            compressed: If True, excludes less important nodes for smaller output (default: False)
            pretty: If True, formats the XML with proper indentation (default: True)
            max_depth: Maximum depth of XML hierarchy to include (default: 50)
            device_id: Optional device identifier. If not provided, uses the first available device

        Returns:
            str: XML string representing the complete UI hierarchy

        Examples:
            >>> dump_hierarchy()  # Full pretty-formatted hierarchy
            >>> dump_hierarchy(compressed=True)  # Smaller output for debugging
            >>> dump_hierarchy(max_depth=10)  # Limited depth for faster processing

        Note:
            The output can be very large for complex screens. Use compressed=True
            for quicker analysis when you don't need all details.
        """
        try:
            d = u2.connect(device_id)
            xml = d.dump_hierarchy(
                compressed=compressed, pretty=pretty, max_depth=max_depth
            )
            return xml
        except Exception as e:
            print(f"Failed to dump UI hierarchy: {str(e)}")
            return ""