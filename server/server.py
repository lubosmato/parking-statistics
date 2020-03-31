import asyncio
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from aiohttp import web, MultipartWriter
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from aiohttp_apispec import setup_aiohttp_apispec, validation_middleware

logger = logging.getLogger(__name__)


class RestHandler:
    async def get(self, request: Request) -> Response:
        pass

    async def post(self, request: Request) -> Response:
        pass

    async def put(self, request: Request) -> Response:
        pass

    async def patch(self, request: Request) -> Response:
        pass

    async def delete(self, request: Request) -> Response:
        pass


@dataclass
class MjpegStream:
    raw_image_data: bytearray


class Server:
    _mjpeg_streams: Dict[str, MjpegStream]

    def __init__(self):
        self.app = web.Application()
        self._mjpeg_streams = dict()

    def add_handler(self, path: str, handler: RestHandler):
        allowed_http_methods = ["get", "post", "put", "patch", "delete"]
        routes = (
            (getattr(handler, http_method), http_method)
            for http_method in allowed_http_methods
            if self._is_method_implemented(handler, http_method)
        )
        for handler_method, http_method in routes:
            self.app.router.add_route(http_method, path, handler_method)

    @staticmethod
    def _is_method_implemented(handler: RestHandler, http_method: str):
        handler_func = getattr(handler.__class__, http_method)
        default_func = getattr(RestHandler, http_method)
        return handler_func != default_func

    def run(self):
        setup_aiohttp_apispec(
            app=self.app,
            title="Parking statistics",
            version="v1",
            url="/api/docs/swagger.json",
            swagger_path="/api/docs",
        )
        self.app.middlewares.append(validation_middleware)
        static_folder = Path(__file__).resolve().parent.parent / "frontend" / "dist"
        self.app.add_routes([web.static('/', static_folder)])
        web.run_app(self.app)

    def add_mjpeg_stream(self, path: str, stream_rate=10) -> MjpegStream:
        if path in self._mjpeg_streams:
            raise AttributeError(f"path '{path}' is already in use")

        stream = MjpegStream(bytearray())
        self._mjpeg_streams[path] = stream

        async def handle_mjpeg(request: Request):
            logger.info(f"Client connected to MJPEG stream '{path}'")
            boundary = 'frame-start'
            response = web.StreamResponse(
                status=200,
                reason='OK',
                headers={
                    "Content-Type": f"multipart/x-mixed-replace;boundary={boundary}"
                }
            )
            try:
                await response.prepare(request)
                while True:
                    with MultipartWriter('image/jpeg', boundary=boundary) as writer:
                        writer.append(stream.raw_image_data, {'Content-Type': 'image/jpeg'})
                        await writer.write(response, close_boundary=False)

                    await asyncio.sleep(1 / stream_rate)
            except Exception as e:
                logger.info(f"Client disconnected from MJPEG stream '{path}' because '{e}'")

        self.app.router.add_get(path, handle_mjpeg)
        return stream
