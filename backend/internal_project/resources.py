import json
import os

from dotenv import load_dotenv

from vinyl.lib.asset import resource
from vinyl.lib.connect import (
    BigQueryConnector,
    DatabaseFileConnector,
    FileConnector,
    PostgresConnector,
    SnowflakeConnector,
)

load_dotenv()


@resource
def local_filesystem():
    return FileConnector(path="data/csvs")


@resource
def local_parquet():
    return FileConnector(path="data/parquets")


@resource
def local_json():
    return FileConnector(path="data/jsons")


@resource
def local_duckdb():
    return DatabaseFileConnector(path="../vinyl/tests/fixtures/test.duckdb")


@resource
def supabase_copilot_postgres():
    return PostgresConnector(
        host="aws-0-us-east-1.pooler.supabase.com",
        port="5432",
        user=os.getenv("SUPABASE_COPILOT_USER"),
        password=os.getenv("SUPABASE_COPILOT_PASSWORD"),
        tables=["postgres.public.*"],
    )


@resource
def dbt_bigquery():
    return BigQueryConnector(
        service_account_info=json.loads(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS").replace("\n", "\\n")
        ),
        tables=["analytics-dev-372514.dbt_itracey.companies"],
    )


@resource
def dbt_snowflake():
    return SnowflakeConnector(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        tables=["ANALYTICS.MIXPANEL.EVENT"],
    )


# @resource
# def dbt_turntable_dbt():
#     return DBTConnectorFull(
#         dbt_project_dir="../../turntable_dbt/",
#         dialect=DBTDialect.BIGQUERY,
#         version=DBTVersion.V1_5,
#         tables=[
#             "analytics-dev-372514.plausible.stats_timeseries_results",
#             "analytics-dev-372514.linkedin_company_pages.comment_history",
#             "analytics-dev-372514.linkedin_company_pages.comment_on_ugc_post",
#             "analytics-dev-372514.linkedin_company_pages.comment_social_metadata_summary",
#             "analytics-dev-372514.linkedin_company_pages.country",
#             "analytics-dev-372514.linkedin_company_pages.followers_by_association_type",
#             "analytics-dev-372514.linkedin_company_pages.followers_by_function",
#             "analytics-dev-372514.linkedin_company_pages.followers_by_industry",
#             "analytics-dev-372514.linkedin_company_pages.followers_by_seniority",
#             "analytics-dev-372514.linkedin_company_pages.followers_by_staff_count_range",
#             "analytics-dev-372514.linkedin_company_pages.function",
#             "analytics-dev-372514.linkedin_company_pages.industry",
#             "analytics-dev-372514.linkedin_company_pages.organization",
#             "analytics-dev-372514.linkedin_company_pages.organization_followers_by_association_type",
#             "analytics-dev-372514.linkedin_company_pages.organization_followers_by_function",
#             "analytics-dev-372514.linkedin_company_pages.organization_followers_by_industry",
#             "analytics-dev-372514.linkedin_company_pages.organization_followers_by_seniority",
#             "analytics-dev-372514.linkedin_company_pages.organization_followers_by_staff_count_range",
#             "analytics-dev-372514.linkedin_company_pages.organization_industries",
#             "analytics-dev-372514.linkedin_company_pages.organization_page_statistic_by_country",
#             "analytics-dev-372514.linkedin_company_pages.organization_page_statistic_by_function",
#             "analytics-dev-372514.linkedin_company_pages.organization_page_statistic_by_industry",
#             "analytics-dev-372514.linkedin_company_pages.organization_page_statistic_by_region",
#             "analytics-dev-372514.linkedin_company_pages.organization_page_statistic_by_seniority",
#             "analytics-dev-372514.linkedin_company_pages.organization_page_statistic_by_staff_count_range",
#             "analytics-dev-372514.linkedin_company_pages.organization_share",
#             "analytics-dev-372514.linkedin_company_pages.organization_time_bound_follower_statistic",
#             "analytics-dev-372514.linkedin_company_pages.organization_time_bound_page_statistic",
#             "analytics-dev-372514.linkedin_company_pages.organization_time_bound_share_statistic",
#             "analytics-dev-372514.linkedin_company_pages.organization_total_follower_statistic",
#             "analytics-dev-372514.linkedin_company_pages.organization_total_page_statistic",
#             "analytics-dev-372514.linkedin_company_pages.organization_total_share_statistic",
#             "analytics-dev-372514.linkedin_company_pages.page_statistic_by_country",
#             "analytics-dev-372514.linkedin_company_pages.page_statistic_by_function",
#             "analytics-dev-372514.linkedin_company_pages.page_statistic_by_industry",
#             "analytics-dev-372514.linkedin_company_pages.page_statistic_by_region",
#             "analytics-dev-372514.linkedin_company_pages.page_statistic_by_seniority",
#             "analytics-dev-372514.linkedin_company_pages.page_statistic_by_staff_count_range",
#             "analytics-dev-372514.linkedin_company_pages.region",
#             "analytics-dev-372514.linkedin_company_pages.seniority",
#             "analytics-dev-372514.linkedin_company_pages.share_content",
#             "analytics-dev-372514.linkedin_company_pages.share_history",
#             "analytics-dev-372514.linkedin_company_pages.share_share_statistic",
#             "analytics-dev-372514.linkedin_company_pages.share_statistic",
#             "analytics-dev-372514.linkedin_company_pages.social_metadata_summary",
#             "analytics-dev-372514.linkedin_company_pages.time_bound_follower_statistic",
#             "analytics-dev-372514.linkedin_company_pages.time_bound_page_statistic",
#             "analytics-dev-372514.linkedin_company_pages.time_bound_share_statistic",
#             "analytics-dev-372514.linkedin_company_pages.total_follower_statistic",
#             "analytics-dev-372514.linkedin_company_pages.total_page_statistic",
#             "analytics-dev-372514.linkedin_company_pages.total_share_statistic",
#             "analytics-dev-372514.linkedin_company_pages.ugc_post_social_metadata_summary",
#             "analytics-dev-372514.pipedrive.activity",
#             "analytics-dev-372514.pipedrive.activity_participant",
#             "analytics-dev-372514.pipedrive.activity_type",
#             "analytics-dev-372514.pipedrive.currency",
#             "analytics-dev-372514.pipedrive.deal_history",
#             "analytics-dev-372514.pipedrive.email_bcc",
#             "analytics-dev-372514.pipedrive.email_cc",
#             "analytics-dev-372514.pipedrive.email_to",
#             "analytics-dev-372514.pipedrive.file",
#             "analytics-dev-372514.pipedrive.filter",
#             "analytics-dev-372514.pipedrive.filter_helper",
#             "analytics-dev-372514.pipedrive.fivetran_audit",
#             "analytics-dev-372514.pipedrive.lead_history",
#             "analytics-dev-372514.pipedrive.lead_label_history",
#             "analytics-dev-372514.pipedrive.lead_lead_label",
#             "analytics-dev-372514.pipedrive.lead_source",
#             "analytics-dev-372514.pipedrive.mail_message",
#             "analytics-dev-372514.pipedrive.mail_thread",
#             "analytics-dev-372514.pipedrive.note",
#             "analytics-dev-372514.pipedrive.organization",
#             "analytics-dev-372514.pipedrive.person",
#             "analytics-dev-372514.pipedrive.person_email",
#             "analytics-dev-372514.pipedrive.person_phone",
#             "analytics-dev-372514.pipedrive.pipeline",
#             "analytics-dev-372514.pipedrive.product",
#             "analytics-dev-372514.pipedrive.product_deal",
#             "analytics-dev-372514.pipedrive.role",
#             "analytics-dev-372514.pipedrive.stage",
#             "analytics-dev-372514.pipedrive.user",
#             "analytics-dev-372514.linear.issues",
#             "analytics-dev-372514.quickbooks_quickbooks.quickbooks__balance_sheet",
#             "analytics-dev-372514.quickbooks_quickbooks.quickbooks__expenses_sales_enhanced",
#             "analytics-dev-372514.quickbooks_quickbooks.quickbooks__general_ledger",
#             "analytics-dev-372514.quickbooks_quickbooks.quickbooks__general_ledger_by_period",
#             "analytics-dev-372514.quickbooks_quickbooks.quickbooks__profit_and_loss",
#             "analytics-dev-372514.mixpanel.event",
#             "analytics-dev-372514.mixpanel.fivetran_audit",
#             "analytics-dev-372514.mixpanel.people",
#             "analytics-dev-372514.supabase_public.inferences",
#             "analytics-dev-372514.supabase_public.responses",
#             "analytics-dev-372514.supabase_public.waitlist",
#             "analytics-dev-372514.hubspot_hubspot.hubspot__companies",
#             "analytics-dev-372514.hubspot_hubspot.hubspot__company_history",
#             "analytics-dev-372514.hubspot_hubspot.hubspot__contact_history",
#             "analytics-dev-372514.hubspot_hubspot.hubspot__contact_lists",
#             "analytics-dev-372514.hubspot_hubspot.hubspot__contacts",
#             "analytics-dev-372514.hubspot_hubspot.hubspot__deal_history",
#             "analytics-dev-372514.hubspot_hubspot.hubspot__deal_stages",
#             "analytics-dev-372514.hubspot_hubspot.hubspot__deals",
#             "analytics-dev-372514.hubspot_hubspot.hubspot__engagement_calls",
#             "analytics-dev-372514.hubspot_hubspot.hubspot__engagement_emails",
#             "analytics-dev-372514.hubspot_hubspot.hubspot__engagement_meetings",
#             "analytics-dev-372514.hubspot_hubspot.hubspot__engagement_notes",
#             "analytics-dev-372514.hubspot_hubspot.hubspot__engagement_tasks",
#             "analytics-dev-372514.hubspot_hubspot.hubspot__engagements",
#             "analytics-dev-372514.hubspot_hubspot.int_hubspot__contact_merge_adjust",
#             "analytics-dev-372514.github.asset",
#             "analytics-dev-372514.github.branch_commit_relation",
#             "analytics-dev-372514.github.commit",
#             "analytics-dev-372514.github.commit_file",
#             "analytics-dev-372514.github.commit_parent",
#             "analytics-dev-372514.github.commit_pull_request",
#             "analytics-dev-372514.github.deployment",
#             "analytics-dev-372514.github.deployment_status",
#             "analytics-dev-372514.github.github__daily_metrics",
#             "analytics-dev-372514.github.github__issues",
#             "analytics-dev-372514.github.github__monthly_metrics",
#             "analytics-dev-372514.github.github__pull_requests",
#             "analytics-dev-372514.github.github__quarterly_metrics",
#             "analytics-dev-372514.github.github__weekly_metrics",
#             "analytics-dev-372514.github.issue",
#             "analytics-dev-372514.github.issue_assignee",
#             "analytics-dev-372514.github.issue_assignee_history",
#             "analytics-dev-372514.github.issue_closed_history",
#             "analytics-dev-372514.github.issue_comment",
#             "analytics-dev-372514.github.issue_label",
#             "analytics-dev-372514.github.issue_label_history",
#             "analytics-dev-372514.github.issue_mention",
#             "analytics-dev-372514.github.issue_merged",
#             "analytics-dev-372514.github.issue_referenced",
#             "analytics-dev-372514.github.issue_renamed",
#             "analytics-dev-372514.github.label",
#             "analytics-dev-372514.github.pull_request",
#             "analytics-dev-372514.github.pull_request_ready_for_review_history",
#             "analytics-dev-372514.github.pull_request_review",
#             "analytics-dev-372514.github.pull_request_review_comments",
#             "analytics-dev-372514.github.release",
#             "analytics-dev-372514.github.repository",
#             "analytics-dev-372514.github.requested_reviewer_history",
#             "analytics-dev-372514.github.security_advisory",
#             "analytics-dev-372514.github.security_advisory_cwe",
#             "analytics-dev-372514.github.security_advisory_vulnerability",
#             "analytics-dev-372514.github.security_alert",
#             "analytics-dev-372514.github.security_cwe",
#             "analytics-dev-372514.github.security_reference",
#             "analytics-dev-372514.github.security_vulnerability",
#             "analytics-dev-372514.github.stg_github__issue",
#             "analytics-dev-372514.github.stg_github__issue_assignee",
#             "analytics-dev-372514.github.stg_github__issue_assignee_tmp",
#             "analytics-dev-372514.github.stg_github__issue_closed_history",
#             "analytics-dev-372514.github.stg_github__issue_closed_history_tmp",
#             "analytics-dev-372514.github.stg_github__issue_comment",
#             "analytics-dev-372514.github.stg_github__issue_comment_tmp",
#             "analytics-dev-372514.github.stg_github__issue_label",
#             "analytics-dev-372514.github.stg_github__issue_label_tmp",
#             "analytics-dev-372514.github.stg_github__issue_merged",
#             "analytics-dev-372514.github.stg_github__issue_merged_tmp",
#             "analytics-dev-372514.github.stg_github__issue_tmp",
#             "analytics-dev-372514.github.stg_github__label",
#             "analytics-dev-372514.github.stg_github__label_tmp",
#             "analytics-dev-372514.github.stg_github__pull_request",
#             "analytics-dev-372514.github.stg_github__pull_request_review",
#             "analytics-dev-372514.github.stg_github__pull_request_review_tmp",
#             "analytics-dev-372514.github.stg_github__pull_request_tmp",
#             "analytics-dev-372514.github.stg_github__repository",
#             "analytics-dev-372514.github.stg_github__repository_tmp",
#             "analytics-dev-372514.github.stg_github__requested_reviewer_history",
#             "analytics-dev-372514.github.stg_github__requested_reviewer_history_tmp",
#             "analytics-dev-372514.github.stg_github__user",
#             "analytics-dev-372514.github.stg_github__user_tmp",
#             "analytics-dev-372514.github.user",
#             "analytics-dev-372514.github.user_email",
#             "analytics-dev-372514.github.workflow",
#             "analytics-dev-372514.github.task",
#             "analytics-dev-372514.github.task_pull_request",
#             "analytics-dev-372514.posthog.data_attribute",
#             "analytics-dev-372514.posthog.event",
#             "analytics-dev-372514.posthog.insight",
#             "analytics-dev-372514.posthog.person",
#             "analytics-dev-372514.posthog.person_name",
#             "analytics-dev-372514.posthog.project",
#             "analytics-dev-372514.posthog.test_account_filter",
#             "analytics-dev-372514.posthog.users",
#         ],
#     )
