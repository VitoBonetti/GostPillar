# Role-Based Access Control (RBAC)

## 1. The Role Permission System Explained
The system relies on a hierarchical scoping model ``(Region -> Market -> Organization -> Asset -> Test -> Vulnerability)``. It separates "Global" users from "Scoped" users.

## Global Roles
These roles operate outside the standard hierarchy and cannot be assigned scoped roles.

- **GOD (Superuser)**: Has absolute read, write, and delete permissions across the entire platform. This is the only role permitted to delete high-level management objects (Regions, Markets, Organizations).

- **Platform Admin**: An administrative role that has full read and write access across the platform but cannot delete high-level management objects. A user cannot be both GOD and Admin.

## Scoped Roles (RoleAssignment)
These roles are assigned to a specific level in your hierarchy. A user can only hold one scope per assignment, and the system prevents conflicting roles (like mixing Manager and Operator in the same region).

- **Regional Viewer (``REGIONAL_VIEWER``)**:
  - **Scope Level**: Assigned only to a Region. 
  - **Permissions**: Read-only access to everything inside that Region (Markets, Orgs, Assets, Tests, Vulns). Cannot edit anything.

- **Manager (``MANAGER``)**:
  - **Scope Level**: Assigned only to a Market. 
  - **Permissions**: Can read and edit everything within their specific Market. They can also manage (invite/assign) operators within their market.

- **Operator (``OPERATOR``)**:
  - **Scope Level**: Assigned to an Organization, Asset, or Test. 
  - **Permissions**: Granular write access to Tests and Vulnerabilities. Their read access trickles down:
    - If assigned to an Organization: Can view the Org, its Assets, and any Tests/Vulns linked to those Assets. 
    - If assigned to an Asset: Can view the Asset and its Tests/Vulns. 
    - If assigned to a Test: Can only view that Test and its Vulns.