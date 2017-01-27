"""
Receipt page
"""
import time

from bok_choy.page_object import PageObject

from regression.pages.common.utils import (
    convert_date_format,
    extract_numerical_value_from_price_string
)
from regression.pages.whitelabel.const import (
    SHORT_TIME_OUT_LIMIT,
    WAIT_TIME,
    INITIAL_WAIT_TIME
)
from regression.pages.whitelabel.dashboard_page import DashboardPage


class ReceiptException(Exception):
    """
    Catch failures in receipt page
    """

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class ReceiptPage(PageObject):
    """
    Receipt
    """

    url = None

    def is_browser_on_page(self):
        """
        Is browser on the page?
        Raises:
            True if receipt report is present on the page:
        """
        return self.q(css='.container').present

    def is_receipt_displayed(self):
        """
        This is a temporary work around due to the fact that sometimes the
        receipt pages shows and error, however on refreshing the page it
        starts showing original receipt
        Returns:
            True if receipt is found:
        """
        found = False
        t_end = time.time() + SHORT_TIME_OUT_LIMIT
        # Run the loop for a pre defined time
        current_url = self.browser.current_url
        while time.time() < t_end:
            time.sleep(INITIAL_WAIT_TIME)
            try:
                if not self.q(
                        css='#receipt-container'
                ).is_present():
                    raise ReceiptException
                found = True
                break
            except ReceiptException:
                time.sleep(WAIT_TIME)
                self.browser.get(current_url)
                self.wait_for_page()
        if found:
            return True

    @property
    def order_num(self):
        """
        Get the order number from receipt
        Returns:
            order number:
        """
        return self.q(
            css='.order-summary>dl>dd:nth-of-type(1)').text[0]

    @property
    def order_desc(self):
        """
        Get the order description from receipt
        Returns:
            order description:
        """
        return self.q(
            css='.course-description>span').text[0]

    @property
    def order_date(self):
        """
        Get the order date from receipt
        Raises:
            order date:
        """
        date_string = self.q(
            xpath=".//*[@id='receipt-container']//dt[text()='Order Date:']"
                  "/following-sibling::dd"
        ).text[0]
        return convert_date_format(
            date_string,
            '%B %d, %Y',
            '%Y-%m-%d'
        )

    @property
    def order_amount(self):
        """
        Get the order amount from receipt
        Returns:
            order amount:
        """
        amount = self.q(
            css='.line-price.price'
        ).text[0]
        return extract_numerical_value_from_price_string(amount)

    @property
    def total_amount(self):
        """
        Get the total amount
        Returns:
            total amount:
        """
        total_amount = self.q(
            css='.order-total:nth-of-type(2)>.price').text[0]
        return extract_numerical_value_from_price_string(total_amount)

    @property
    def billed_to(self):
        """
        Get the information about the person to whom it is billed
        Returns:
            billed_to_info:
        """
        return self.q(css='.confirm-message>a').text[0]

    def go_to_dashboard(self):
        """
        Go to user dashboard page by clicking on Go to Dashboard button
        """
        self.q(css='.dashboard-link.nav-link').click()
        DashboardPage(self.browser).wait_for_page()
