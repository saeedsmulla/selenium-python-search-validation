import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


@pytest.fixture(scope="function")
def setup():
    # Setup Chrome driver
    print("Setting up the browser...")
    driver = webdriver.Chrome()
    driver.maximize_window()

    yield driver
    print("Closing the browser...")
    driver.quit()


def test_search_functionality(setup):
    driver = setup
    wait = WebDriverWait(driver, 10)
    # Expected values
    expected_visible_entries = 5  # Number of filtered entries
    expected_total_entries = 24  # Total entries in the table

    print("Navigating to the Selenium Playground Table Search Demo...")
    # Navigate to the Selenium Playground Table Search Demo
    driver.get("https://www.lambdatest.com/selenium-playground/table-sort-search-demo")
    try:

        print("Waiting for the search box to be visible...")
        # Locate Header
        wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//h1[text()='Table Sorting And Searching']")))
        print("Validating total entries in the table...")
        total_entries = calculate_total_entries(driver)

        search_box = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[type='search']")))
        print("Search box is visible. Entering 'New York' into the search box...")
        search_box.send_keys("New York")
        print("Waiting for table to be visible")
        wait.until(EC.visibility_of_element_located((By.ID, "example")))

        print("Locating visible rows in the table...")
        rows = driver.find_elements(By.XPATH,
                                    "//table[@id='example']/tbody/tr[not(contains(@style, 'display: none'))]")
        visible_rows = [row for row in rows if row.is_displayed()]
        print(f"Number of visible rows found: {len(visible_rows)}")

        # Validating 5 Entries out of 24 enteries
        assert len(
            visible_rows) == expected_visible_entries, f"Expected {expected_visible_entries} rows, but found {len(visible_rows)}."
        assert total_entries == expected_total_entries, f"Expected {expected_total_entries} total entries, but found {total_entries}."

        # Validate the filtered entries text
        validate_filtered_entries_text(driver, expected_visible_entries, expected_total_entries)

        print("Test passed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
        raise


def calculate_total_entries(driver):
    total_entries = 0
    wait = WebDriverWait(driver, 10)

    while True:
        # Wait for the table rows to load on the current page
        rows = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//table[@id='example']/tbody/tr")))

        # Count the rows on the current page and add to total entries
        total_entries += len(rows)
        print(f"Rows on current page: {len(rows)}, Total so far: {total_entries}")

        # Check if the "Next" button is enabled
        next_button = driver.find_element(By.XPATH, "//a[contains(@class, 'paginate_button next')]")
        if "disabled" in next_button.get_attribute("class"):
            print("No more pages to navigate.")
            break  # Exit the loop if the "Next" button is disabled

        # Click the "Next" button to go to the next page
        print("Navigating to the next page...")
        next_button.click()

    print(f"Total entries across all pages: {total_entries}")
    return total_entries


def validate_filtered_entries_text(driver, expected_visible, expected_total):
    # Wait for the element that displays the entry text
    wait = WebDriverWait(driver, 10)
    entry_text_element = wait.until(EC.visibility_of_element_located((By.ID, "example_info")))

    # Extract the full text
    entry_text = entry_text_element.text
    print(f"Full entry text displayed: '{entry_text}'")

    # Parse the portion "5 entries filtered from 24 total entries"
    import re
    match = re.search(r"(\d+) entries .*?filtered from (\d+) total entries", entry_text)
    if not match:
        raise AssertionError(f"Unexpected text format: {entry_text}")

    visible_entries = int(match.group(1))
    total_entries = int(match.group(2))

    print(f"Parsed values: Visible={visible_entries}, Total={total_entries}")

    # Validate visible and total entries
    assert visible_entries == expected_visible, f"Expected {expected_visible} visible entries, but found {visible_entries}"
    assert total_entries == expected_total, f"Expected {expected_total} total entries, but found {total_entries}"

    print("Filtered entries validation passed!")
