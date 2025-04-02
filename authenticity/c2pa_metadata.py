from dataclasses import dataclass
from typing import Any


@dataclass
class SoftwareAgent:
    """Represents a software agent that performed an action on the media."""

    name: str
    action: str

    def get_formatted_action(self) -> str:
        """Returns a human-readable description of the action."""
        if self.action == "created":
            return "The asset was created by"
        if self.action == "converted":
            return "The asset format was converted by"
        return f"{self.action} by"


@dataclass
class C2PAMetadata:
    """Represents parsed C2PA metadata from an image."""

    instance_id: str
    title: str
    issuer: str
    generator_name: str
    digital_source_type: str | None
    software_agents: list[SoftwareAgent]

    @classmethod
    def from_manifest(cls, manifest: dict[str, Any]) -> "C2PAMetadata":
        """
        Parse a C2PA manifest dictionary and extract relevant metadata.

        Args:
            manifest: Dictionary containing C2PA manifest data

        Returns:
            C2PAMetadata object with parsed information
        """
        active_manifest_id = manifest.get("active_manifest")
        active_manifest = manifest.get("manifests", {}).get(active_manifest_id, {})
        claim = active_manifest.get("claim", {})
        claim_generator_info = claim.get("claim_generator_info", {})
        instance_id = claim.get("instanceID", "Unknown")
        title = claim.get("dc:title", "Unknown")

        signature_info = active_manifest.get("signature", {})
        issuer = signature_info.get("issuer", "Unknown")

        assertion_store = active_manifest.get("assertion_store", {})
        assertion_manifest_id = (
            assertion_store.get("c2pa.ingredient.v3", {})
            .get("activeManifest", {})
            .get("url", "")
            .split("/")[-1]
        )

        software_agents: list[SoftwareAgent] = []
        digital_source_type: str | None = None

        assertion_manifest = manifest.get("manifests", {}).get(assertion_manifest_id, {})

        if assertion_manifest:
            assertion_assertion_store = assertion_manifest.get("assertion_store", {})

            # Extract software agents and digital source type from assertions
            actions = assertion_assertion_store.get("c2pa.actions.v2", {}).get("actions", [])
            for action in actions:
                agent_name = action.get("softwareAgent", {}).get("name")
                if agent_name and agent_name not in [sa.name for sa in software_agents]:
                    action_type = action.get("action", "").replace("c2pa.", "")
                    software_agents.append(SoftwareAgent(name=agent_name, action=action_type))

                if "digitalSourceType" in action:
                    digital_source_type = action.get("digitalSourceType", "")
                    if "trainedAlgorithmicMedia" in digital_source_type:
                        digital_source_type = "This content was generated with an AI tool"

        return cls(
            instance_id=instance_id,
            title=title,
            issuer=issuer,
            generator_name=claim_generator_info.get("name", "Unknown"),
            digital_source_type=digital_source_type,
            software_agents=software_agents,
        )
