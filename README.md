# ARElight 0.24.0

![](https://img.shields.io/badge/Python-3.9-brightgreen.svg)
![](https://img.shields.io/badge/AREkit-0.24.0-orange.svg)

### :point_right: [DEMO]() :point_left:

<p align="center">
    <img src="logo.png"/>
</p>

ARElight is an application for a granular view onto sentiments between mentioned named entities 
in a mass-media texts written in Russian.

### Sentiment Analysis Pipeline

ARElight core is powered by [AREkit](https://github.com/nicolay-r/AREkit) framework,
responsible for raw text sampling.
To annotate objects in text, we use `BERT`-based models trained on
`OntoNotes5` (powered by [DeepPavlov](https://github.com/deeppavlovteam/DeepPavlov))
For relations annotation, we support 
[OpenNRE](https://github.com/thunlp/OpenNRE)
`BERT` models.
The default inference is pretrained BERT with transfer learning based on 
[RuSentRel](https://github.com/nicolay-r/RuSentRel)
and 
[RuAttitudes](https://github.com/nicolay-r/RuAttitudes)
collections, that were sampled and translated into English via 
[arekit-ss](https://github.com/nicolay-r/arekit-ss).


# Installation

```bash
pip install git+https://github.com/nicolay-r/arelight@v0.24.0
```

## Usage

Infer sentiment attitudes from a mass-media document(s).
```bash
python3 -m arelight.run.infer  \
    --sampling-framework "arekit" \
    --ner-model-name "ner_ontonotes_bert_mult" \
    --ner-types "ORG|PERSON|LOC|GPE" \
    --terms-per-context 50 \
    --sentence-parser "ru" \
    --tokens-per-context 128 \
    --bert-framework "opennre" \
    --batch-size 10 \
    --pretrained-bert "DeepPavlov/rubert-base-cased" \
    --bert-torch-checkpoint "ra4-rsr1_DeepPavlov-rubert-base-cased_cls.pth.tar" \
    --backend "d3js_graphs" \
    --d3js-host 8000 \
    --docs-limit 500 \
    -o "output" \
    --text "США намерена ввести санкции против России."
```

Launches server at `http://0.0.0.0:8000/` so you may analyse the results.

<details>
<summary>

## Advanced and Partial Usage
</summary>

### `D3JS`: Operations between Graphs

### `D3JS`: Launch Graph Builder and DEMO server

Launch Graph Builder for D3JS and (optional) start DEMO server for collections in `output` dir:

```bash
python3 -m arelight.run.infer --backend "d3js_graphs" -o output --d3js-host 8080 
```
</details>

## Powered by

* AREkit [[github]](https://github.com/nicolay-r/AREkit)

<p float="left">
<a href="https://github.com/nicolay-r/AREkit"><img src="docs/arekit_logo.png"/></a>
</p>
