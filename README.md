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
