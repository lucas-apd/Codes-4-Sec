# Clone the project, e.g. `myproject` is my project repository:
    git clone https://github/lucas-apd/myproject.git

# Since all of the commits history are in the `.git` folder, we have to remove it:
   cd myproject

# And delete the `.git` folder:
   git rm -rf .git

# Now, re-initialize the repository:
    git init
      
    git remote add origin https://github.com/lucas-apd/myproject.git
    
    git remote -v

# Add all the files and commit the changes:
    git add --all
    git commit -am "Initial commit"

# Force push update to the master branch of our project repository:
    git push -f origin master

thanks to @heiswayi
