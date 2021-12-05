# MetaAutoML

## How to check out the latest version

Clone MetaAutoML Repository:  
`git clone git@github.com:hochschule-darmstadt/MetaAutoML.git`

Clone submodules recursively:  
`git submodule update --init --recursive`

The submodules are now initialized to a specific commit that the MetaAutoML meta repository points to.
This MIGHT NOT BE THE LATEST COMMIT of the submodules.
If you like to check out the latest commits and therefore also change the pointer of the meta repository to the latest commits of the submodules, use:  
`git submodule update --remote --merge`

In order to persist this update of references in the meta repo you would obviously need to commit this in the meta repo.

If you like to commit on the submodules you will need to check out a branch there, because the submodules are initially in detached state:  
`git checkout <some branch>`
