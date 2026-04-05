## 404 Not Found Handing

There are no global error-handler overrides, so an un-matched route
will return Flasks HTML 404 page.

Our endpoint handler also return 404 when appropriate. For example when
we look up the id for a user, URL, event that does not exist.

In our URL-redirect handler, if the short-code is invalid or the URL is
inactive will will call `abort(404)` telling the user that something
was not found.

## 500 Internal Errors Handling
Each route is wrapped in a `try/except Exception` block around its
core DB or business logic, this way if something unexpected happens
we can return a 500 error to the client indicating that their request
was not malformed and that there is some internal issue with the
server.

