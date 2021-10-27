"""REST client handling, including BrilliumStream base class."""

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Union

import requests
from memoization import cached
from singer_sdk.authenticators import BasicAuthenticator
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream

from tap_brillium.streams import MAX_PAGE_SIZE

SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class BrilliumStream(RESTStream):
    """Brillium stream class."""

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config.get("base_uri")

    records_jsonpath = "$[*]"  # Or override `parse_response`.
    next_page_token_jsonpath = "$.HasMore"
    curr_page_token_jsonpath = "$.Page"

    @property
    def authenticator(self) -> BasicAuthenticator:
        """Return a new authenticator object."""
        return BasicAuthenticator.create_for_stream(
            self,
            username=self.config.get("api_key"),
            password="x"
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")
        if "api_version" in self.config:
            headers["Accept"] = f"application/vnd.ingeniousgroup.testcraftapi-{self.config.get('api_version')}+json"

        return headers

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        next_page_token = None
        next_page_matches = extract_jsonpath(
            self.next_page_token_jsonpath, response.json()
        )
        next_page = next(iter(next_page_matches), None)
        if next_page == True:
            curr_page_matches = extract_jsonpath(
                self.curr_page_token_jsonpath, response.json()
            )
            curr_page = next(iter(curr_page_matches), None)
            if type(curr_page) == int:
                next_page_token = curr_page + 1

        return next_page_token

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {
            "pagesize": MAX_PAGE_SIZE
        }
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
        return params
