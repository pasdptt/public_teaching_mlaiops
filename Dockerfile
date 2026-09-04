# ITCS355 Lab 1 — training image
#
# TODO(Lab 1, Task 2): pin this base image BY DIGEST, not by tag.
#   Tags move. `python:3.11-slim` today is not `python:3.11-slim` next month, and a
#   moving base is the commonest reason a "reproducible" build stops reproducing.
#   Get the digest with:
#       docker pull python:3.11-slim && docker inspect --format='{{index .RepoDigests 0}}' python:3.11-slim
#   Then replace the two FROM lines below with the digest form:
#       FROM python@sha256:<digest> AS builder
FROM python:3.11-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

# Dependencies first so this layer caches independently of your source.
COPY requirements.txt ./
# TODO(Lab 1, Task 2): once requirements.txt carries hashes, add --require-hashes here.
# It turns a silently-substituted package into a build failure, which is what you want.
RUN pip install --prefix=/install -r requirements.txt


FROM python:3.11-slim AS runtime

# Non-root. A training container has no reason to run as root, and graders check.
RUN useradd --create-home --uid 10001 runner
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

COPY --from=builder /install /usr/local
WORKDIR /app
COPY --chown=runner:runner src/ ./src/
COPY --chown=runner:runner cloudlayer/ ./cloudlayer/
COPY --chown=runner:runner scripts/ ./scripts/

USER runner

# Credentials NEVER enter an image layer. They arrive at runtime from SECRET_STORE_PATH
# or from the platform's identity. If you find yourself adding an ARG for a key, stop.
ENTRYPOINT ["python", "-m", "src.train"]
CMD ["--n-estimators", "200", "--max-depth", "8"]
