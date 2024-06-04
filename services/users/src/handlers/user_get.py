import custom_logger
from core_utils.auth_utils.permissions import Permission
from core_utils.enums import Actions, Components, Modules, Subcomponents
from core_utils.http_utils.api_handler import select_tenant_database
from core_utils.http_utils.api_utils import check_api_keys
from core_utils.http_utils.enums import StatusCodes
from core_utils.lambda_utils import lambda_wrapper, polymorphic_event
from core_utils.lambda_utils.models import (
    LambdaContext,
    LambdaEvent,
    LambdaEventResponse,
    LambdaHandler,
)
from core_utils.lambda_utils.models.events import (
    ApiGatewayEvent,
    CognitoEvent,
    DefaultEvent,
    EventBridgeEvent,
    LambdaInvokeEvent,
    S3Event,
    SNSEvent,
    SQSEvent,
    StepFunctionEvent,
)
from core_utils.lambda_utils.models.responses import (
    ApiGawewayEventResponse,
    CognitoEventResponse,
    DefaultEventResponse,
    EventBridgeEventResponse,
    LambdaInvokeEventResponse,
    S3EventResponse,
    SNSEventResponse,
    SQSEventResponse,
    StepFunctionEventResponse,
)
from custom_logger.enums import LoggingLevels
from src.services.user_get import perform
from utils.logger.custom_logger import initialize_logging

initialize_logging()


@polymorphic_event.register
def sqs_event_handler(event: SQSEvent, _: LambdaContext) -> SQSEventResponse:
    custom_logger.log({"event_type": " event from SQS"}, LoggingLevels.INFO)
    return SQSEventResponse([])


@polymorphic_event.register
def api_gateway_event_handler(event: ApiGatewayEvent, _: LambdaContext) -> ApiGawewayEventResponse:
    _, tenant_id = check_api_keys(event.raw_event, validate_tenant=False)
    select_tenant_database(tenant_id)

    user_id, tenant_id = check_api_keys(event.raw_event)
    cognito_user_id = event.path_parameters.get("cognito_user_id")

    authorization = Permission(
        cognito_user_id=user_id,
        tenant_id=tenant_id,
        module=Modules.ADMIN,
        component=Components.USERS,
        subcomponent=Subcomponents.GENERAL,
        action=Actions.CAN_READ,
    )
    authorization.check_permissions()

    user_info = perform(cognito_user_id)

    return ApiGawewayEventResponse(
        status_code=StatusCodes.OK,
        body={"result": "Get user successfully", "user": user_info.model_dump(mode="json")},
    )


@polymorphic_event.register
def lambda_event_handler(event: LambdaInvokeEvent, _: LambdaContext) -> LambdaInvokeEventResponse:
    custom_logger.log({"event_type": " event from Lambda"}, LoggingLevels.INFO)
    return LambdaInvokeEventResponse({"message": "Lambda return message"})


@polymorphic_event.register
def cognito_event_handler(event: CognitoEvent, _: LambdaContext) -> CognitoEventResponse:
    custom_logger.log({"event_type": " event from Cognito"}, LoggingLevels.INFO)
    return CognitoEventResponse({"message": "Lambda return cognito"})


@polymorphic_event.register
def default_event_handler(event: DefaultEvent, _: LambdaContext) -> DefaultEventResponse:
    custom_logger.log({"event_type": " event from Default source"}, LoggingLevels.INFO)
    return DefaultEventResponse({"message": "Lambda return default"})


@polymorphic_event.register
def event_bridge_event_handler(
    event: EventBridgeEvent, _: LambdaContext
) -> EventBridgeEventResponse:
    custom_logger.log({"event_type": " event from EventBridge"}, LoggingLevels.INFO)
    return EventBridgeEventResponse({"message": "Lambda return EventBridge"})


@polymorphic_event.register
def s3_event_handler(event: S3Event, _: LambdaContext) -> S3EventResponse:
    custom_logger.log({"event_type": " event from S3"}, LoggingLevels.INFO)
    return S3EventResponse({"message": "Lambda return S3"})


@polymorphic_event.register
def sns_event_handler(event: SNSEvent, _: LambdaContext) -> SNSEventResponse:
    custom_logger.log({"event_type": " event from SNS"}, LoggingLevels.INFO)
    return SNSEventResponse({"message": "Lambda return SNS"})


@polymorphic_event.register
def step_function_event_handler(
    event: StepFunctionEvent, _: LambdaContext
) -> StepFunctionEventResponse:
    custom_logger.log({"event_type": " event from StepFunction"}, LoggingLevels.INFO)
    return StepFunctionEventResponse({"message": "Lambda return StepFunction"})


def before(event: LambdaEvent, context: LambdaContext):
    print("Before lambda logic")


def after(
    event: LambdaEvent, context: LambdaContext, response: LambdaEventResponse
) -> LambdaEventResponse:
    print("After lambda logic")
    return response


@lambda_wrapper(
    before=before, after=after, transactional=True, event_logging_level=LoggingLevels.INFO
)
def lambda_handler(event: LambdaEvent, context: LambdaContext):
    lambda_handler_creator = LambdaHandler(event, context)
    response = lambda_handler_creator.perform(polymorphic_event)
    return response
