"""Stream type classes for tap-brillium."""

from pathlib import Path
from typing import Optional

from tap_brillium.client import SCHEMAS_DIR, BrilliumStream

class AccountsStream(BrilliumStream):
    name = "Accounts"
    path = "/Accounts"
    schema_filepath = SCHEMAS_DIR / "Accounts.json"
    primary_keys = ["Id"]
    replication_method = 'INCREMENTAL'
    valid_replication_keys = ['DateModified']
    replication_key = 'DateModified'

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""

        return {
            "assessments_path":
                record["RelatedUris"]["Assessments"].replace(self.url_base, ""),
            "respondents_path":
                record["RelatedUris"]["Respondents"].replace(self.url_base, ""),
            "email_templates_path":
                record["RelatedUris"]["EmailTemplates"].replace(self.url_base, "")
        }

class EmailTemplatesStream(BrilliumStream):
    name = "EmailTemplates"
    parent_stream_type = AccountsStream
    path = "/{email_templates_path}"
    schema_filepath = SCHEMAS_DIR / "EmailTemplates.json"
    primary_keys = ["Id"]
    replication_method = 'INCREMENTAL'
    valid_replication_keys = ['DateModified']
    replication_key = 'DateModified'

class AssessmentsStream(BrilliumStream):
    name = "Assessments"
    parent_stream_type = AccountsStream
    path = "/{assessments_path}"
    schema_filepath = SCHEMAS_DIR / "Assessments.json"
    primary_keys = ["Id"]
    replication_method = 'INCREMENTAL'
    valid_replication_keys = ['DateModified']
    replication_key = 'DateModified'

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""

        result = super().get_child_context(record, context)
        result.update({
            "ignore_streams": ["Questions"] if record["Active"] == "Archived" else [],
            "question_groups_path":
                record["RelatedUris"]["QuestionGroups"].replace(self.url_base, ""),
            "questions_path":
                record["RelatedUris"]["Questions"].replace(self.url_base, ""),
            "respondents_path":
                record["RelatedUris"]["Respondents"].replace(self.url_base, ""),
            "incompletes_path":
                record["RelatedUris"]["Incompletes"].replace(self.url_base, ""),
            "invitations_path":
                record["RelatedUris"]["Invitations"].replace(self.url_base, ""),
        })
        return result

class QuestionGroupsStream(BrilliumStream):
    name = "QuestionGroups"
    parent_stream_type = AssessmentsStream
    path = "/{question_groups_path}"
    schema_filepath = SCHEMAS_DIR / "QuestionGroups.json"
    primary_keys = ["Id"]
    replication_method = 'INCREMENTAL'
    valid_replication_keys = ['DateModified']
    replication_key = 'DateModified'

class QuestionsStream(BrilliumStream):
    name = "Questions"
    parent_stream_type = AssessmentsStream
    path = "/{questions_path}"
    schema_filepath = SCHEMAS_DIR / "Questions.json"
    primary_keys = ["Id"]
    valid_replication_keys = None
    replication_key = None
