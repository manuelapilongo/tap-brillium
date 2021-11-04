"""Brillium tap class."""

from typing import List

from singer_sdk import Stream, Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_brillium.streams import (
    AccountsStream, AssessmentsStream, EmailTemplatesStream, IncompletesStream,
    QuestionGroupsStream, QuestionsStream, RespondentsStream, ResultsStream)

STREAM_TYPES = [
    AccountsStream,
    AssessmentsStream,
    QuestionGroupsStream,
    QuestionsStream,
    EmailTemplatesStream,
    RespondentsStream,
    ResultsStream,
    # CommentsStream,
    IncompletesStream
]


class TapBrillium(Tap):
    """Brillium tap class."""
    name = "tap-brillium"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            description="The key to authenticate against the API service"
        ),
        th.Property(
            "base_uri",
            th.StringType,
            required=True,
            description="The base url for the API service"
        ),
        th.Property(
            "user_agent",
            th.StringType,
            description="User Agent to use for requests"
        ),
        th.Property(
            "api_version",
            th.StringType,
            description="Brillium Api Version. Default to latest available"
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="The earliest record date to sync"
        )
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]
