import yaml
from pathlib import Path
import sys
from typing import Dict, Any


def load_openapi_spec(file_path: str) -> Dict[Any, Any]:
    """Load the OpenAPI specification from a YAML file."""
    try:
        with open(file_path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading OpenAPI spec: {e}")
        sys.exit(1)


def extract_resources(spec: Dict[Any, Any]) -> Dict[str, Dict[str, Dict[str, str]]]:
    """Extract resources from the OpenAPI spec paths."""
    resources = {}

    for path, path_data in spec.get("paths", {}).items():
        # Skip webhook paths as they're handled differently
        if path.startswith("/webhooks"):
            continue

        # Extract resource name from path
        # Remove leading slash and take first segment
        resource_name = path.split("/")[1]

        # Skip if this is a nested resource path
        if len(path.split("/")) > 2 and "{" not in path.split("/")[2]:
            continue

        operations = {}

        # Handle collection-level operations
        if "{" not in path:
            if "post" in path_data:
                operations["create"] = {"path": path, "method": "POST"}
            # Collection GET becomes list operation
            if "get" in path_data:
                operations["list"] = {"path": path, "method": "GET"}

        # Handle individual resource operations
        if "{" in path:
            if "get" in path_data:
                operations["read"] = {"path": path, "method": "GET"}
            if "put" in path_data:
                operations["update"] = {"path": path, "method": "PUT"}
            if "delete" in path_data:
                operations["delete"] = {"path": path, "method": "DELETE"}

        # Only add if we found operations
        if operations:
            # Initialize resource if it doesn't exist
            if resource_name not in resources:
                resources[resource_name] = {}

            # Merge new operations with existing ones
            resources[resource_name].update(operations)

    # Post-process: Ensure resources have required operations
    for resource_name, operations in list(resources.items()):
        # If a resource has list but no read, copy list to read
        if "list" in operations and "read" not in operations:
            operations["read"] = operations["list"].copy()

        # If a resource has no create operation but has update, use update as create
        if "create" not in operations and "update" in operations:
            operations["create"] = operations["update"].copy()

    return resources


def generate_config(spec: Dict[Any, Any]) -> Dict[str, Any]:
    """Generate the generator config structure."""
    resources = extract_resources(spec)

    config = {"provider": {"name": "lago"}, "resources": {}}

    # Add resources to config
    for resource_name, operations in resources.items():
        if operations:  # Only add resources with operations
            config["resources"][resource_name] = operations

    return config


def write_config(config: Dict[Any, Any], output_path: str) -> None:
    """Write the generator config to a YAML file."""
    try:
        with open(output_path, "w") as f:
            yaml.dump(config, f, sort_keys=False, default_flow_style=False)
        print(f"Successfully generated {output_path}")
    except Exception as e:
        print(f"Error writing generator config: {e}")
        sys.exit(1)


def main() -> None:
    """Main function to generate the generator config."""
    # Get the project root directory (assuming the script is in src/terraform_provider_lago)
    project_root = Path(__file__).parent.parent.parent

    # Define paths
    openapi_spec_path = project_root / "lago_openapi.yaml"
    output_path = project_root / "generator_config.yml"

    # Load OpenAPI spec
    spec = load_openapi_spec(str(openapi_spec_path))

    # Generate config
    config = generate_config(spec)

    # Write config to file
    write_config(config, str(output_path))


if __name__ == "__main__":
    main()
