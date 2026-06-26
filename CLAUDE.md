# 보안 로그 기반 위협 점수화 & 리포트 생성 시스템 설계도

> 목적: 포트폴리오용이 아니라, 보안/네트워크/SI/AI 보안 솔루션 업무를 이해하기 위한 개인 학습용 프로젝트다.  
> 핵심 목표는 “보안 로그가 어떻게 생기고, 어떻게 묶이고, 왜 위험하다고 판단되는지”를 직접 구현하면서 이해하는 것이다.

---

## 1. 프로젝트 개요

### 프로젝트 이름

```text
Security Log Analyzer
```

또는 개인 학습용 이름으로는 다음처럼 사용해도 된다.

```text
Threat Score Reporter
보안 로그 위협 점수 리포터
```

### 한 줄 설명

```text
FW, WAF, IPS 형태의 보안 로그를 수집하고, IP와 시간 흐름 기준으로 이벤트를 묶어 위험도를 점수화한 뒤, 판단 근거와 침해 의심 리포트를 생성하는 학습용 시스템
```

### 만들면서 이해할 내용

이 프로젝트를 만들면서 아래 지식을 자연스럽게 익힌다.

```text
IP / Port / Protocol
Firewall / WAF / IPS
웹 공격 유형
보안 로그 필드 구조
로그 파싱
시간 기반 이벤트 그룹핑
위험도 점수화
XAI 방식의 판단 근거 설명
리포트 자동 생성
FastAPI 기반 백엔드
SQLite 기반 저장 구조
간단한 관리자 화면
```

---

## 2. 전체 흐름

```text
보안 로그 CSV 준비
        ↓
CSV 업로드 API 호출
        ↓
로그 파싱 및 DB 저장
        ↓
로그 목록 조회 / 필터링
        ↓
IP + 시간 윈도우 기준 이벤트 그룹핑
        ↓
위험도 점수 계산
        ↓
위협 의심 사건 Incident 생성
        ↓
판단 근거 Explanation 생성
        ↓
Markdown 리포트 생성
        ↓
관리자 화면에서 확인
```

---

## 3. 학습 목표

### 3.1 네트워크 이해

이 프로젝트에서는 로그에 포함된 네트워크 필드를 직접 다룬다.

```text
src_ip      출발지 IP
src_port    출발지 포트
dst_ip      목적지 IP
dst_port    목적지 포트
protocol    TCP / UDP / HTTP / HTTPS
```

이 필드를 다루면서 다음을 이해한다.

```text
어떤 IP가 공격자로 의심되는가?
어떤 서버가 공격 대상인가?
어떤 포트가 공격받았는가?
HTTP/HTTPS 요청은 WAF와 어떻게 연결되는가?
방화벽 로그와 웹 방화벽 로그는 어떤 차이가 있는가?
```

---

### 3.2 보안 장비 이해

프로젝트에서는 세 가지 장비 로그를 가정한다.

| 장비 | 의미 | 주로 탐지하는 것 |
|---|---|---|
| FW | Firewall | IP/Port 기반 접근 제어, 포트 스캔, 차단 로그 |
| WAF | Web Application Firewall | SQL Injection, XSS, Path Traversal 등 웹 공격 |
| IPS | Intrusion Prevention System | 공격 시그니처, 침입 시도, 악성 패턴 |

학습 포인트는 다음과 같다.

```text
FW는 네트워크 접근 흐름을 본다.
WAF는 웹 요청의 공격 패턴을 본다.
IPS는 알려진 공격 시그니처나 침입 시도를 본다.
세 로그가 따로 보면 단편적이지만, 시간 흐름으로 묶으면 공격 시나리오가 보인다.
```

---

### 3.3 XAI 방식 이해

이 프로젝트의 핵심은 단순히 “위험하다”고 출력하는 것이 아니다.

```text
왜 위험한지
어떤 로그 때문에 위험한지
몇 점이 어떤 이유로 추가되었는지
어떤 순서로 공격이 진행된 것으로 보이는지
```

위 내용을 사람이 이해할 수 있게 설명하는 것이 핵심이다.

예시:

```text
10.0.0.15 IP는 5분 이내에 PORT_SCAN, SQL_INJECTION, SIGNATURE_HIT 이벤트가 연속으로 발생했다.
먼저 여러 포트 접근이 탐지되었고, 이후 웹 공격 시도가 발생했으며, 마지막으로 IPS 시그니처 탐지까지 이어졌다.
따라서 단순 오탐보다는 침해 사고 의심 흐름으로 판단한다.
```

---

## 4. 기술 스택

처음부터 복잡하게 가지 않고, 이해 중심으로 구성한다.

```text
Python 3.11+
FastAPI
SQLite
SQLAlchemy
Pandas
Jinja2
HTML / CSS / JavaScript
Markdown 리포트 생성
선택: PDF 변환
```

### 선택하지 않는 것

초기 버전에서는 아래 기술은 일부러 제외한다.

```text
Docker
Redis
Kafka
Elasticsearch
실제 AI 모델
실시간 스트리밍 처리
복잡한 프론트엔드 프레임워크
```

이유:

```text
목표는 실무급 솔루션이 아니라 보안 로그 흐름을 이해하는 것이다.
처음부터 기술을 많이 넣으면 로그 분석보다 환경 구축에 시간을 빼앗긴다.
```

---

## 5. 주요 기능

## 5.1 로그 CSV 업로드

### 기능 설명

사용자가 보안 로그 CSV 파일을 업로드하면 서버가 CSV를 읽고 DB에 저장한다.

### API

```text
POST /api/logs/upload
```

### 입력 파일 예시

```csv
timestamp,device_type,src_ip,src_port,dst_ip,dst_port,protocol,event_type,action,severity,message
2026-06-26 10:12:01,FW,10.0.0.15,52144,172.16.0.5,22,TCP,PORT_SCAN,DENY,MEDIUM,Multiple port access detected
2026-06-26 10:13:20,WAF,10.0.0.15,52145,172.16.0.5,443,HTTPS,SQL_INJECTION,BLOCK,HIGH,SQL injection pattern detected
2026-06-26 10:15:02,IPS,10.0.0.15,52146,172.16.0.5,443,TCP,SIGNATURE_HIT,BLOCK,HIGH,Known attack signature detected
```

### 학습 포인트

```text
CSV 파싱
로그 필드 구조
날짜 문자열을 datetime으로 변환
DB 저장
잘못된 데이터 예외 처리
```

---

## 5.2 로그 목록 조회

### 기능 설명

DB에 저장된 로그를 목록으로 조회한다.

### API

```text
GET /api/logs
```

### 필터 조건

```text
src_ip
dst_ip
device_type
event_type
severity
action
start_time
end_time
```

### 예시

```text
GET /api/logs?src_ip=10.0.0.15
GET /api/logs?event_type=SQL_INJECTION
GET /api/logs?device_type=WAF&severity=HIGH
```

### 학습 포인트

```text
로그 검색
쿼리 파라미터
날짜 범위 조회
페이지네이션
관리자 화면의 필터 구조
```

---

## 5.3 위협 이벤트 분석

### 기능 설명

같은 출발지 IP가 일정 시간 안에 만든 로그를 묶고, 공격 흐름을 분석한다.

### 기본 기준

```text
분석 기준: src_ip
시간 윈도우: 10분
대상: MEDIUM 이상 로그
```

### 분석 흐름

```text
1. 로그를 시간순으로 정렬한다.
2. src_ip 기준으로 그룹을 나눈다.
3. 같은 src_ip의 로그 중 10분 이내에 발생한 이벤트를 묶는다.
4. 이벤트 타입별 점수를 합산한다.
5. 점수 기준에 따라 위험 등급을 정한다.
6. 공격 흐름 설명을 생성한다.
```

### API

```text
POST /api/incidents/analyze
```

### 학습 포인트

```text
시간 기반 그룹핑
IP 기준 분석
공격 시나리오 구성
단일 로그와 묶음 로그의 차이
```

---

## 5.4 위험도 점수화

### 이벤트별 기본 점수

| 이벤트 타입 | 점수 | 설명 |
|---|---:|---|
| PORT_SCAN | 40 | 여러 포트 접근 시도 |
| SQL_INJECTION | 30 | SQL 삽입 공격 의심 |
| XSS | 25 | 스크립트 삽입 공격 의심 |
| PATH_TRAVERSAL | 25 | 서버 파일 경로 접근 시도 |
| BRUTE_FORCE | 35 | 반복 로그인 시도 |
| SIGNATURE_HIT | 20 | IPS 공격 시그니처 탐지 |
| MALICIOUS_BOT | 30 | 악성 봇 의심 |
| DDoS_PATTERN | 50 | 대량 요청 패턴 |

### 보정 점수

| 조건 | 추가 점수 | 설명 |
|---|---:|---|
| 10분 이내 이벤트 3개 이상 | +15 | 짧은 시간에 여러 이벤트 발생 |
| FW → WAF → IPS 순서 발생 | +20 | 공격 흐름이 단계적으로 이어짐 |
| action이 BLOCK 또는 DENY | +5 | 보안 장비가 차단 판단 |
| severity가 CRITICAL | +20 | 심각도 높음 |
| 동일 dst_ip에 집중 | +10 | 특정 서버 대상 공격 가능성 |

### 위험 등급 기준

| 점수 | 등급 | 의미 |
|---:|---|---|
| 0 ~ 39 | LOW | 단일 이벤트 또는 낮은 위험 |
| 40 ~ 69 | MEDIUM | 주의가 필요한 의심 이벤트 |
| 70 ~ 99 | HIGH | 침해 사고 의심 |
| 100 이상 | CRITICAL | 즉시 확인이 필요한 고위험 이벤트 |

### 학습 포인트

```text
룰 기반 탐지
점수화 기준
Threshold
오탐 가능성
정탐 가능성
위험도 설명
```

---

## 5.5 판단 근거 생성

### 기능 설명

분석된 Incident에 대해 사람이 이해할 수 있는 설명을 생성한다.

### 설명 구성

```text
1. 어떤 IP가 의심되는가?
2. 어떤 시간 범위에서 이벤트가 발생했는가?
3. 어떤 이벤트들이 순서대로 발생했는가?
4. 각 이벤트가 점수에 어떻게 반영되었는가?
5. 최종 위험 등급은 무엇인가?
6. 어떤 조치를 검토해야 하는가?
```

### 출력 예시

```text
출발지 IP 10.0.0.15는 2026-06-26 10:12부터 10:15까지 3분 동안 PORT_SCAN, SQL_INJECTION, SIGNATURE_HIT 이벤트를 연속으로 발생시켰다.

먼저 FW 로그에서 여러 포트 접근 시도가 차단되었고, 이후 WAF 로그에서 SQL Injection 패턴이 탐지되었다.
마지막으로 IPS에서 알려진 공격 시그니처가 탐지되었기 때문에, 단순한 접근 실패보다는 공격 흐름이 이어진 것으로 판단한다.

기본 점수는 PORT_SCAN 40점, SQL_INJECTION 30점, SIGNATURE_HIT 20점이며, 짧은 시간 내 연속 이벤트와 FW-WAF-IPS 흐름이 확인되어 추가 점수가 반영되었다.
최종 위험도는 105점으로 CRITICAL 등급이다.
```

### 학습 포인트

```text
XAI
Rule explanation
보안 담당자용 문장 구성
분석 결과 요약
```

---

## 5.6 Incident 저장

### 기능 설명

분석 결과를 Incident 단위로 저장한다.

### Incident란?

```text
개별 로그 한 줄이 아니라, 여러 로그가 하나의 공격 흐름으로 묶인 분석 결과
```

### 예시

```text
Incident ID: 1
src_ip: 10.0.0.15
dst_ip: 172.16.0.5
start_time: 2026-06-26 10:12:01
end_time: 2026-06-26 10:15:02
event_count: 3
score: 105
risk_level: CRITICAL
status: OPEN
```

### 학습 포인트

```text
로그와 사건의 차이
분석 결과 저장
상태 관리
OPEN / REVIEWED / CLOSED
```

---

## 5.7 리포트 생성

### 기능 설명

Incident 하나를 선택하면 Markdown 리포트를 생성한다.

### API

```text
POST /api/reports/{incident_id}
GET /api/reports/{incident_id}
```

### Markdown 리포트 예시

```markdown
# 침해 사고 의심 리포트

## 1. 요약
출발지 IP 10.0.0.15에서 3분 이내에 포트 스캔, SQL Injection, IPS 시그니처 탐지 이벤트가 연속 발생했다.

## 2. 기본 정보
- 출발지 IP: 10.0.0.15
- 목적지 IP: 172.16.0.5
- 시작 시간: 2026-06-26 10:12:01
- 종료 시간: 2026-06-26 10:15:02
- 위험도: CRITICAL
- 점수: 105

## 3. 탐지 이벤트
| 시간 | 장비 | 이벤트 | 조치 | 심각도 |
|---|---|---|---|---|
| 10:12:01 | FW | PORT_SCAN | DENY | MEDIUM |
| 10:13:20 | WAF | SQL_INJECTION | BLOCK | HIGH |
| 10:15:02 | IPS | SIGNATURE_HIT | BLOCK | HIGH |

## 4. 판단 근거
FW, WAF, IPS에서 순차적으로 이벤트가 발생했으며, 이는 단순 단일 이벤트보다 공격 단계가 이어진 흐름으로 볼 수 있다.

## 5. 권장 조치
- 출발지 IP 차단 여부 검토
- 목적지 서버의 웹 접근 로그 확인
- 동일 IP의 과거 접속 이력 확인
- 유사 공격 패턴 추가 탐지 여부 확인
```

### 학습 포인트

```text
리포트 자동화
템플릿 구성
분석 결과 문서화
Markdown 파일 생성
```

---

## 5.8 관리자 화면

### 화면 목록

```text
/                      대시보드
/logs                  로그 목록
/incidents             위협 의심 사건 목록
/incidents/{id}        위협 상세
/reports/{id}          리포트 보기
/upload                로그 업로드
```

### 대시보드 표시 항목

```text
전체 로그 수
위험 이벤트 수
Incident 수
HIGH 이상 Incident 수
가장 많이 탐지된 이벤트 타입
가장 많이 등장한 출발지 IP
최근 24시간 위험도 추이
```

### 로그 목록 화면

표시 필드:

```text
timestamp
device_type
src_ip
src_port
dst_ip
dst_port
protocol
event_type
action
severity
```

### Incident 상세 화면

표시 항목:

```text
위험 점수
위험 등급
출발지 IP
목적지 IP
발생 시간 범위
관련 로그 목록
점수 계산 근거
자동 생성 설명
리포트 생성 버튼
```

---

## 6. DB 설계

초기에는 SQLite를 사용한다.

## 6.1 security_logs 테이블

```sql
CREATE TABLE security_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME NOT NULL,
    device_type VARCHAR(20) NOT NULL,
    src_ip VARCHAR(45) NOT NULL,
    src_port INTEGER,
    dst_ip VARCHAR(45) NOT NULL,
    dst_port INTEGER,
    protocol VARCHAR(20),
    event_type VARCHAR(50) NOT NULL,
    action VARCHAR(20),
    severity VARCHAR(20),
    message TEXT,
    raw_log TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 주요 필드 설명

| 필드 | 설명 |
|---|---|
| timestamp | 로그 발생 시간 |
| device_type | FW, WAF, IPS |
| src_ip | 출발지 IP |
| src_port | 출발지 포트 |
| dst_ip | 목적지 IP |
| dst_port | 목적지 포트 |
| protocol | TCP, UDP, HTTP, HTTPS |
| event_type | PORT_SCAN, SQL_INJECTION 등 |
| action | ALLOW, DENY, BLOCK |
| severity | LOW, MEDIUM, HIGH, CRITICAL |
| message | 로그 설명 |
| raw_log | 원본 로그 문자열 |

---

## 6.2 incidents 테이블

```sql
CREATE TABLE incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    src_ip VARCHAR(45) NOT NULL,
    dst_ip VARCHAR(45),
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    event_count INTEGER NOT NULL,
    score INTEGER NOT NULL,
    risk_level VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'OPEN',
    summary TEXT,
    explanation TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### status 값

```text
OPEN       아직 확인하지 않음
REVIEWED   확인 완료
CLOSED     조치 완료 또는 무시
```

---

## 6.3 incident_logs 테이블

Incident와 관련 로그를 연결한다.

```sql
CREATE TABLE incident_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    log_id INTEGER NOT NULL,
    FOREIGN KEY (incident_id) REFERENCES incidents(id),
    FOREIGN KEY (log_id) REFERENCES security_logs(id)
);
```

---

## 6.4 reports 테이블

```sql
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    file_path VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (incident_id) REFERENCES incidents(id)
);
```

---

## 7. 폴더 구조

```text
security-log-analyzer/
│
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   │
│   ├── models/
│   │   ├── security_log.py
│   │   ├── incident.py
│   │   └── report.py
│   │
│   ├── schemas/
│   │   ├── log_schema.py
│   │   ├── incident_schema.py
│   │   └── report_schema.py
│   │
│   ├── api/
│   │   ├── log_api.py
│   │   ├── incident_api.py
│   │   └── report_api.py
│   │
│   ├── services/
│   │   ├── log_parser.py
│   │   ├── threat_analyzer.py
│   │   ├── score_engine.py
│   │   ├── explanation_generator.py
│   │   └── report_generator.py
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── logs.html
│   │   ├── incidents.html
│   │   ├── incident_detail.html
│   │   └── report.html
│   │
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── main.js
│
├── data/
│   ├── sample_logs.csv
│   └── uploaded/
│
├── reports/
│   └── generated/
│
├── tests/
│   ├── test_score_engine.py
│   ├── test_log_parser.py
│   └── test_threat_analyzer.py
│
├── requirements.txt
├── README.md
└── 설계도.md
```

---

## 8. 핵심 모듈 설계

## 8.1 log_parser.py

### 역할

```text
CSV 파일을 읽고, 각 행을 SecurityLog 객체로 변환한다.
```

### 주요 함수

```python
def parse_csv(file_path: str) -> list[dict]:
    pass


def validate_log_row(row: dict) -> bool:
    pass


def normalize_log_row(row: dict) -> dict:
    pass
```

### 책임

```text
timestamp 형식 변환
비어 있는 포트 처리
장비 타입 검증
이벤트 타입 검증
severity 대문자 통일
```

---

## 8.2 score_engine.py

### 역할

```text
로그 이벤트 목록을 받아 위험 점수를 계산한다.
```

### 주요 함수

```python
def calculate_event_score(event_type: str) -> int:
    pass


def calculate_bonus_score(logs: list) -> int:
    pass


def calculate_total_score(logs: list) -> int:
    pass


def get_risk_level(score: int) -> str:
    pass
```

### 책임

```text
이벤트별 기본 점수 부여
연속 이벤트 보정 점수 계산
FW-WAF-IPS 흐름 보정
위험 등급 결정
```

---

## 8.3 threat_analyzer.py

### 역할

```text
로그를 src_ip와 시간 윈도우 기준으로 묶고 Incident 후보를 만든다.
```

### 주요 함수

```python
def group_logs_by_src_ip(logs: list) -> dict:
    pass


def create_time_windows(logs: list, minutes: int = 10) -> list[list]:
    pass


def analyze_threats(logs: list) -> list[dict]:
    pass
```

### 책임

```text
로그 시간순 정렬
src_ip 기준 그룹핑
10분 이내 이벤트 묶기
위험 점수 계산 요청
Incident 후보 생성
```

---

## 8.4 explanation_generator.py

### 역할

```text
Incident 분석 결과를 사람이 이해할 수 있는 문장으로 변환한다.
```

### 주요 함수

```python
def generate_summary(incident: dict, logs: list) -> str:
    pass


def generate_explanation(incident: dict, logs: list) -> str:
    pass


def generate_recommendations(incident: dict, logs: list) -> list[str]:
    pass
```

### 책임

```text
위협 요약 생성
판단 근거 생성
점수 산정 이유 설명
권장 조치 생성
```

---

## 8.5 report_generator.py

### 역할

```text
Incident 정보를 기반으로 Markdown 리포트를 생성한다.
```

### 주요 함수

```python
def generate_markdown_report(incident: dict, logs: list) -> str:
    pass


def save_report(content: str, incident_id: int) -> str:
    pass
```

### 책임

```text
리포트 템플릿 구성
Incident 정보 삽입
관련 로그 표 생성
Markdown 파일 저장
```

---

## 9. API 설계

## 9.1 로그 API

| Method | URL | 설명 |
|---|---|---|
| POST | /api/logs/upload | CSV 로그 업로드 |
| GET | /api/logs | 로그 목록 조회 |
| GET | /api/logs/{log_id} | 로그 상세 조회 |
| DELETE | /api/logs | 전체 로그 삭제 |

### GET /api/logs 응답 예시

```json
{
  "items": [
    {
      "id": 1,
      "timestamp": "2026-06-26T10:12:01",
      "device_type": "FW",
      "src_ip": "10.0.0.15",
      "dst_ip": "172.16.0.5",
      "dst_port": 22,
      "protocol": "TCP",
      "event_type": "PORT_SCAN",
      "action": "DENY",
      "severity": "MEDIUM"
    }
  ],
  "total": 1
}
```

---

## 9.2 Incident API

| Method | URL | 설명 |
|---|---|---|
| POST | /api/incidents/analyze | 로그 분석 실행 |
| GET | /api/incidents | Incident 목록 조회 |
| GET | /api/incidents/{incident_id} | Incident 상세 조회 |
| PATCH | /api/incidents/{incident_id}/status | Incident 상태 변경 |

### POST /api/incidents/analyze 응답 예시

```json
{
  "created_count": 1,
  "incidents": [
    {
      "id": 1,
      "src_ip": "10.0.0.15",
      "dst_ip": "172.16.0.5",
      "score": 105,
      "risk_level": "CRITICAL",
      "event_count": 3,
      "summary": "10.0.0.15에서 3분 이내에 복수 보안 이벤트가 연속 발생했습니다."
    }
  ]
}
```

---

## 9.3 Report API

| Method | URL | 설명 |
|---|---|---|
| POST | /api/reports/{incident_id} | 리포트 생성 |
| GET | /api/reports/{incident_id} | 리포트 조회 |
| GET | /api/reports/{incident_id}/download | 리포트 파일 다운로드 |

---

## 10. 샘플 데이터 설계

## 10.1 정상 로그

```csv
timestamp,device_type,src_ip,src_port,dst_ip,dst_port,protocol,event_type,action,severity,message
2026-06-26 09:00:01,FW,10.0.0.10,50001,172.16.0.5,443,TCP,NORMAL_ACCESS,ALLOW,LOW,Normal HTTPS access
2026-06-26 09:01:05,WAF,10.0.0.10,50002,172.16.0.5,443,HTTPS,NORMAL_REQUEST,ALLOW,LOW,Normal web request
```

## 10.2 포트 스캔 의심

```csv
2026-06-26 10:00:01,FW,10.0.0.20,51001,172.16.0.5,21,TCP,PORT_SCAN,DENY,MEDIUM,Port scan detected
2026-06-26 10:00:03,FW,10.0.0.20,51002,172.16.0.5,22,TCP,PORT_SCAN,DENY,MEDIUM,Port scan detected
2026-06-26 10:00:05,FW,10.0.0.20,51003,172.16.0.5,23,TCP,PORT_SCAN,DENY,MEDIUM,Port scan detected
```

## 10.3 웹 공격 의심

```csv
2026-06-26 10:13:20,WAF,10.0.0.15,52145,172.16.0.5,443,HTTPS,SQL_INJECTION,BLOCK,HIGH,SQL injection pattern detected
2026-06-26 10:13:40,WAF,10.0.0.15,52146,172.16.0.5,443,HTTPS,XSS,BLOCK,HIGH,XSS pattern detected
2026-06-26 10:14:02,WAF,10.0.0.15,52147,172.16.0.5,443,HTTPS,PATH_TRAVERSAL,BLOCK,HIGH,Path traversal pattern detected
```

## 10.4 복합 공격 흐름

```csv
2026-06-26 10:12:01,FW,10.0.0.15,52144,172.16.0.5,22,TCP,PORT_SCAN,DENY,MEDIUM,Multiple port access detected
2026-06-26 10:13:20,WAF,10.0.0.15,52145,172.16.0.5,443,HTTPS,SQL_INJECTION,BLOCK,HIGH,SQL injection pattern detected
2026-06-26 10:15:02,IPS,10.0.0.15,52146,172.16.0.5,443,TCP,SIGNATURE_HIT,BLOCK,HIGH,Known attack signature detected
```

---

## 11. 구현 단계

## 1단계: 프로젝트 초기 세팅

### 목표

```text
FastAPI 프로젝트 실행
SQLite 연결
기본 폴더 구조 생성
```

### 완료 기준

```text
uvicorn app.main:app --reload 실행 가능
/docs 접근 가능
SQLite DB 파일 생성
```

---

## 2단계: DB 모델 생성

### 목표

```text
security_logs
incidents
incident_logs
reports
```

테이블을 SQLAlchemy 모델로 만든다.

### 완료 기준

```text
앱 실행 시 테이블 생성
DB Browser for SQLite로 테이블 확인 가능
```

---

## 3단계: 샘플 로그 CSV 작성

### 목표

```text
정상 로그
포트 스캔 로그
웹 공격 로그
복합 공격 로그
```

샘플 데이터를 직접 만든다.

### 완료 기준

```text
data/sample_logs.csv 파일 존재
최소 30개 이상의 로그 포함
정상/위험 로그가 섞여 있음
```

---

## 4단계: CSV 업로드 및 저장

### 목표

```text
POST /api/logs/upload
```

CSV를 업로드하면 DB에 저장한다.

### 완료 기준

```text
업로드 후 security_logs 테이블에 데이터 저장
잘못된 행은 스킵하거나 에러 메시지 출력
```

---

## 5단계: 로그 조회 API

### 목표

```text
GET /api/logs
```

필터링 가능한 로그 목록 API를 만든다.

### 완료 기준

```text
src_ip 필터 가능
event_type 필터 가능
device_type 필터 가능
start_time / end_time 필터 가능
```

---

## 6단계: 점수 엔진 구현

### 목표

이벤트 타입별 점수와 보정 점수를 계산한다.

### 완료 기준

```text
PORT_SCAN = 40
SQL_INJECTION = 30
SIGNATURE_HIT = 20
연속 이벤트 보정 점수 적용
risk_level 반환
```

---

## 7단계: 위협 분석 구현

### 목표

```text
POST /api/incidents/analyze
```

로그를 분석해서 Incident를 생성한다.

### 완료 기준

```text
src_ip 기준 그룹핑
10분 윈도우 기준 묶기
점수 40점 이상이면 Incident 생성
관련 로그 incident_logs에 연결
```

---

## 8단계: 설명 생성 구현

### 목표

Incident의 판단 근거를 문장으로 만든다.

### 완료 기준

```text
summary 생성
explanation 생성
recommendations 생성
점수 계산 근거 포함
```

---

## 9단계: 리포트 생성

### 목표

Incident를 Markdown 리포트로 저장한다.

### 완료 기준

```text
reports/generated/incident_{id}.md 생성
리포트 내용에 요약/기본정보/로그표/판단근거/권장조치 포함
```

---

## 10단계: 관리자 화면 구현

### 목표

HTML 기반 관리자 화면을 만든다.

### 완료 기준

```text
/upload에서 CSV 업로드 가능
/logs에서 로그 목록 확인 가능
/incidents에서 Incident 목록 확인 가능
/incidents/{id}에서 상세 확인 가능
/reports/{id}에서 리포트 확인 가능
```

---

## 12. 학습 체크리스트

## 네트워크

- [ ] src_ip와 dst_ip의 차이를 설명할 수 있다.
- [ ] dst_port가 22, 80, 443일 때 의미를 알 수 있다.
- [ ] TCP와 UDP의 차이를 간단히 설명할 수 있다.
- [ ] HTTP/HTTPS 요청이 WAF와 연결되는 이유를 설명할 수 있다.

## 보안 장비

- [ ] FW 로그와 WAF 로그의 차이를 설명할 수 있다.
- [ ] IPS가 어떤 상황에서 탐지 로그를 남기는지 설명할 수 있다.
- [ ] DENY와 BLOCK의 의미를 이해한다.
- [ ] severity가 LOW/MEDIUM/HIGH/CRITICAL로 나뉘는 이유를 이해한다.

## 웹 보안

- [ ] SQL Injection이 무엇인지 설명할 수 있다.
- [ ] XSS가 무엇인지 설명할 수 있다.
- [ ] Path Traversal이 무엇인지 설명할 수 있다.
- [ ] Brute Force와 Credential Stuffing의 차이를 설명할 수 있다.

## 로그 분석

- [ ] 로그를 시간순으로 정렬할 수 있다.
- [ ] 같은 IP의 로그를 그룹핑할 수 있다.
- [ ] 특정 시간 안에 발생한 이벤트를 묶을 수 있다.
- [ ] 단일 로그와 Incident의 차이를 설명할 수 있다.

## XAI

- [ ] 위험 점수가 왜 나왔는지 설명할 수 있다.
- [ ] 어떤 이벤트가 점수에 영향을 줬는지 출력할 수 있다.
- [ ] 판단 근거를 사람이 읽을 수 있는 문장으로 만들 수 있다.

## 리포트

- [ ] Incident 정보를 Markdown 리포트로 만들 수 있다.
- [ ] 관련 로그를 표로 정리할 수 있다.
- [ ] 권장 조치를 자동으로 출력할 수 있다.

---

## 13. 구현 시 주의할 점

### 13.1 실제 보안 로그를 쓰지 않는다

학습용 프로젝트이므로 실제 회사나 실제 시스템 로그를 사용하지 않는다.

```text
개인정보
실제 IP
실제 서버명
실제 공격 로그
고객사 정보
```

이런 정보는 사용하지 않는다.

샘플 로그는 직접 만든 가짜 데이터만 사용한다.

---

### 13.2 AI 모델을 처음부터 넣지 않는다

이 프로젝트의 핵심은 AI 모델이 아니다.

```text
로그를 어떻게 읽는지
어떻게 묶는지
왜 위험하다고 판단하는지
그 판단을 어떻게 설명하는지
```

이 흐름을 먼저 이해하는 것이 중요하다.

나중에 여유가 있으면 LLM을 붙여서 리포트 문장을 더 자연스럽게 만들 수 있다.

---

### 13.3 점수 규칙은 정답이 아니다

이 프로젝트의 점수 규칙은 학습용이다.

```text
PORT_SCAN = 40
SQL_INJECTION = 30
SIGNATURE_HIT = 20
```

이런 숫자는 실제 보안 솔루션의 기준이 아니라, “점수화 구조를 이해하기 위한 임의 기준”이다.

중요한 것은 점수 그 자체가 아니라 다음이다.

```text
어떤 이벤트가 위험도에 영향을 주는가?
왜 추가 점수가 붙는가?
점수가 높으면 어떤 조치를 해야 하는가?
```

---

## 14. 최종 완성 기준

이 프로젝트가 완성되었다고 볼 수 있는 기준은 다음과 같다.

```text
1. 샘플 보안 로그 CSV를 업로드할 수 있다.
2. 업로드한 로그가 DB에 저장된다.
3. 로그 목록을 필터링해서 볼 수 있다.
4. 같은 IP의 이벤트를 시간 기준으로 묶을 수 있다.
5. 이벤트 타입과 조건에 따라 위험 점수를 계산할 수 있다.
6. 위험 점수에 따라 LOW/MEDIUM/HIGH/CRITICAL을 구분할 수 있다.
7. Incident 상세 화면에서 관련 로그를 볼 수 있다.
8. 왜 위험한지 설명 문장을 볼 수 있다.
9. Markdown 리포트를 생성할 수 있다.
10. 구현하면서 FW/WAF/IPS/로그/위험도/XAI 개념을 설명할 수 있게 된다.
```

---

## 15. 이후 확장 아이디어

초기 버전을 완성한 뒤, 이해가 더 필요하면 다음을 추가한다.

### 15.1 PDF 리포트 변환

```text
Markdown → HTML → PDF
```

### 15.2 차트 추가

```text
이벤트 타입별 개수
시간대별 위험 이벤트 수
src_ip별 위험도 순위
```

### 15.3 간단한 LLM 리포트 보정

```text
룰 기반으로 만든 분석 결과를 LLM에게 전달
더 자연스러운 보고서 문장 생성
```

단, LLM은 판단을 직접 하게 하지 말고 문장 정리에만 사용한다.

### 15.4 실시간 로그 흉내내기

```text
샘플 로그를 1초마다 하나씩 DB에 넣기
관리자 화면에서 새 로그 갱신
```

### 15.5 검색 성능 개선

```text
날짜 인덱스
src_ip 인덱스
event_type 인덱스
```

### 15.6 Elasticsearch 연동

로그가 많아지는 상황을 가정하고 검색 엔진을 붙여본다.

---

## 16. 추천 학습 순서

이 프로젝트를 만들면서 공부할 때는 아래 순서가 좋다.

```text
1. IP / Port / Protocol
2. FW / WAF / IPS 개념
3. 웹 공격 유형
4. 보안 로그 필드 구조
5. CSV 파싱
6. FastAPI 업로드 API
7. DB 저장
8. 로그 검색
9. 시간 기반 그룹핑
10. 위험도 점수화
11. XAI 설명 생성
12. 리포트 자동 생성
```

---

## 17. 이 프로젝트의 핵심 문장

이 프로젝트를 만들고 나면 다음 문장을 스스로 설명할 수 있어야 한다.

```text
보안 로그 한 줄은 단편적인 이벤트일 뿐이지만, 같은 IP와 시간 흐름을 기준으로 여러 장비의 로그를 연결하면 공격의 맥락을 추론할 수 있다.
그리고 그 판단 결과는 점수뿐 아니라, 어떤 로그와 어떤 규칙 때문에 위험하다고 판단했는지 함께 설명되어야 한다.
```

