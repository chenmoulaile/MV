# 语音克隆管线（已验证可用）
- 环境: torch 2.3.1+cpu + f5-tts 1.1.9 (--no-deps 修复版) + vocos + transformers 4.46.3 + hub 0.27.1
- 模型: workspace/models/F5TTS_v1_Base/model_1250000.safetensors (337M) + vocab.txt + vocos-mel-24khz vocoder
- 源: ModelScope AI-ModelScope/F5-TTS (27MB/s) + hf-mirror (voc小文件)
- 参考: assets/hina_ref.m4a 5:36 语音条合集; 候选参考窗 39.16-44.00s
- 陷阱: transformers 5.x 不兼容; tokenizers 0.20.3; pypinyin 0.55; f5_tts/model/__init__.py 已 patch trainer 可选; wandb 已 stub(--no-deps 后缺 google, 用 try/except 绕过)
- 速度: 单连接全被限速(~20KB/s), pdl.sh 16并行可达 150KB/s-27MB/s(看源)
