# API Documentation: [API Name]

## Metadata

| Field         | Value                                       |
|---------------|---------------------------------------------|
| Date          | [YYYY-MM-DD]                                |
| Owner         | [Name / team responsible for this API]       |
| Related links | [OpenAPI spec, repo, architecture docs]      |
| Status        | Draft / Reviewed / Approved                 |

## Overview

*What this API does and who it is for.*

[1-2 sentences describing the API's purpose and primary consumers.]

## Base URL

| Environment | Base URL |
|-------------|----------|
| Production  | [https://api.example.com/v1] |
| Staging     | [https://api-staging.example.com/v1] |

## Authentication

*How to authenticate requests.*

- **Method**: [API key / Bearer token / OAuth 2.0 / other]
- **Header**: [e.g., Authorization: Bearer {token}]
- **How to obtain credentials**: [Process or link to credential management]

## Rate Limits

| Tier | Requests per Minute | Burst Limit |
|------|-------------------|-------------|
| [Default] | [60] | [10] |

*Rate limit headers returned*: [e.g., X-RateLimit-Remaining, X-RateLimit-Reset]

## Common Headers

| Header | Value | Required | Description |
|--------|-------|----------|-------------|
| [Content-Type] | [application/json] | Yes | [Request body format] |
| [Accept] | [application/json] | No | [Response format] |
| [X-Request-ID] | [UUID] | No | [Client-generated request tracking ID] |

## Endpoints Summary

| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| [GET] | [/resources] | [List all resources] | [Yes] |
| [GET] | [/resources/{id}] | [Get a single resource] | [Yes] |
| [POST] | [/resources] | [Create a new resource] | [Yes] |
| [PUT] | [/resources/{id}] | [Update a resource] | [Yes] |
| [DELETE] | [/resources/{id}] | [Delete a resource] | [Yes] |

---

## Endpoint Details

### [GET /resources]

*[Description of what this endpoint does.]*

**Parameters**

| Name | In | Type | Required | Description |
|------|----|------|----------|-------------|
| [page] | query | integer | No | [Page number for pagination, default 1] |
| [limit] | query | integer | No | [Items per page, default 20, max 100] |
| [filter] | query | string | No | [Filter expression] |

**Request Example**

```
[GET /resources?page=1&limit=20]
```

**Response Example (200 OK)**

```json
[Paste or describe the response body structure]
```

**Error Responses**

| Status | Description | Body |
|--------|-------------|------|
| [401] | [Unauthorized -- invalid or missing credentials] | [Error body example] |
| [429] | [Rate limit exceeded] | [Error body example] |

---

### [POST /resources]

*[Description of what this endpoint does.]*

**Request Body**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| [name] | string | Yes | [Resource name] |
| [description] | string | No | [Resource description] |

**Request Example**

```json
[Paste or describe the request body]
```

**Response Example (201 Created)**

```json
[Paste or describe the response body]
```

**Error Responses**

| Status | Description | Body |
|--------|-------------|------|
| [400] | [Validation error] | [Error body example] |
| [409] | [Resource already exists] | [Error body example] |

---

## Error Code Reference

| Status Code | Meaning | Common Causes |
|-------------|---------|---------------|
| [400] | [Bad Request] | [Invalid request body, missing required fields] |
| [401] | [Unauthorized] | [Missing or invalid authentication] |
| [403] | [Forbidden] | [Valid auth but insufficient permissions] |
| [404] | [Not Found] | [Resource does not exist] |
| [422] | [Unprocessable Entity] | [Valid syntax but semantic errors] |
| [429] | [Too Many Requests] | [Rate limit exceeded] |
| [500] | [Internal Server Error] | [Unexpected server error -- contact support] |

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| [YYYY-MM-DD] | [v1.0] | [Initial release] |

## Definition of Done

- [ ] All endpoints are documented with parameters and examples
- [ ] Authentication method is described with instructions
- [ ] Error responses are listed for each endpoint
- [ ] Request and response examples are accurate and tested
- [ ] Changelog is up to date
- [ ] Reviewed by API consumers for clarity
