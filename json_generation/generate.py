#!/usr/bin/env python3
"""Generate world models from the situations in ``situations/situations.json``.

Sends ``prompts/zero_shot.md`` as the system message and one situation as the user
message, then writes each reply **verbatim** to ``runs/<timestamp>/<id>.<n>.json``.
Nothing is stripped or repaired: tier 0 of ``eval/check.py`` judges the reply as it
came back, so a fenced or chatty one has to fail.

    python generate.py                     # every situation, one sample each
    python generate.py --k 5               # five samples each, for pass@k
    python generate.py --only dropped-keys
    python generate.py --config sweep.yaml # a different model or sampling setup

The model and the sampling parameters come from ``config.yaml``; ``--temperature``,
``--top-p`` and ``--max-tokens`` override it for one run. Auth follows ``auth:`` in
that file: ``entra_id`` (via DefaultAzureCredential) or ``api_key`` (via
AZURE_AI_API_KEY in ``.env``). See ``.env.example``.

A run directory holds the candidates and nothing else — no metadata, and none of
the ``reasoning_content`` a reasoning deployment may return beside its reply.
"""
from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
from datetime import datetime

import yaml
from dotenv import load_dotenv
from openai import OpenAI

ROOT = pathlib.Path(__file__).resolve().parent
PROMPT_PATH = ROOT / "prompts" / "zero_shot.md"
SITUATIONS_PATH = ROOT / "situations" / "situations.json"
CONFIG_PATH = ROOT / "config.yaml"
RUNS = ROOT / "runs"

# Sampling parameters the OpenAI client takes as named arguments. Anything else
# under `sampling:` — top_k, and whatever a given deployment adds — is passed
# through in extra_body, which the client sends as-is.
NAMED_SAMPLING = ("temperature", "top_p", "max_tokens", "frequency_penalty",
                  "presence_penalty", "seed", "stop")


def load_config(path: pathlib.Path) -> dict:
    """The YAML config, with the keys generate.py requires checked for presence."""
    if not path.exists():
        raise SystemExit(f"no config at {path}")
    config = yaml.safe_load(path.read_text()) or {}
    if missing := [k for k in ("endpoint", "deployment") if not config.get(k)]:
        raise SystemExit(f"missing from {path.name}: {', '.join(missing)}")
    return config


def credential(mode: str):
    """What the client authenticates with: an Entra ID token provider, or the API key.

    The OpenAI client accepts either a string or a ``Callable[[], str]`` as `api_key`,
    which is how the bearer-token provider is passed through.
    """
    if mode == "api_key":
        load_dotenv(ROOT / ".env")
        for name in ("AZURE_API_KEY", "AZURE_AI_API_KEY"):
            if key := os.environ.get(name):
                return key
        raise SystemExit("auth: api_key in the config, but neither AZURE_API_KEY nor "
                         "AZURE_AI_API_KEY is set in the environment or .env")
    if mode != "entra_id":
        raise SystemExit(f"unknown auth mode {mode!r}: expected entra_id or api_key")
    try:
        from azure.identity import DefaultAzureCredential, get_bearer_token_provider
    except ImportError:
        raise SystemExit("entra_id auth needs azure-identity: pip install azure-identity") from None
    # Managed identity is excluded on purpose: off Azure there is no IMDS to answer,
    # and the probe hangs for minutes without printing anything.
    provider = get_bearer_token_provider(
        DefaultAzureCredential(exclude_managed_identity_credential=True),
        "https://ai.azure.com/.default",
    )
    print("signing in with DefaultAzureCredential...", file=sys.stderr, flush=True)
    try:
        provider()  # fail here, with a real message, rather than inside the first call
    except Exception as exc:
        raise SystemExit(f"entra_id sign-in failed: {exc}\n"
                         "Sign in (az login / azd auth login) or set auth: api_key.") from None
    return provider


def build_client(config: dict) -> tuple[OpenAI, str]:
    """An OpenAI client pointed at the Azure AI Foundry v1 endpoint, and the deployment."""
    client = OpenAI(
        base_url=config["endpoint"],
        api_key=credential(config.get("auth", "entra_id")),
        timeout=float(config.get("timeout", 600)),
    )
    return client, config["deployment"]


def sampling_options(sampling: dict) -> tuple[dict, dict]:
    """The `sampling:` block split into named arguments and extra_body passthrough.

    A parameter set to null is dropped from both, so it is left out of the request
    entirely and a deployment that rejects it never sees it.
    """
    given = {k: v for k, v in (sampling or {}).items() if v is not None}
    named = {k: v for k, v in given.items() if k in NAMED_SAMPLING}
    extra = {k: v for k, v in given.items() if k not in NAMED_SAMPLING}
    return named, extra


def generate(client, deployment: str, system: str, situation: str,
             named: dict, extra: dict) -> str:
    """One call: the prompt as the system message, the situation as the user message.

    Returns the raw reply. Any `reasoning_content` a deployment returns beside it is
    discarded — only the world model is kept.
    """
    completion = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Situation:\n{situation}"},
        ],
        **named,
        **({"extra_body": extra} if extra else {}),
    )
    choice = completion.choices[0]
    if choice.finish_reason == "length":
        # A truncated reply cannot parse; say so rather than let tier 0 blame the model.
        raise RuntimeError(f"reply hit the {named.get('max_tokens')}-token cap "
                           "— raise sampling.max_tokens")
    if not choice.message.content:
        raise RuntimeError("empty reply")
    return choice.message.content


def load_situations(only: str | None) -> list[dict]:
    situations = json.loads(SITUATIONS_PATH.read_text())["situations"]
    if only:
        situations = [s for s in situations if s["id"] == only]
        if not situations:
            raise SystemExit(f"no situation with id {only!r}")
    return situations


def start_run() -> pathlib.Path:
    """A fresh run directory. Nothing goes in it but the candidates themselves."""
    out = RUNS / datetime.now().strftime("%Y%m%d-%H%M%S")
    out.mkdir(parents=True)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate world models from situations.")
    parser.add_argument("--config", type=pathlib.Path, default=CONFIG_PATH,
                        help="model and sampling config (default config.yaml)")
    parser.add_argument("--deployment", help="overrides the config, to compare models")
    parser.add_argument("--k", type=int, help="samples per situation (default from the config)")
    parser.add_argument("--only", metavar="ID", help="generate for one situation only")
    parser.add_argument("--temperature", type=float, help="overrides the config")
    parser.add_argument("--top-p", type=float, help="overrides the config")
    parser.add_argument("--max-tokens", type=int, help="overrides the config")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.deployment:
        config["deployment"] = args.deployment
    sampling = dict(config.get("sampling") or {})
    for key in ("temperature", "top_p", "max_tokens"):
        if (value := getattr(args, key)) is not None:
            sampling[key] = value
    named, extra = sampling_options(sampling)
    k = args.k if args.k is not None else int(config.get("k", 1))

    system = PROMPT_PATH.read_text()
    situations = load_situations(args.only)
    client, deployment = build_client(config)
    out = start_run()

    total = len(situations) * k
    print(f"{deployment} at {config['endpoint']}\n{total} candidate(s) to generate",
          file=sys.stderr, flush=True)

    for situation in situations:
        for sample in range(k):
            name = f"{situation['id']}.{sample}.json"
            print(f"  {name:32} ...", end="\r", file=sys.stderr, flush=True)
            try:
                reply = generate(client, deployment, system, situation["description"],
                                 named, extra)
            except Exception as exc:
                print(f"  {name:32} failed: {exc}", file=sys.stderr)
                continue
            (out / name).write_text(reply)
            print(f"  {name:32} {len(reply)} chars", file=sys.stderr)

    print(f"\ncheck them with:  python eval/check.py {out.relative_to(ROOT)}/<file>",
          file=sys.stderr)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
