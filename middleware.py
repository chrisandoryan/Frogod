#from https://eshlox.net/2017/08/02/falcon-framework-json-middleware-loads-dumps
import falcon, json

class JSONValidator:
    def process_request(self, req, resp):
        """
        req.stream corresponds to the WSGI wsgi.input environ variable,
        and allows you to read bytes from the request body.
        See also: PEP 3333
        """

        if req.content_length in (None, 0):
            return

        body = req.stream.read()

        if not body:
            raise falcon.HTTPBadRequest(
                'Empty request body. A valid JSON document is required.'
            )

        try:
            req.context['request'] = json.loads(body.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            raise falcon.HTTPError(
                falcon.HTTP_753,
                'Malformed JSON. Could not decode the request body.'
                'The JSON was incorrect or not encoded as UTF-8.'
            )

    def process_response(self, req, resp, resource, req_succeeded):
        if 'response' not in resp.context:
            return

        resp.body = json.dumps(
            resp.context['response'],
            default=self._json_serializer
        )
    
    def _json_serializer(obj):
        if isinstance(obj, datetime.datetime):
            return str(obj)
        elif isinstance(obj, decimal.Decimal):
            return str(obj)

        raise TypeError('Cannot serialize {!r} (type {})'.format(obj, type(obj)))
