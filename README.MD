Create conda environment
```bash
conda create -n vs-poc python=3.10
```

Activate conda environment
```bash
conda activate vs-poc
```

Install dependencies
```bash
pip install pip==24.0.0
pip install pip-tools
pip-compile requirements.in
pip install -r requirements.txt
```





