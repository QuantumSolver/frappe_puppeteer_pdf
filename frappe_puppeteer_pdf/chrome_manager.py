import os
import subprocess
import time
from pathlib import Path

import frappe


class ChromeManager:
    """Manages Chrome process for Puppeteer PDF generation"""

    def __init__(self):
        self.process = None
        self.port = 9222
        self.executable_path = None

    def start(self):
        """Start Chrome with remote debugging enabled"""
        if self.process and self.process.poll() is None:
            frappe.logger().info("Chrome already running")
            return

        self.executable_path = self.get_chrome_path()

        cmd = [
            self.executable_path,
            "--headless=new",
            "--disable-gpu",
            f"--remote-debugging-port={self.port}",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-setuid-sandbox",
            "--disable-background-networking",
            "--disable-default-apps",
            "--disable-extensions",
            "--disable-sync",
            "--disable-translate",
            "--metrics-recording-only",
            "--no-first-run",
            "--safebrowsing-disable-auto-update",
            "--disable-client-side-phishing-detection",
            "--disable-component-update",
            "--disable-domain-reliability",
            "--disable-features=TranslateUI",
            "--hide-scrollbars",
            "--mute-audio",
            "about:blank",
        ]

        try:
            frappe.logger().info(f"Starting Chrome: {self.executable_path}")
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

            # Wait for Chrome to start
            time.sleep(3)

            # Verify Chrome is running
            if self.process.poll() is not None:
                raise Exception("Chrome process failed to start")

            frappe.logger().info(f"Chrome started on port {self.port}")

        except Exception as e:
            frappe.log_error(f"Failed to start Chrome: {e}")
            self.process = None
            raise

    def get_chrome_path(self):
        """Get Chrome executable path from install.py"""
        from .install import find_or_download_chromium_executable

        return find_or_download_chromium_executable()

    def get_connection_url(self):
        """Get WebSocket URL for Playwright connection"""
        return f"http://localhost:{self.port}"

    def stop(self):
        """Stop Chrome process"""
        if self.process:
            try:
                frappe.logger().info("Stopping Chrome process")
                self.process.terminate()
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                frappe.logger().warning(
                    "Chrome did not terminate gracefully, forcing kill"
                )
                self.process.kill()
                self.process.wait()
            finally:
                self.process = None

    def is_running(self):
        """Check if Chrome process is running"""
        return self.process and self.process.poll() is None

    def __del__(self):
        """Ensure Chrome is stopped when object is destroyed"""
        self.stop()


# Global Chrome manager instance
_chrome_manager = None


def get_chrome_manager():
    """Get singleton Chrome manager instance"""
    global _chrome_manager
    if _chrome_manager is None:
        _chrome_manager = ChromeManager()
    return _chrome_manager


def ensure_chrome_running():
    """Ensure Chrome is running, start if not"""
    manager = get_chrome_manager()
    if not manager.is_running():
        manager.start()
    return manager


def stop_chrome():
    """Stop Chrome if running"""
    global _chrome_manager
    if _chrome_manager:
        _chrome_manager.stop()
        _chrome_manager = None
