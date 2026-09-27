# Protected API surface

`Client.send(request) -> Response`
`Client.status() -> Status`
`Response.id: string`
`Response.state: string`

Compatibility invariant: existing documented calls and response fields must remain available without mandatory caller changes.
