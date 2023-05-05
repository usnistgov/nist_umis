# Overview

In the move toward big data applications there are many activities focused on the structure, presentation, and annotation all kinds of data. Central though to all these efforts is the need to report a unit with any measured value. Currently, there are a number of disparate activities focused around the digital representation of units because of the urgent need to definitively represent and refer to scientific units, quantities and dimensions in the digital space. Interoperability is significantly hampered in the current, fragmented digital unit landscape. This project is focused on development of a site dedicated to the interoperability, usage and documentation of unit representations.

## Features

* Provide a stable, authoritative source for scientific units for digital applications
* Allow international units-related bodies to facilitate the process of digital unit development
* Codify, through ontologies, vocabularies and naming conventions unit and quantity representations
* Promote systematic unit/quantity application and usage through best practices and use cases
* Allow international standards agencies to provide formal language translations of units
* Provide a mechanism whereby legacy units can be represented and related to current units
* Produce a global network of synchronized unit repositories

## Status

This project is currently under development, contact the author for more information.  Stuart Chalk.

# License

This is free software, see LICENSE.

# Contact

The author can be reach at

# Credits

.

## Getting Started
---
## Docker Commands
---
### Start Docker Container(s)

`docker-compose up -d`

### Stop and Remove Container(s)

> Note: This will **delete** the containers

`docker-compose down`

### Stop Container(s)

`docker-compose stop`

### Restart Container(s)
`docker-compose restart`

### Local Site Link
[UMIS Local Site](http://127.0.0.1:8081)

---
## Prerequisites
---
- [Dockerhub v20.10.24](https://hub.docker.com/)
- [Git v2.4.0](https://git-scm.com/downloads)
- [GitHub Access](https://github.com/stuchalk/nist_umis/tree/nist_umis)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
> Please ensure you have a copy of the .env file used for docker-compose & mysql variables

Optional
- [VS Code](https://code.visualstudio.com/download)
  > Required VSCode Extensions
  - Docker
  - Dev Containers
  - Python

---
## Install, build and start application
---
### Clone the repository
`git clone git@github.com:stuchalk/nist_umis.git`

> If the development branch hasn't been merged yet, switch to the development branch
> 
> `git checkout nist_umis_v2`

### Move into the directory
`cd nist_umis`

### Verify .env variables are correct
`vi .env`

### Start MySQL & Umis Application container
`docker-compose up -d`

### Open browser and type in local site
`http://127.0.0.1:8081` or `http://localhost:8081`

### Log into container
`docker exec -it umis_app /bin/bash`

### Verify MySQL access
`mysql -u mysqluser stuchalk_umis -p`
> Enter mysqluser password from .env file
> SHOW TABLES;

---
## Added & Modified files
---
- .gitignore 
  - Added .DS_Store
- .dockerignore 
  - Created & added .env & .vscode files
- .env
  - File will not be stored in repository
- Dockerfile
- docker-compose.yaml
- api/views.py
  - Removed `+ uport +` on site =
- requirements.txt
  - Slightly modified specific versions
- umisconfig/settings.py
  - Creates secret variables which rely on .env file
- entrypoint.sh
  - Sets to start application after waiting 30 seconds (for mysql database)
