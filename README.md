DeepRadar - Cyber Threat Intelligence Platform

다크웹 및 유출 데이터를 수집·분석하여 실시간 위협 인텔리전스를 제공하는 CTI(Cyber Threat Intelligence) 통합 관제 시스템

프로젝트 소개

최근 다크웹과 인포스틸러(Infostealer)를 통한 계정 정보 유출이 증가하면서, 유출 데이터를 신속하게 수집·분석하고 대응할 수 있는 보안 플랫폼의 필요성이 커지고 있습니다.

본 프로젝트는 다크웹에서 수집된 비정형 데이터를 자동으로 분석하여 계정 정보와 침해지표(IoC)를 추출하고, 이를 실시간 관제 시스템에서 관리할 수 있는 CTI(Cyber Threat Intelligence) 플랫폼을 구축하는 것을 목표로 개발되었습니다.

전체 시스템은 수집기(Collector), 데이터 처리기(Parser), API Gateway, Database, Dashboard를 하나의 파이프라인으로 연결하여 실시간 위협 정보를 관리할 수 있도록 설계하였습니다.

시스템 아키텍처
Crawler / Collector
        │
        ▼
API Gateway
        │
        ▼
Regex Parser
        │
        ▼
Validation
        │
        ▼
Database
        │
        ▼
Dashboard
        │
        ▼
Telegram Notification

API Gateway를 중심으로 모든 데이터가 통합 처리되며, 데이터 검증 이후에만 Database에 저장되도록 설계하였습니다.

주요 기능
1. 다크웹 데이터 수집

Collector를 통해 다크웹과 유출 사이트에서 Raw 데이터를 수집합니다.

수집 대상

계정 정보
이메일
패스워드
인포스틸러 로그
유출 데이터베이스

수집된 데이터는 API Gateway를 통해 분석 서버로 전달됩니다.

2. Regex 기반 IoC 추출

수집된 Raw 데이터는 다양한 형식으로 존재합니다.

예를 들어

user=test

mail=test@gmail.com

password=1234

또는

id : admin

pw : qwer1234

처럼 형식이 모두 다릅니다.

Regex Parser를 구현하여

Email
ID
Password

등의 IoC(Indicator of Compromise)를 자동으로 추출하도록 개발하였습니다.

3. API Gateway

모든 데이터는 API Gateway를 통해 처리됩니다.

Gateway에서는

API Key 인증
JWT 인증
입력값 검증(Input Validation)
데이터 중복 제거
JSON 표준화
저장 승인

과정을 수행합니다.

외부 모듈은 Database에 직접 접근하지 않고 반드시 Gateway를 거치도록 설계하여 시스템 신뢰성과 보안을 강화하였습니다.

4. JWT 및 API Key 인증

관리자 시스템은 JWT 기반 인증을 적용하였습니다.

Collector와 Parser는 로그인 기능을 사용할 수 없기 때문에 API Key 기반 인증을 별도로 구현하였습니다.

이를 통해

관리자
수집기
데이터 처리기

를 서로 다른 인증 체계로 관리하도록 설계하였습니다.

5. 데이터 정제 및 표준화

수집되는 데이터는 형식이 모두 다르기 때문에

Null 데이터 제거
필수값 검증
중복 제거
JSON 표준화

과정을 거쳐 Database에 저장하도록 구현하였습니다.

이를 통해 동일한 유출 데이터가 여러 번 저장되는 문제를 방지하였습니다.

6. Dashboard

관리자는 Dashboard에서

전체 유출 건수
최근 탐지 현황
위협 검색
엔진 상태
조치 상태

를 실시간으로 확인할 수 있습니다.

또한 특정 계정이나 이메일을 검색하여 관련 유출 정보를 빠르게 조회할 수 있도록 구현하였습니다.

7. Telegram 알림

새로운 위협이 탐지되거나 관리자의 즉각적인 대응이 필요한 경우 Telegram Bot API를 이용하여 실시간 알림을 전송하도록 구현하였습니다.

이를 통해 별도의 Dashboard 접속 없이도 주요 보안 이벤트를 확인할 수 있습니다.

8. 운영 환경

프로젝트는 VMware 기반 개발 환경에서 Docker를 이용하여 컨테이너를 구성하였습니다.

GitHub Actions를 이용한 CI/CD를 구축하여 코드 변경 시 자동으로 배포가 수행되도록 구성하였으며, EC2 환경에서 운영 테스트를 진행하였습니다.

Swagger를 이용하여 API 문서를 자동 생성하고 협업 효율성을 높였습니다.

데이터 처리 흐름
Raw Data
      │
      ▼
Regex Parser
      │
      ▼
IoC Extraction
      │
      ▼
Validation
      │
      ▼
Duplicate Check
      │
      ▼
JSON Normalization
      │
      ▼
Database
      │
      ▼
Dashboard
기술 스택
Backend
Spring Boot
Spring Security
Spring Data JPA
JWT
OAuth2
Swagger
Database
MySQL
DevOps
Docker
Docker Compose
VMware
GitHub Actions
AWS EC2
Security
Regex Parsing
API Gateway
API Key Authentication
JWT Authentication
Input Validation
Notification
Telegram Bot API
주요 특징
Cyber Threat Intelligence(CTI) 플랫폼 구현
API Gateway 기반 중앙 통합 구조
Regex 기반 IoC 자동 추출
JWT 및 API Key 이중 인증
입력값 검증과 데이터 표준화
Dashboard 기반 실시간 위협 관제
Telegram 실시간 알림
GitHub Actions 기반 CI/CD
Docker 기반 운영 환경 구성
기대 효과
다크웹 유출 정보를 자동 수집·분석하여 신속한 위협 대응 지원
IoC 자동 추출과 데이터 표준화를 통해 분석 효율 향상
API Gateway 중심의 보안 아키텍처로 데이터 무결성과 시스템 안정성 확보
실시간 관제와 알림 기능을 통해 보안 운영자의 대응 시간을 단축
CI/CD와 컨테이너 기반 운영 환경을 통해 유지보수성과 확장성을 향상
