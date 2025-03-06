var temp = {
  "openapi": "3.1.0",
  "info": {
    "title": "API Documentation",
    "description": "Development Server",
    "termsOfService": "http://example.com/terms/",
    "contact": {
      "name": "API Documentation",
      "email": "api-documentation@example.com"
    },
    "license": {
      "name": "MIT License",
      "url": "https://opensource.org/licenses/MIT"
    },
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://htxoulxfxc.execute-api.us-east-2.amazonaws.com/dev"
    }
  ],
  "paths": {
    "/queues": {
      "get": {
        "tags": [
          "Queues"
        ],
        "summary": "Get Queues",
        "description": "Get Queues",
        "responses": {
          "200": {
            "description": "Queues retrieved successfully.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/GetQueuesSuccessResponse"
                }
              }
            }
          },
          "500": {
            "description": "Internal Code Error.",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          }
        },
        "security": [
          {
            "bearer": [
              "aws.cognito.signin.user.admin"
            ]
          },
          {
            "appKey": [],
            "oauth2": [
              "apiauthidentifier/json.read"
            ],
            "tenant_id": []
          },
          {
            "tenantKey": [],
            "oauth2": [
              "apiauthidentifier/json.read"
            ]
          }
        ]
      }
    }
  },
  "components": {
    "schemas": {
      "DueDateRelative": {
        "properties": {
          "value": {
            "type": "integer",
            "title": "Value",
            "description": "Numeric value for the relative due date"
          },
          "unit": {
            "type": "string",
            "title": "Unit",
            "description": "Time unit for the due date, e.g., 'days'"
          }
        },
        "type": "object",
        "required": [
          "value",
          "unit"
        ],
        "title": "DueDateRelative"
      },
      "ErrorResponse": {
        "properties": {
          "code": {
            "type": "string",
            "title": "Code",
            "description": "Code error, format: {Service}.{CodeError}"
          },
          "message": {
            "type": "string",
            "title": "Message",
            "description": "Message error."
          },
          "correlation_id": {
            "type": "string",
            "title": "Correlation Id",
            "description": "Process UUID."
          }
        },
        "type": "object",
        "required": [
          "code",
          "message",
          "correlation_id"
        ],
        "title": "ErrorResponse"
      },
      "GetQueuesSuccessResponse": {
        "properties": {
          "result": {
            "type": "string",
            "title": "Result",
            "description": "Response description."
          },
          "correlation_id": {
            "type": "string",
            "title": "Correlation Id",
            "description": "Process UUID."
          },
          "atm_queues": {
            "items": {
              "anyOf": [
                {
                  "$ref": "#/components/schemas/QueueObject"
                },
                {
                  "type": "null"
                }
              ]
            },
            "type": "array",
            "title": "Atm Queues",
            "description": "Queues List"
          }
        },
        "type": "object",
        "required": [
          "result",
          "correlation_id",
          "atm_queues"
        ],
        "title": "GetQueuesSuccessResponse"
      },
      "Label": {
        "properties": {
          "atm_label_id": {
            "type": "string",
            "title": "Atm Label Id",
            "description": "Unique identifier for the label"
          },
          "name": {
            "type": "string",
            "title": "Name",
            "description": "Label name"
          }
        },
        "type": "object",
        "required": [
          "atm_label_id",
          "name"
        ],
        "title": "Label"
      },
      "QueueObject": {
        "properties": {
          "atm_queue_id": {
            "type": "string",
            "title": "Atm Queue Id",
            "description": "Unique queue identifier"
          },
          "created_at": {
            "type": "string",
            "title": "Created At",
            "description": "Creation timestamp"
          },
          "is_active": {
            "type": "boolean",
            "title": "Is Active",
            "description": "Indicates if the queue is active"
          },
          "is_live": {
            "type": "boolean",
            "title": "Is Live",
            "description": "Indicates if the queue is live"
          },
          "queue_name": {
            "type": "string",
            "title": "Queue Name",
            "description": "Queue name"
          },
          "description": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Description",
            "description": "Queue description",
            "default": ""
          },
          "task_summary": {
            "type": "string",
            "title": "Task Summary",
            "description": "Task summary"
          },
          "task_instruction": {
            "type": "string",
            "title": "Task Instruction",
            "description": "Task instructions"
          },
          "manual_assignment": {
            "type": "boolean",
            "title": "Manual Assignment",
            "description": "Indicates if assignment is manual"
          },
          "advanced_priority": {
            "type": "boolean",
            "title": "Advanced Priority",
            "description": "Indicates if advanced priority is enabled"
          },
          "priority": {
            "type": "number",
            "title": "Priority",
            "description": "Priority value"
          },
          "task_type": {
            "type": "string",
            "title": "Task Type",
            "description": "Task type identifier"
          },
          "task_name": {
            "type": "string",
            "title": "Task Name",
            "description": "Task name"
          },
          "max_snooze_time": {
            "type": "number",
            "title": "Max Snooze Time",
            "description": "Maximum snooze time"
          },
          "due_date_relative": {
            "allOf": [
              {
                "$ref": "#/components/schemas/DueDateRelative"
              }
            ],
            "description": "Relative due date information"
          },
          "escalation_queue": {
            "type": "boolean",
            "title": "Escalation Queue",
            "description": "Indicates if the queue is an escalation queue"
          },
          "assignee_level": {
            "type": "string",
            "title": "Assignee Level",
            "description": "Assignee level identifier"
          },
          "trigger_type": {
            "type": "string",
            "title": "Trigger Type",
            "description": "Trigger type identifier"
          },
          "trigger_name": {
            "type": "string",
            "title": "Trigger Name",
            "description": "Trigger name"
          },
          "labels": {
            "items": {
              "$ref": "#/components/schemas/Label"
            },
            "type": "array",
            "title": "Labels",
            "description": "List of associated labels"
          },
          "process": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Process",
            "description": "Associated process (can be null)"
          },
          "flow_id": {
            "type": "string",
            "title": "Flow Id",
            "description": "Flow identifier"
          },
          "filevine_project_type_id": {
            "type": "string",
            "title": "Filevine Project Type Id",
            "description": "Filevine project type identifier"
          },
          "triggered_by": {
            "allOf": [
              {
                "$ref": "#/components/schemas/TriggeredBy"
              }
            ],
            "description": "Information about who or what triggered the action"
          },
          "instance_created": {
            "type": "integer",
            "title": "Instance Created",
            "description": "Instance creation count"
          },
          "atm_timezone_configuration_id": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Atm Timezone Configuration Id",
            "description": "Timezone configuration identifier"
          }
        },
        "type": "object",
        "required": [
          "atm_queue_id",
          "created_at",
          "is_active",
          "is_live",
          "queue_name",
          "task_summary",
          "task_instruction",
          "manual_assignment",
          "advanced_priority",
          "priority",
          "task_type",
          "task_name",
          "max_snooze_time",
          "due_date_relative",
          "escalation_queue",
          "assignee_level",
          "trigger_type",
          "trigger_name",
          "labels",
          "flow_id",
          "filevine_project_type_id",
          "triggered_by",
          "instance_created"
        ],
        "title": "QueueObject"
      },
      "TriggeredBy": {
        "properties": {
          "target_queue_id": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Target Queue Id",
            "description": "Source queue identifier for the trigger"
          },
          "queue_name": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Queue Name",
            "description": "Source queue name for the trigger"
          }
        },
        "type": "object",
        "required": [
          "target_queue_id",
          "queue_name"
        ],
        "title": "TriggeredBy"
      }
    },
    "securitySchemes": {
      "bearer": {
        "type": "http",
        "scheme": "bearer"
      },
      "appKey": {
        "type": "apiKey",
        "name": "App-Key",
        "in": "header"
      },
      "oauth2": {
        "type": "oauth2",
        "flows": {
          "clientCredentials": {
            "authorizationUrl": "http://example.com/auth/authorize",
            "tokenUrl": "https://pocbackendcoredevappkeys.auth.us-east-2.amazoncognito.com/oauth2/token",
            "refreshUrl": "http://example.com/auth/refresh",
            "scopes": {
              "apiauthidentifier/json.read": ""
            }
          }
        }
      },
      "tenant_id": {
        "type": "apiKey",
        "name": "tenant_id",
        "in": "header"
      },
      "tenantKey": {
        "type": "apiKey",
        "name": "Tenant-Key",
        "in": "header"
      }
    }
  },
  "tags": [
    {
      "name": "Queues"
    }
  ]
}