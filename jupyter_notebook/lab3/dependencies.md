<!-- Jupyter YAML {{{
---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: pandoc
      format_version: 3.8
      jupytext_version: 1.18.1
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
  nbformat: 4
  nbformat_minor: 5
---
}}} -->

**Install required system packages**

```python
!apt install -y ffmpeg python3-scipy python3-sklearn python3-matplotlib python3-llvmlite
```

**Install specially cross-compiled tflite_runtime (the PyPI wheel uses instructions not available on this ARM core\...)**

```python
!pip install --no-deps https://github.com/DeepWok/pynqchat/raw/refs/heads/main/talkbot/tflite_runtime-2.14.1-cp310-cp310-linux_armv7l.whl
```

**Install other python packages**

```python
!pip install --no-deps -r https://github.com/DeepWok/pynqchat/raw/refs/heads/main/talkbot/requirements.txt
```
