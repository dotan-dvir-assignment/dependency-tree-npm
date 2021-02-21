# dependency-tree-npm
Create a dependency tree from an npm pacage name. The code starts a Flask server on port 5000. The end point is http://localhost:5000/package_name with package name being the package you want to build the dependency tree for.

The code returns an HTTP status code of 200 in case of success and 400 in case of failure. In case of success the code prints a dependency tree.

The code is not production quality. It makes the following simplifications:
1. It treats the version string in a naive way and only asks for exact versions - i.e. ^1.1.0 and ~1.1.0 both will try to retrieve 1.1.0
2. It does not treat complicated version requirements such as >1.5 & <2.0
3. It does not manage dependecies pointing to code in external repositories - i.e. github.com/author/package
4. It assumes requests will come in sequentially and not at the same time




