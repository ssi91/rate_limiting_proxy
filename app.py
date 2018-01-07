import argparse
import asyncio

from aiohttp import web, ClientSession

from rate_limit import RLQ, rate_limit_middleware

BASE_URL_TEMPLATE = "http://127.0.0.1:8001/{}"


async def _response(method, path, headers, params, body):
    session = ClientSession()
    response = await session.request(method, BASE_URL_TEMPLATE.format(path), params=params, data=body, headers=headers)
    session.close()
    return response


async def index_view(request):
    response = await _response(request.method, request.match_info['path'], request.headers, request.query, await request.read())
    _headers = dict()
    for h in response.headers:
        if h not in ("Content-Encoding", "Transfer-Encoding"):  # exclude hop-by-hop headers
            _headers[h] = response.headers[h]
    return web.Response(body=response.content._buffer[0], headers=_headers, status=response.status)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--base-host', required=True)
    parser.add_argument('-p', '--port', type=int, required=True)
    args = parser.parse_args()

    BASE_URL_TEMPLATE = args.base_host + "/{}"

    q = RLQ()
    loop = asyncio.get_event_loop()

    app = web.Application(middlewares=[rate_limit_middleware(q)], debug=True)
    app.router.add_route('*', '/{path:.*}', index_view)

    print("Run the server", "BASE HOST: {}".format(args.base_host), "PORT: {}".format(args.port), sep='\n')
    loop.run_until_complete(loop.create_server(app.make_handler(), '127.0.0.1', args.port))
    loop.run_forever()
