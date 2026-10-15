import datetime
import logging
from mitmproxy import http

LOG_FILE = "forms.log"

# Настраиваем отдельный логгер, чтобы не мешать выводу самого mitmproxy
logger = logging.getLogger("interceptor")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
handler.setFormatter(logging.Formatter("%(message)s"))
logger.addHandler(handler)


def _timestamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _log_form(flow: http.HTTPFlow, fields: list[tuple[str, str]], form_type: str) -> None:
    lines = [
        f"[{_timestamp()}] {flow.request.method} {flow.request.pretty_url} ({form_type})"
    ]
    for name, value in fields:
        lines.append(f"    {name} = {value}")
    entry = "\n".join(lines) + "\n"

    logger.info(entry)
    # дублируем в консоль mitmproxy, чтобы видеть перехват в реальном времени
    print(entry)


class FormInterceptor:
    """Аддон, который отслеживает отправку HTML-форм."""

    def request(self, flow: http.HTTPFlow) -> None:
        request = flow.request

        # Нас интересуют только запросы с телом (в первую очередь POST,
        # но форма технически может быть отправлена и GET-ом)
        if not request.content:
            return

        content_type = request.headers.get("Content-Type", "")

        # application/x-www-form-urlencoded
        if "application/x-www-form-urlencoded" in content_type:
            try:
                fields = list(request.urlencoded_form.items())
            except Exception:
                fields = []
            if fields:
                _log_form(flow, fields, "urlencoded")
            return

        # multipart/form-data
        if "multipart/form-data" in content_type:
            try:
                fields = [
                    (k, v if isinstance(v, str) else "<binary/file data>")
                    for k, v in request.multipart_form.items()
                ]
            except Exception:
                fields = []
            if fields:
                _log_form(flow, fields, "multipart")
            return

        # На случай, если форма отправлена GET-запросом (данные в query string)
        if request.method == "GET" and request.query:
            fields = list(request.query.items())
            if fields:
                _log_form(flow, fields, "query/GET")


addons = [FormInterceptor()]
