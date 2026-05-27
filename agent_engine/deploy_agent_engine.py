"""Companion Agent Engine deployment scaffold.

This is intentionally separate from the Cloud Run product runtime. Use it only
to create an Agent Platform / Agent Engine proof artifact if judges expect one.
Verify the current Vertex AI Agent Engine SDK call before running.
"""

PROJECT_ID = "direct-subject-497307-p8"
LOCATION = "us-east4"
DISPLAY_NAME = "flux-onboarding-agent"
ENTRYPOINT_MODULE = "agent"
ENTRYPOINT_OBJECT = "root_agent"


def main() -> None:
    print("Companion Agent Engine deployment scaffold")
    print(f"project={PROJECT_ID}")
    print(f"location={LOCATION}")
    print(f"display_name={DISPLAY_NAME}")
    print(f"entrypoint={ENTRYPOINT_MODULE}:{ENTRYPOINT_OBJECT}")
    print("Before running, confirm the current Agent Engine deploy API and add the SDK call here.")


if __name__ == "__main__":
    main()
