# MetaAutoML

## How to check out the latest version

Clone MetaAutoML Repository:  
`git clone git@github.com:hochschule-darmstadt/MetaAutoML.git`

Clone submodules recursively:  
`git submodule update --init --recursive`

The submodules are now initialized to a specific commit that the MetaAutoML meta repository points to.
This MIGHT NOT BE THE LATEST COMMIT of the submodules.
If you like to pull the latest commit of submodules you must first check out an already existing branch in the submodule, because it will initially be in detached state:  
`git checkout <some branch>` (e.g. main branch)

Then you need to pull the latest changes of that branch:  
`git pull origin <your current branch>`

In order to persist this update of references in the meta repo you would obviously need to commit this in the meta repo.

If you like to commit on the submodules you will need to check out a branch there, because the submodules are initially in detached state:  

You then have to commit and push you changes in the submodule. The meta repository will then update its reference to the submodule.
This update can than be committed in the meta repository.

## Docker Setup
There is one main docker-compose file, which configures all backend modules to run in a local setup.
Backend modules being the Controller and all Adapters.
Then there are two supplementary docker-compose files namely `docker-compose-frontend.yml` and `docker-compose-dummy.yml` which can be used to start the dummy or the frontend also in a separate docker-container to go along with the backend.  
It is recommended to use the Makefile to quickly start the desired setup.
So examine the Makefile and start whatever setup you want.  

Once you have the backend running you can connect to it on the host machine on port `5001`, because that port is mapped from the host into the container which the Controller runs in.
All Adapters are not mapped to the host but communicate with the Controller inside the internal docker-compose network.  
So when running the backend in docker-compose you can connect to it from the frontend or dummy running locally.  
However, as explained there is also the option to run the frontend or dummy in docker-compose directly.
The docker-compose setup for dummy and frontend then arranges that they connect to the controller over the mapped port 5001.
This way the backend setup is ready to work with either the local or the containerized frontend/dummy interface.