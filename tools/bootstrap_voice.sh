#!/bin/bash
# Bootstrap voice-cloning env after sandbox reset (runs ~10 min)
set -e
W=/home/z/my-project/workspace
M=$W/models
S=/home/z/my-project/scripts
mkdir -p /tmp/wheels $M

# 0) pdl helper
[ -f $S/pdl.sh ] || exit 1

# 1) torch + torchaudio from aliyun (fast)
curl -sSL -o /tmp/torch.whl "https://mirrors.aliyun.com/pytorch-wheels/cpu/torch-2.3.1%2Bcpu-cp312-cp312-linux_x86_64.whl"
curl -sSL -o /tmp/torchaudio.whl "https://mirrors.aliyun.com/pytorch-wheels/cpu/torchaudio-2.3.1%2Bcpu-cp312-cp312-linux_x86_64.whl"
cp /tmp/torch.whl /tmp/torch-2.3.1-cp312-cp312-linux_x86_64.whl
cp /tmp/torchaudio.whl /tmp/torchaudio-2.3.1-cp312-cp312-linux_x86_64.whl
pip install -q /tmp/torch-2.3.1-cp312-cp312-linux_x86_64.whl /tmp/torchaudio-2.3.1-cp312-cp312-linux_x86_64.whl -i https://mirrors.aliyun.com/pypi/simple/

# 2) f5-tts and friends via tuna pdl
python3 $S/fetch_wheels.py

# 3) version fixes
python3 - << 'PYEOF'
import re, subprocess, urllib.request, html as H
from urllib.parse import urljoin
BASE="https://pypi.tuna.tsinghua.edu.cn/simple/"
def grab(pkg, want):
    req=urllib.request.Request(BASE+pkg+"/",headers={"User-Agent":"pip/24"})
    h=urllib.request.urlopen(req,timeout=30).read().decode("utf-8","ignore")
    for l in re.findall(r'href="([^"]+)"',h):
        u=urljoin(BASE+pkg+"/", l.split("#sha256=")[0]); fn=H.unescape(u.rsplit("/",1)[-1])
        if want in fn and ("cp312" in fn and "x86_64" in fn and "macos" not in fn and fn.endswith(".whl") or fn.endswith("py3-none-any.whl") and want in fn):
            subprocess.run(["/home/z/my-project/scripts/pdl.sh",u,"/tmp/wheels/"+fn,"8"],capture_output=True,text=True,timeout=560)
            print("got",fn); return fn
    return None
files=[]
files.append(grab("transformers","4.46.3"))
files.append(grab("tokenizers","0.20.3"))
files.append(grab("pypinyin","0.55.0"))
files.append(grab("av","av-12.3.0"))
files.append(grab("encodec","0.1.1"))
files.append(grab("jieba","0.42"))
files.append(grab("funcy","funcy-2"))
subprocess.run(["pip","install","-q","--no-deps"]+["/tmp/wheels/"+f for f in files if f])
PYEOF
pip install -q --no-deps /tmp/wheels/f5_tts-1.1.9-py3-none-any.whl /tmp/wheels/vocos-0.1.0-py3-none-any.whl /tmp/wheels/einx-0.4.3-py3-none-any.whl /tmp/wheels/cn2an-0.5.9-py3-none-any.whl 2>/dev/null || true
pip install -q frozendict einops librosa tomli "huggingface_hub==0.27.1" wandb accelerate torchdiffeq x-transformers ema-pytorch safetensors soundfile pydub faster-whisper -i https://mirrors.aliyun.com/pypi/simple/ || true

# 4) patch f5_tts model __init__ (trainer optional)
F=/home/z/.venv/lib/python3.12/site-packages/f5_tts/model/__init__.py
if [ -f $F ] && ! rg -q "except ImportError" $F; then
python3 - << 'PYEOF'
p="/home/z/.venv/lib/python3.12/site-packages/f5_tts/model/__init__.py"
s=open(p).read()
s=s.replace("from f5_tts.model.trainer import Trainer\n","try:\n    from f5_tts.model.trainer import Trainer\nexcept ImportError:\n    Trainer = None\n")
open(p,"w").write(s)
print("patched")
PYEOF
fi

# 5) verify
python3 -c "from f5_tts.infer.utils_infer import load_model, load_vocoder, infer_process; print('VOICE ENV OK')"
