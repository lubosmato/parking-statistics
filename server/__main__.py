import logging

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp_apispec import docs, request_schema, response_schema
from marshmallow import Schema, fields, validate

from server.analysis.analyzer import ImageAnalyzer
from server.analysis.types import Point
from server.logging import load_logger_config
from server.server import RestHandler, Server


logger = logging.getLogger(__name__)


class RequestSchema(Schema):
    id = fields.Int()
    name = fields.Str(description="name")


class PointSchema(Schema):
    x = fields.Int()
    y = fields.Int()


class SizeSchema(Schema):
    width = fields.Int()
    height = fields.Int()


class RectangleSchema(Schema):
    top_left = fields.Nested(PointSchema)
    size = fields.Nested(SizeSchema)


class PoISchema(Schema):
    points = fields.Nested(PointSchema(many=True), validate=validate.Length(equal=4))


class PoiHandler(RestHandler):
    def __init__(self, analyzer: ImageAnalyzer):
        self.analyzer = analyzer

    @docs(
        tags=["analysis"],
        summary="Get POI points",
        description="4 points of POI (Polygon of Interest) are used to define an area of image",
    )
    @response_schema(PoISchema())
    async def get(self, request: Request) -> Response:
        return web.json_response(PoISchema().dump({"points": self.analyzer.poi}))

    @docs(
        tags=["analysis"],
        summary="Set POI points",
        description="4 points of POI (Polygon of Interest) are used to define an area of image",
    )
    @request_schema(PoISchema())
    async def post(self, request: Request) -> Response:
        points = request["data"]["points"]
        poi = [
            Point(**point)
            for point in points
        ]
        self.analyzer.poi = poi
        return web.json_response({"message": "POI set successfully"})


if __name__ == '__main__':
    load_logger_config("log_config.json")
    server = Server()

    analyzer = ImageAnalyzer()

    poi_handler = PoiHandler(analyzer)
    server.add_handler("/api/v1/poi", poi_handler)

    image_streams = {
        name: server.add_mjpeg_stream(f"/mjpeg/{name}")
        for name in analyzer.output_images_names
    }

    for name, stream in image_streams.items():
        analyzer.assign_stream(name, stream)

    analyzer.start()

    server.run()

    analyzer.stop()
