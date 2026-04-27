from shbmcp import Server, tool, resource, prompt, Context, require_scopes
from shbmcp import SDKLogger


logger = SDKLogger.get_logger()


server = Server(
    name="standalone-test"
)


@tool(
    name="search_products",
    description="Search product catalog by keyword",
    tags={"catalog", "search", "ecommerce"},
    meta={
        "version": "1.2",
        "owner": "commerce-team",
        "category": "product-api"
    },
    auth=require_scopes("mcp:tools")
)
def search_products(keyword: str, ctx: Context):
    logger.info(ctx)

    auth_info = ctx.request_context.auth if hasattr(ctx.request_context, "auth") else None

    if auth_info:
        scopes = auth_info.get(scope, auth_info.get("scp", []))
        print(scopes)

    return "search_products"


@resource(
    "config://app/settings",
    name="app_settings",
    description="Provides application configuration",
    tags={"config", "system"},
    meta={
        "owner": "platform-team",
        "version": "1.0"
    },
    auth=require_scopes("mcp:tools")
)
def app_settings(ctx: Context):
    logger.info(ctx)
    return "app_settings"


@prompt(
    name="data_analysis_request",
    description="Generate request to analyze dataset",
    tags={"analysis", "data"},
    meta={
        "version": "2.1",
        "author": "data-team"
    },
    auth=require_scopes("mcp:tools")
)
def data_analysis_request(ctx: Context):
    logger.info(ctx)
    return "this is prompt"


app = server.http_app()