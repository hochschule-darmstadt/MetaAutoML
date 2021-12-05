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
