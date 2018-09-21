# dab (dynamic ab)

기본 `ab`(apache benchmark)에서 dynamic하게 load를 변화시킬 수 있는 기능 추가

## 기능

- random 정도를 조절 가능한 load generation
- generation한 load를 json형태의 script로 저장
- 저장된 load script를 interpreting
- latency 결과를 csv로 저장

## 요구사항

- Python 3.7

_python package는 requirements.txt에_ 

## 사용법

### 1. load generator

```bash
generator.py [-h] [-a ALPHA] [-d DURATION] [-m MAXIMUM_CONCURRENCY] url [dest_path]
```

##### parameters

- `-a`: [파레토 분포](https://ko.wikipedia.org/wiki/%ED%8C%8C%EB%A0%88%ED%86%A0_%EB%B6%84%ED%8F%AC)의 `alpha`값
- `-d`: 실험할 시간 (초)
- `-m`: generate된 load (concurrent thread)의 최대값
- `url`: 실험할 페이지의 URL
- `dest_path`: 저장할 script의 주소 (지정하지 않는다면 `script.json`)

### 2. dab

#### interpreting mode

```bash
dab.py i [-h] script_path
```

##### parameters

- `script_path`: 불러와서 interpreting할 script의 주소

#### generation mode

```bash
dab.py g [-h] [-a ALPHA] -d DURATION [-o OUTPUT] url
```

##### parameters

- `-a`: [파레토 분포](https://ko.wikipedia.org/wiki/%ED%8C%8C%EB%A0%88%ED%86%A0_%EB%B6%84%ED%8F%AC)의 `alpha`값
- `-d`: 실험할 시간 (초)
- `-o`: generate된 script를 저장할 주소
- `url`: 실험할 페이지의 URL