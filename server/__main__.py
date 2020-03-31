from aiohttp import web
from aiohttp_apispec import docs, request_schema
from marshmallow import Schema, fields

from server.analysis.analyzer import ImageAnalyzer
from server.logging import load_logger_config
from server.server import RestHandler, Server


class RequestSchema(Schema):
    id = fields.Int()
    name = fields.Str(description="name")


class ExampleHandler(RestHandler):
    @docs(
        tags=["mytag"],
        summary="Test method summary",
        description="Test method description",
    )
    async def get(self, request):
        return web.json_response({"msg": "done from get", "data": {}})

    @docs(
        tags=["mytag"],
        summary="Another method",
        description="Test method description",
    )
    @request_schema(RequestSchema())
    async def post(self, request):
        return web.json_response({"msg": "done from post", "data": {}})


if __name__ == '__main__':
    load_logger_config("log_config.json")
    server = Server()

    example_handler = ExampleHandler()
    server.add_handler("/api/v1/test", example_handler)

    analyzer = ImageAnalyzer()
    image_streams = {
        name: server.add_mjpeg_stream(f"/mjpeg/{name}")
        for name in analyzer.output_images_names
    }

    for name, stream in image_streams.items():
        analyzer.assign_stream(name, stream)

    analyzer.start()

    server.run()

    analyzer.stop()
