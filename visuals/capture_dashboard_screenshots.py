"""
capture_dashboard_screenshots.py

Capture one complete full-page screenshot for every Terp Protect
dashboard tab.

Screenshots are saved under:

visuals/
└── UI screenshots/
    └── dashboard_capture_<timestamp>/
"""

from datetime import datetime
from pathlib import Path
import re

from playwright.sync_api import sync_playwright


DASHBOARD_URL = "http://localhost:8501"

DASHBOARD_TABS = [
    "Command Center",
    "Time Patterns",
    "Location Hotspots",
    "Case Outcomes",
    "Reporting Delay",
    "Arrests & Charges",
    "Data Quality",
]


SCRIPT_DIRECTORY = Path(__file__).resolve().parent

OUTPUT_DIRECTORY = (
    SCRIPT_DIRECTORY
    / "UI screenshots"
    / f"dashboard_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
)


def create_file_name(tab_name):
    """
    Convert a tab name into a safe screenshot filename.
    """
    file_name = re.sub(
        r"[^A-Za-z0-9]+",
        "_",
        tab_name.strip()
    )

    return file_name.strip("_").lower()


def ensure_sidebar_is_open(page):
    """
    Open the Streamlit sidebar when it is collapsed.
    """
    sidebar = page.locator(
        '[data-testid="stSidebar"]'
    )

    if (
        sidebar.count() > 0
        and sidebar.first.is_visible()
    ):
        return

    sidebar_button = page.locator(
        '[data-testid="stSidebarCollapsedControl"]'
    )

    if (
        sidebar_button.count() > 0
        and sidebar_button.first.is_visible()
    ):
        sidebar_button.first.click()

        page.wait_for_timeout(
            700
        )


def scroll_through_dashboard(page):
    """
    Scroll through the dashboard so charts and tables lower on the
    page finish rendering.
    """
    page.evaluate(
        """
        async () => {
            const wait = (milliseconds) =>
                new Promise(
                    resolve => setTimeout(resolve, milliseconds)
                );

            const mainContainer =
                document.querySelector('[data-testid="stMain"]');

            const scrollContainer =
                mainContainer || document.documentElement;

            const viewportHeight =
                scrollContainer.clientHeight || window.innerHeight;

            const scrollStep = Math.max(
                500,
                Math.floor(viewportHeight * 0.8)
            );

            let position = 0;

            while (
                position < scrollContainer.scrollHeight
            ) {
                scrollContainer.scrollTo(
                    0,
                    position
                );

                window.scrollTo(
                    0,
                    position
                );

                await wait(180);

                position += scrollStep;
            }

            scrollContainer.scrollTo(
                0,
                scrollContainer.scrollHeight
            );

            await wait(500);

            scrollContainer.scrollTo(
                0,
                0
            );

            window.scrollTo(
                0,
                0
            );

            await wait(500);
        }
        """
    )


def prepare_full_page_layout(page):
    """
    Expand Streamlit's internal scrolling containers while preserving
    the dashboard's dark background.

    Streamlit normally keeps the main application inside a fixed-height
    scrolling container. This function temporarily removes those height
    restrictions so Playwright can capture the entire dashboard.
    """
    page.add_style_tag(
        content="""
        html,
        body,
        #root,
        .stApp,
        [data-testid="stApp"],
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {
            background:
                linear-gradient(
                    135deg,
                    #090D14 0%,
                    #0E1624 48%,
                    #111C2D 100%
                ) !important;

            background-color: #0B111C !important;

            height: auto !important;
            min-height: 100% !important;
            max-height: none !important;

            overflow: visible !important;
            overflow-y: visible !important;
        }

        [data-testid="stMainBlockContainer"] {
            height: auto !important;
            min-height: 100vh !important;
            max-height: none !important;

            overflow: visible !important;

            background: transparent !important;
        }

        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"] {
            background-color: #0B111C !important;
        }

        [data-testid="stSidebar"] {
            height: auto !important;
            min-height: 100vh !important;
            max-height: none !important;

            overflow: visible !important;
            overflow-y: visible !important;

            background:
                linear-gradient(
                    180deg,
                    #111827 0%,
                    #0B101A 100%
                ) !important;
        }

        [data-testid="stSidebar"] > div {
            height: auto !important;
            min-height: 100vh !important;
            max-height: none !important;

            overflow: visible !important;
            overflow-y: visible !important;
        }
        """
    )

    page.evaluate(
        """
        () => {
            const mainContainer =
                document.querySelector('[data-testid="stMain"]');

            const sidebar =
                document.querySelector('[data-testid="stSidebar"]');

            const mainHeight = mainContainer
                ? mainContainer.scrollHeight
                : 0;

            const sidebarHeight = sidebar
                ? sidebar.scrollHeight
                : 0;

            const requiredHeight = Math.max(
                mainHeight,
                sidebarHeight,
                document.body.scrollHeight,
                document.documentElement.scrollHeight,
                window.innerHeight
            );

            document.documentElement.style.height =
                `${requiredHeight}px`;

            document.documentElement.style.minHeight =
                `${requiredHeight}px`;

            document.body.style.height =
                `${requiredHeight}px`;

            document.body.style.minHeight =
                `${requiredHeight}px`;

            document.body.style.backgroundColor =
                '#0B111C';

            if (mainContainer) {
                mainContainer.style.height =
                    `${requiredHeight}px`;

                mainContainer.style.minHeight =
                    `${requiredHeight}px`;

                mainContainer.style.backgroundColor =
                    '#0B111C';
            }

            window.scrollTo(0, 0);
        }
        """
    )

    page.wait_for_timeout(
        800
    )


def capture_dashboard():
    """
    Open the dashboard and capture every main dashboard tab.
    """
    OUTPUT_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True
    )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False
        )

        context = browser.new_context(
            viewport={
                "width": 1920,
                "height": 1080
            },
            device_scale_factor=1,
            color_scheme="dark"
        )

        page = context.new_page()

        page.goto(
            DASHBOARD_URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        page.locator(
            '[data-testid="stAppViewContainer"]'
        ).wait_for(
            state="visible",
            timeout=60000
        )

        page.wait_for_timeout(
            2500
        )

        ensure_sidebar_is_open(
            page
        )

        print()
        print("Dashboard opened.")
        print()
        print(
            "In the browser window:"
        )
        print(
            "1. Select the required filters."
        )
        print(
            "2. Expand or collapse filter groups as required."
        )
        print(
            "3. Set the Data Review Panel to the desired state."
        )
        print(
            "4. Return to this terminal and press Enter."
        )

        input()

        ensure_sidebar_is_open(
            page
        )

        main_tab_list = page.locator(
            '[data-baseweb="tab-list"]'
        ).first

        for tab_number, tab_name in enumerate(
            DASHBOARD_TABS,
            start=1
        ):
            print(
                f"Capturing {tab_name}..."
            )

            tab = main_tab_list.get_by_role(
                "tab",
                name=tab_name,
                exact=True
            )

            tab.click()

            page.wait_for_timeout(
                2500
            )

            ensure_sidebar_is_open(
                page
            )

            scroll_through_dashboard(
                page
            )

            prepare_full_page_layout(
                page
            )

            screenshot_path = (
                OUTPUT_DIRECTORY
                / (
                    f"{tab_number:02d}_"
                    f"{create_file_name(tab_name)}.png"
                )
            )

            page.screenshot(
                path=str(screenshot_path),
                full_page=True,
                animations="disabled"
            )

            print(
                f"Saved: {screenshot_path}"
            )

        browser.close()

    print()
    print("Screenshot capture completed.")
    print(
        f"Files saved to: {OUTPUT_DIRECTORY}"
    )


if __name__ == "__main__":
    capture_dashboard()