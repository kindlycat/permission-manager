FROM python:3.12.1-slim

COPY --from=ghcr.io/astral-sh/uv:0.4.10 /uv /bin/uv

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONBREAKPOINT=ipdb.set_trace \
    WORKDIR=/app

ENV PATH="$WORKDIR/.venv/bin:$PATH" \
    VIRTUAL_ENV=$WORKDIR/.venv

WORKDIR $WORKDIR

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

ADD . $WORKDIR

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project
