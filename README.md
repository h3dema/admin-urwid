# virtualbox TUI


# Local test



```
# create environment
cd admin-urwid
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt

# run
cd src
python3 -m virtualbox_TUI
```



# Build the app


```
cd admin-urwid/
pip3 install setuptools build twine
python3 -m build
```

The distribuition archives are created in the [dist](./dist) folder.
They can be uploaded to pip using twine.
The example below puts it on the test repository.

```
python3 -m twine upload --repository testpypi dist/*
```

To upload the package, you need an API token that allows you to write the files on pypitest.
The authentication via token uses the information stored at `$HOME/.pypirc`.
This file contains the following 3 lines. `username` is always `__token__` and you need to put on the password field the token generated in the pypitest website.


```
[testpypi]
  username = __token__
  password = pypi-....
```

After running the command above, you will see a lot of information and the last lines contain the link to the package in the test pypi.
<pre>
View at:
https://test.pypi.org/project/vtui/0.1.0/
</pre>


To install the uploaded app, use the following link that can be found [here](https://test.pypi.org/project/vtui/). Notice that the version may change.

```
pip3 install -i https://test.pypi.org/simple/ vtui==0.1.0
```


> More information on [Packaging Python Projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/).
