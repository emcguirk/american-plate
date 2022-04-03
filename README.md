# American Plate

After cloning to your machine, follow the instructions below to create the virtual environment

## Windows
Ensure you have python and virtualenv installed

```
py -m pip install --upgrade pip
py -m pip --version
py -m pip install --user virtualenv
```
In the root folder of the project, create a virtual environment, then activate it
```
py -m venv venv
.\env\Scripts\activate
```

Install dependencies
```
py -m pip install -r requirements.txt
```

## macOS/Linux

Ensure you have python and virtualenv installed

```
python3 -m pip install --user --upgrade pip
python3 -m pip --version
python3 -m pip install --user virtualenv
```

In the root folder of the project, create a virtual environment, then activate it
```
python3 -m venv venv
source env/bin/activate
```

Install dependencies
```
python3 -m pip install -r requirements.txt
```


