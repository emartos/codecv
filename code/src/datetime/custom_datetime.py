from datetime import datetime
from typing import Dict, Optional


class CustomDatetime:

    def process_input_dates(
        self, start_date: Optional[str] = None, end_date: Optional[str] = None
    ) -> Dict[str, Optional[datetime]]:
        """
        Validates and converts input dates into datetime objects.

        Ensures that the provided `start_date` and `end_date` are in the "YYYY-MM-DD" format,
        and verifies that the `start_date`, if specified, is earlier than or equal to the `end_date`.
        Returns a dictionary with parsed datetime objects or None if dates are not provided.

        Args:
           start_date (Optional[str]): The start date in "YYYY-MM-DD" format. Defaults to None.
           end_date (Optional[str]): The end date in "YYYY-MM-DD" format. Defaults to None.

        Returns:
           Dict[str, Optional[datetime]]: A dictionary containing:
               - 'start_date': A datetime object for the start date, or None if not provided.
               - 'end_date': A datetime object for the end date, or None if not provided.

        Raises:
           ValueError: If the dates are incorrectly formatted, or if `start_date` is later than `end_date`.
        """
        start_date_obj = None
        end_date_obj = None

        # Process START_DATE, if provided
        if start_date:
            start_date_obj = self._validate_input_date(start_date)

        # Process END_DATE, if provided
        if end_date:
            end_date_obj = self._validate_input_date(end_date)

        # Check that START_DATE is earlier than END_DATE
        if start_date_obj and end_date_obj and start_date_obj > end_date_obj:
            raise ValueError(
                f"❌ Invalid date range: start date '{start_date}' must be earlier than end date '{end_date}'."
            )

        return {
            "start_date": start_date_obj,
            "end_date": end_date_obj,
        }

    def validate_date_format(self, format: str) -> None:
        """
        Validates a date format string by attempting to format the current date.

        Args:
            format (str): The date format string to validate.

        Raises:
            ValueError: If the format is invalid.
        """
        try:
            datetime.now().strftime(format)
        except ValueError:
            raise ValueError(f"❌ Invalid date format: '{format}'.")

    def _validate_input_date(self, date) -> Optional[datetime]:
        """
        Validates and converts a date string into a datetime object.

        Verifies that the provided date string is in the "YYYY-MM-DD" format. If the format is invalid,
        a `ValueError` is raised. Returns the corresponding `datetime` object if the format is valid.

        Args:
           date (str): The date string to validate, in "YYYY-MM-DD" format.

        Returns:
           datetime: The validated and parsed datetime object.

        Raises:
           ValueError: If the date string is not in the valid "YYYY-MM-DD" format.
        """
        if not date:
            return None

        try:
            return datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError(f"❌ Invalid date: '{date}'. Use the YYYY-MM-DD format.")
