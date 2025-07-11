# OpenStack Model Context Protocol (MCP) Server

<img width="1475" height="709" alt="image" src="https://github.com/user-attachments/assets/c7395a12-8494-4e52-af87-06f55faf1ae9" />

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [OpenStack Configuration](#openstack-configuration)
  - [Running the MCP Server](#running-the-mcp-server)
  - [Connecting with Claude Desktop](#connecting-with-claude-desktop)
- [Tools, Resources, and Prompts](#tools-resources-and-prompts)
- [Usage Examples](#usage-examples)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Introduction

This project presents a robust and extensible Model Context Protocol (MCP) server designed to enable seamless interaction between Large Language Models (LLMs) like Claude and your on-premise OpenStack cloud environment. By acting as a standardized interface, this MCP server allows LLMs to manage and query OpenStack resources through natural language commands, bridging the gap between advanced AI capabilities and traditional cloud infrastructure management.

The server is built to be hosted locally on-premise, ensuring your OpenStack infrastructure remains within your controlled network while still leveraging the power of AI for automation and operational tasks. This approach prioritizes security and maintains the benefits of a private cloud.
## Features

This OpenStack MCP server provides the following key functionalities to LLM clients:

-   **List OpenStack Projects:** Retrieve a list of all projects within your OpenStack cloud.
-   **List OpenStack Servers:** Get details about all virtual machines (VMs) deployed in OpenStack.
-   **Create OpenStack Server:** Provision a new VM instance with specified parameters.
-   **Delete OpenStack Server:** Terminate an existing VM instance.
-   **Find VM by IP Address:** Locate a specific VM by its assigned IP address.
-   **Configurable OpenStack Credentials:** Securely configure and use your OpenStack credentials to interact with the API.
-   **Lightweight and Extensible:** Designed to be easily extended with new OpenStack-related tools and functionalities.
-   **Secure Interaction:** Utilizes the Model Context Protocol to ensure secure and controlled access to your OpenStack environment.

## Architecture

The project leverages a client-server architecture based on the Model Context Protocol.

-   **MCP Client (Claude Desktop):** The Claude LLM application acts as the MCP client, initiating requests to the OpenStack MCP server using the standardized MCP protocol.
-   **OpenStack MCP Server:** This server component, hosted on your local on-premise infrastructure, receives requests from the Claude client, translates them into OpenStack API calls, executes them, and returns the results to Claude.
-   **OpenStack Cloud:** Your existing OpenStack cloud environment, which the MCP server interacts with to manage resources.

## Getting Started

Follow these steps to set up and run your OpenStack MCP server and connect it with Claude Desktop.

### Prerequisites

-   An active OpenStack cloud environment (locally hosted).
-   OpenStack credentials (tenant name, username, password, auth URL) or application credentials with appropriate permissions to manage resources.
-   Python >3.10 installed.
-   `pip` (Python package installer) installed.
-   [Claude Desktop](https://www.anthropic.com/claude) installed (as your MCP client).

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/modelcontextprotocol/python-sdk
    cd YOUR_REPO_NAME
    
    ```

2.  **Install dependencies:**

    uv init mcp-server
    
    cd mcp-server
    
    uv add "mcp[cli]"
    
    dependencies = [
        "fastapi>=0.116.0",
        "mcp[cli]>=1.10.1",
        "openstacksdk>=4.6.0",
        "uvicorn>=0.35.0",
### OpenStack Configuration

The MCP server needs to be configured with your OpenStack credentials. This can typically be done via environment variables or a configuration file.

1.  **Using Environment Variables (Recommended for development):**

    ```bash
    export OS_CLOUD=openstack
    export OS_AUTH_URL="YOUR_OPENSTACK_AUTH_URL" # e.g., http://your-controller-ip:5000/v3
    export OS_PROJECT_NAME="YOUR_PROJECT_NAME"
    export OS_USERNAME="YOUR_USERNAME"
    export OS_PASSWORD="YOUR_PASSWORD"
    # Or for Application Credentials:
    # export OS_APPLICATION_CREDENTIAL_ID="YOUR_APP_CRED_ID"
    # export OS_APPLICATION_CREDENTIAL_SECRET="YOUR_APP_CRED_SECRET"
    ```

    Ensure these environment variables are set in the terminal session where you will run the MCP server.

2.  **Using a Configuration File (e.g., `cloud.yaml`):**

    If you prefer to use a `cloud.yaml` file, place it in the appropriate location as per `openstacksdk` documentation. Refer to the `openstacksdk` documentation for details on configuring OpenStack access.

### Running the MCP Server

Start the MCP server using the provided script:

   uv run server.py



