# server.py
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base
import uvicorn
import openstack
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse

# Create an MCP server
mcp = FastMCP(name="openstack-mcp", debug=True, system_prompt=base, port=8001)
app= FastAPI(title="Openstack MCP API")


@mcp.tool()
def greet(name: str) -> str:
    return f"Hello, {name}!"

@app.get("/mcp")
def greet_user(name: str):
    result = greet(name)
    # Return the result as a JSON response  
    return {result}


    # Initialize connection to OpenStack
conn = openstack.connect(cloud='openstack')
cloud2 = conn.connect_as_project('3434dfg324ghjkhjkhasdf234234345')

# Resource: Get openstack project Count
@mcp.resource("openstack://Projects-Count")
def Project_Count() -> list:
     projects = cloud2.identity.projects()
     num_projects = len(list(projects))
     return("Number of projects: ", num_projects)

# Tool: Get openstack project Count
@app.get("/")
def health():
    return {"message": "MCP server is running fine"}


@mcp.tool()
def Project_Count() -> list:
     projects = cloud2.identity.projects()
     num_projects = len(list(projects))
     return("Number of projects: ", num_projects)

@app.get("/project-count")
async def get_project_count():
    # Call the tool function and return its result wrapped in a JSON response
    result = Project_Count()
    return JSONResponse(content=result)

@mcp.prompt(title="Openstack Server Creation")
def create_server_prompt(
    server_name: str,
    flavor: str = "m1.medium",
    network_name: str = "admin",
    image_name: str = "Oracle Linux 8.3 "
) -> str:
    """Generate a Prompt to Create a server Instance on OpenStack Cloud"""

    return (
        f'Create a server named "{server_name}" on OpenStack cloud with flavor "{flavor}", '
        f'connected to network "{network_name}", and using image "{image_name}".'
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
        projects = cloud2.identity.projects()
        for project in projects:
            servers = cloud2.compute.servers(all_projects=True, project_id=project.id, timeout=60)
            for server in servers:
               if server.name == server_name:
                 return {
                    "id": server.id,
                    "name": server.name,
                    "status": server.status,
                    "flavor": server.flavor['original_name'] if 'original_name' in server.flavor else server.flavor['id'],
                    "addresses": server.addresses,
                    "project_name": project.name,
                    "created_at": server.created_at,
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
def create_server(server_name: str, flavor_name: str, image_name: str, network_name: str) -> dict:
        """Create a new server with the specified name, flavor, and image"""
        flavor = cloud2.compute.find_flavor(flavor_name)
        image = cloud2.compute.find_image(image_name)
        network = cloud2.network.find_network(network_name)  
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


@app.post("/create-server")

def create_server_endpoint(
    server_name: str,
    flavor_name: str,
    image_name: str,
    network_name: str
):
    result = create_server(server_name, flavor_name, image_name, network_name)
    status_code = 400 if "error" in result else 200
    return JSONResponse(content=result, status_code=status_code)

# Tool: Delete a server

@mcp.tool()
def delete_server(server_name: str) -> dict:
        """Delete a server by its name"""
        for server in cloud2.compute.servers():
            if server.name == server_name:
                cloud2.compute.delete_server(server.id)
                return {"status": "deleted", "name": server_name}
        return {"error": "Server not found"}
@app.post("/delete-server")
def delete_server_endpoint(
    server_name: str,
):
    result = delete_server(server_name)
    status_code = 400 if "error" in result else 200
    return JSONResponse(content=result, status_code=status_code)



if __name__ == "__main__":
    # Initialize and run the server
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
    
