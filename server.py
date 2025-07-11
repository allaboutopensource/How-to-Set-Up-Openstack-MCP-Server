# server.py
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
import argparse
import re
import os
import openstack
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse

# Create an MCP server
mcp = FastMCP(name="openstack-mcp", port=8080, debug=True)

# Initialize connection to OpenStack
conn = openstack.connect(cloud='openstack')
cloud2 = conn.connect_as_project('asedf32q4fdsfsdfsfdfdsfgae190')

# Resource: Get openstack project Count
@mcp.resource("openstack://Projects-Count")
def Project_Count() -> list:
     projects = cloud2.identity.projects()
     num_projects = len(list(projects))
     return("Number of projects: ", num_projects)

# Tool: Get openstack project Count

@mcp.tool()
def Project_Count() -> list:
     projects = cloud2.identity.projects()
     num_projects = len(list(projects))
     return("Number of projects: ", num_projects)

@mcp.prompt(title="Openstack Server Creation")
def Openstack_Server_Creation() -> base.Prompt:
    """Prompt for creating an OpenStack server"""
    return base.Prompt(
        "OpenStack Server Creation",
        description="Create an OpenStack server with the specified parameters.",
        fields=[
            base.Field(
                "server_name",
                type=base.FieldType.STRING,
                description="Enter the name of the server to be created.",
                example="my_oracle_server"
            ),
            base.Field(
                "flavor_name",
                type=base.FieldType.STRING,
                description="Enter the flavor of the server (e.g., m1.medium).",
                example="m1.medium"
            ),
            base.Field(
                "image_name",
                type=base.FieldType.STRING,
                description="Enter the name of the image to be used for the server.",
                example="Ellucian Oracle Linux 8.3 20230330124320"      
            )
        ],
    )

# Resource: List all OpenStack images
@mcp.resource("openstack://images")
def List_Images() -> list:
    """List all OpenStack images"""
    images = cloud2.compute.images()
    return [image.name for image in images] 

# Resource: List all OpenStack networks

@mcp.resource("openstack://networks")
def List_Networks() -> list:    
    """List all OpenStack networks"""
    networks = cloud2.network.networks()
    return [network.name for network in networks]    

# Resource: List all OpenStack flavors
@mcp.resource("openstack://flavors")
def List_Flavors() -> list:
    """List all OpenStack flavors"""
    flavors = cloud2.compute.flavors()
    return [flavor.name for flavor in flavors]

# Resource: List all OpenStack projects Names
@mcp.resource("openstack://projects")
def List_Projects() -> list:
    """List all OpenStack projects"""
    projects = cloud2.identity.projects()
    return [project.name for project in projects]   

# Tool: List all OpenStack projects Names

@mcp.tool()
def List_Projects() -> list:
    """List all OpenStack projects"""
    projects = cloud2.identity.projects()
    return [project.name for project in projects]   

   
# Tool: List all OpenStack project servers count 

@mcp.tool()
def list_servers_count_in_project(project_name: str) -> list:
            """List all server names in a specific OpenStack project"""
            # Find the project by name
            project = cloud2.identity.find_project(project_name)
            if not project:
                return {"error": "Project Name not found"}
            # List servers in the project
            for p in project:
                 servers = list(cloud2.compute.servers(details=True, all_projects=True, project_id=project.id))
                 instance_count = len(servers)
            return {"instance_count": instance_count}

# Tool: List all OpenStack project servers Names

@mcp.tool()
def list_servers_in_project(project_name: str) -> list:
            """List all server names in a specific OpenStack project"""
            # Find the project by name
            projects = cloud2.identity.find_project(project_name)
            if not projects:
                return {"error": "Project Name not found"}
            # List servers in the project
            for p in projects:
                 servers = cloud2.compute.servers(details=True, all_projects=True, project_id=projects.id)
                 server_names = [server.name for server in servers]
                 s = list(server_names)
            return {"servers": s}


# Tool: List all OpenStack servers Count 
@mcp.tool()
def list_servers_count() -> dict:
    server_count = 0
    active_server_count = 0
    inactive_server_count = 0
    projects = cloud2.identity.projects()
    print(type(projects))
    for project in projects:
        servers = cloud2.compute.servers(all_projects=True, project_id=project.id, timeout=60)
        for instance in servers:
            if instance.status == 'ACTIVE':
                active_server_count += 1
            else:
                inactive_server_count += 1
            server_count += 1
    return {"total_servers": server_count, "active_servers": active_server_count,"inactive_servers": inactive_server_count}


# Tool: Get details of a specific server by name

@mcp.tool()
def get_server_details(server_name: str) -> dict:
        """Get details of a server by its name"""
        for server in cloud2.compute.servers():
            if server.name == server_name:
                return {
                    "id": server.id,
                    "name": server.name,
                    "status": server.status,
                    "flavor": server.flavor['original_name'] if 'original_name' in server.flavor else server.flavor['id'],
                    "addresses": server.addresses,
                }
        return {}

@mcp.tool()
def get_instance_name_by_floating_ip(floating_ip: str) -> dict:
    """
    Returns the name of the instance associated with the given floating IP.
    """
    # Find the floating IP object
    for ip in cloud2.network.ips():
        if ip.floating_ip_address == floating_ip:
            if ip.port_id:
                # Get the port details
                port = cloud2.network.get_port(ip.port_id)
                if port and port.device_id:
                    # Get the server (instance) by device_id
                    server = cloud2.compute.get_server(port.device_id)
                    return {"instance_name": server.name}
            return {"error": "Floating IP is not associated with any instance."}
    
    return {"error": "Floating IP not found."}


# Tool: Create a new server with specified name, flavor, and image
@mcp.tool()
def create_server(server_name: str, flavor_name: str, image_name: str, network_name:str) -> dict:
        """Create a new server with the specified name, flavor, and image"""
        flavor = cloud2.compute.find_flavor(flavor_name)
        image = cloud2.compute.find_image(image_name)
        network = cloud2.network.find_network('fake_dmz')  # Replace 'network_name' with your actual network name
        if not flavor or not image:
            return {"error": "Flavor or image not found"}
        
        server = cloud2.compute.create_server(
            name=server_name,
            flavor_id=flavor.id,
            image_id=image.id,
            networks=[{"uuid": network.id}],
            wait=True
        )
        return {"id": server.id, "name": server.name, "status": server.status}  

# Tool: Delete a server

@mcp.tool()
def delete_server(server_name: str) -> dict:
        """Delete a server by its name"""
        for server in cloud2.compute.servers():
            if server.name == server_name:
                cloud2.compute.delete_server(server.id)
                return {"status": "deleted", "name": server_name}
        return {"error": "Server not found"}


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
