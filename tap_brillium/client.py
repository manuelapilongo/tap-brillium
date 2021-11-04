"""REST client handling, including BrilliumStream base class."""

from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import requests
from singer_sdk.authenticators import BasicAuthenticator
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.streams import RESTStream

MAX_PAGE_SIZE = 1000
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class BrilliumStream(RESTStream):
    """Brillium stream class."""

    # _LOG_REQUEST_METRIC_URLS = True # for testing url in pagination mode

    _page_size: int = MAX_PAGE_SIZE
    data_json_path = None

    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        return self.config.get("base_uri")

    next_page_token_jsonpath = "$.HasMore"
    curr_page_token_jsonpath = "$.Page"

    @property
    def records_jsonpath(self) -> str:
        """Values are usually inside property with endpoint name"""
        path = "$[*]"
        if self.name:
            path = f"$.{self.name}[*]"
        if self.data_json_path:  # in case name differs from json path
            path = f"$.{self.data_json_path}[*]"

        return path

    @property
    def schema_filepath(self) -> str:
        return SCHEMAS_DIR / f"{self.name}.json"

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
            preheader = "application/vnd.ingeniousgroup.testcraftapi"
            headers["Accept"] = f"{preheader}-{self.config.get('api_version')}+json"

        return headers

    @property
    def error_key(self) -> str:
        return self.name.lower()

    def get_next_page_token(
        self, response: requests.Response, previous_token: Optional[Any]
    ) -> Optional[Any]:
        """Return a token for identifying next page or None if no more pages."""
        if response is None:
            return None
        next_page_token = None
        next_page_matches = extract_jsonpath(
            self.next_page_token_jsonpath, response.json()
        )
        next_page = next(iter(next_page_matches), None)
        if next_page is True:
            curr_page_matches = extract_jsonpath(
                self.curr_page_token_jsonpath, response.json()
            )
            curr_page = next(iter(curr_page_matches), None)
            if isinstance(curr_page, int):
                next_page_token = curr_page + 1

        return next_page_token

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization."""
        params: dict = {
            "pagesize": self._page_size
        }
        if next_page_token:
            params["page"] = next_page_token
        if self.replication_key:
            params["sort"] = "asc"
            params["order_by"] = self.replication_key
        return params

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        return {
            "parentId": record["Id"]
        }

    def _sync_children(self, child_context: dict) -> None:
        for child_stream in self.child_streams:
            if child_stream.selected or child_stream.has_selected_descendents:
                if ("ignore_streams" in child_context
                        and child_stream.name in child_context["ignore_streams"]):
                    self.logger.warn(
                        f"Ignoring child {child_stream.name} of "
                        + f"{self.name} Id: {child_context['parentId']}"
                    )
                    continue
                child_stream.sync(context=child_context)

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        return iter([]) if response is None else super().parse_response(response)

    def _request_with_backoff(
        self, prepared_request: requests.PreparedRequest, context: Optional[dict]
    ) -> requests.Response:
        try:
            return super()._request_with_backoff(prepared_request=prepared_request, context=context)
        except RuntimeError as exc:
            self.logger.warn(str(exc))
            if f"No {self.error_key} exist for" not in str(exc):
                raise exc
        return None
