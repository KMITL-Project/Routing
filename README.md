# Routing

## Technologies Used

- [Python3](https://www.python.org/download/releases/3.0/) - The Python Software Foundation is the organization behind Python. Become a member of the PSF and help advance the software and our mission.
- [OpenStreetMap](https://www.openstreetmap.org/) - OpenStreetMap is a free, editable map of the whole world that is being built by volunteers largely from scratch and released with an open-content license.
- [PiP](https://pypi.org/project/pip/) - pip is the package installer for Python. You can use pip to install packages from the Python Package Index and other indexes.

## Getting Started

Install package:

```bash
pip3 install --no-cache-dir -r requirements.txt
```

First, run the development server:

```bash
python3 server.py
```

Run on [http://localhost:5001](http://localhost:5001)

## Build step

#### build image

```bash
docker build --progress=plain -t router-service .
```

#### run image

```bash
docker run -p 5001:5001 router-service
```
