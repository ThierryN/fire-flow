#!/usr/bin/env python3
"""
Dominion Flow UAT Runner — browser-use integration
Called by fire-verify-uat autonomous mode via Bash.

Usage:
  python uat-runner.py --task "..." --output /tmp/result.json [--max-steps 20] [--credentials '{}']

Exit codes:
  0 = script ran successfully, check JSON for PASS/FAIL/ERROR
  1 = setup error (missing dependency, missing API key, etc.)
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path


def check_setup():
    """Verify all prerequisites before importing browser_use."""
    errors = []

    if sys.version_info < (3, 11):
        errors.append(f"Python 3.11+ required (got {sys.version})")

    if not os.environ.get("ANTHROPIC_API_KEY"):
        env_file = Path(".env")
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                if line.startswith("ANTHROPIC_API_KEY="):
                    os.environ["ANTHROPIC_API_KEY"] = line.split("=", 1)[1].strip().strip('"')
                    break

    if not os.environ.get("ANTHROPIC_API_KEY"):
        errors.append("ANTHROPIC_API_KEY not found in environment or .env file")

    try:
        import browser_use  # noqa: F401
    except ImportError:
        errors.append("browser_use not installed. Run: pip install browser-use")

    return errors


def get_result_model():
    from pydantic import BaseModel

    class UATFlowResult(BaseModel):
        status: str
        summary: str
        steps_taken: int
        final_url: str
        errors: list[str]

    return UATFlowResult


async def run_uat(task, max_steps, sensitive_data):
    """Run one UAT flow via browser-use agent."""
    from browser_use import Agent
    from browser_use.llm import ChatAnthropic
    from browser_use.browser.profile import BrowserProfile

    UATFlowResult = get_result_model()

    llm = ChatAnthropic(
        model=os.environ.get("BROWSER_USE_MODEL", "claude-sonnet-4-5"),
        temperature=0.0,
    )

    profile = BrowserProfile(headless=True)

    agent = Agent(
        task=task,
        llm=llm,
        browser_profile=profile,
        sensitive_data=sensitive_data,
        output_model_schema=UATFlowResult,
        generate_gif=False,
    )

    history = await agent.run(max_steps=max_steps)

    raw = history.final_result()
    if raw:
        try:
            parsed = UATFlowResult.model_validate_json(raw)
            result = parsed.model_dump()
        except Exception as e:
            result = {
                "status": "FAIL",
                "summary": f"Agent returned unstructured output: {str(raw)[:500]}",
                "steps_taken": max_steps,
                "final_url": "",
                "errors": [f"Schema parse error: {e}"],
            }
    else:
        result = {
            "status": "FAIL",
            "summary": "Agent completed but returned no result.",
            "steps_taken": max_steps,
            "final_url": "",
            "errors": ["No final result returned by agent"],
        }

    # Attach screenshot paths if available
    try:
        screenshots = [str(p) for item in history.history if hasattr(item, 'state') and hasattr(item.state, 'screenshot') and item.state.screenshot for p in [item.state.screenshot]]
        result["screenshots"] = screenshots
    except Exception:
        result["screenshots"] = []

    return result


def main():
    parser = argparse.ArgumentParser(description="Dominion Flow UAT Runner (browser-use)")
    parser.add_argument("--task", required=True, help="Plain-English UAT task description")
    parser.add_argument("--output", required=True, help="Path for JSON output file")
    parser.add_argument("--max-steps", type=int, default=20, help="Max browser steps (default: 20)")
    parser.add_argument("--credentials", default=None, help='JSON string: {"domain": {"key": "value"}}')
    args = parser.parse_args()

    # 1. Setup checks
    errors = check_setup()
    if errors:
        print("SETUP ERRORS:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print("\nFix: pip install browser-use && uvx browser-use install", file=sys.stderr)
        sys.exit(1)

    # 2. Parse credentials
    sensitive_data = None
    if args.credentials:
        try:
            sensitive_data = json.loads(args.credentials)
        except json.JSONDecodeError as e:
            print(f"Invalid --credentials JSON: {e}", file=sys.stderr)
            sys.exit(1)

    # 3. Run agent
    try:
        result = asyncio.run(run_uat(
            task=args.task,
            max_steps=args.max_steps,
            sensitive_data=sensitive_data,
        ))
    except KeyboardInterrupt:
        print("UAT run interrupted.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        result = {
            "status": "ERROR",
            "summary": f"Infrastructure error: {str(e)}",
            "steps_taken": 0,
            "final_url": "",
            "errors": [str(e)],
            "screenshots": [],
        }

    # 4. Write JSON output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2))

    # 5. Print summary to stdout for Claude to read
    print(f"STATUS: {result['status']}")
    print(f"SUMMARY: {result['summary']}")
    if result.get("errors"):
        print(f"ERRORS: {'; '.join(result['errors'])}")
    print(f"OUTPUT: {args.output}")


if __name__ == "__main__":
    main()
