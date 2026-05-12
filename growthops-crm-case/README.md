# GrowthOps CRM Case Project

마케팅/CRM 데이터를 기반으로 리드 후속 대응 우선순위를 산정하는 Python + CSV 기반 데이터 파이프라인 MVP입니다. 완성형 CRM SaaS가 아니라, 더미데이터 생성부터 데이터 품질 검증, 규칙 기반 리드 스코어링, 캠페인 성과 지표 산출까지 재현 가능하게 실행되는 제출용 프로젝트입니다.

이 프로젝트는 데이터 품질 이슈가 있는 리드를 자동 계산 대상과 수동 검토 대상으로 구분합니다. FastAPI는 핵심 파이프라인이 아니라, 산출된 CSV 결과를 조회하기 위한 선택 확장 기능입니다.

## 1. 프로젝트 목적

마케팅 캠페인, 리드, 고객 행동 이벤트, 전환 데이터를 활용해 영업 후속 대응 우선순위를 계산하고, 캠페인별 성과와 데이터 품질 이슈를 CSV 산출물로 정리합니다.

## 2. 문제 정의

CRM 데이터는 이메일 누락, 중복 리드, 잘못된 캠페인 참조, 봇성 행동 같은 품질 문제가 섞여 있을 수 있습니다. 이 프로젝트는 품질 이슈가 있는 리드를 자동 점수 계산에서 분리하고, 정상 리드에는 설명 가능한 규칙 기반 점수를 부여합니다.

## 3. 실행 방법

```bash
pip install -r requirements.txt
python src/main.py
```

실행하면 `data/raw/` 아래 원천 더미 CSV가 생성되고, `data/processed/` 아래 최종 산출물 3개가 저장됩니다.

테스트 실행:

```bash
pytest -q
```

## 4. 폴더 구조

```text
growthops-crm-case/
  README.md
  requirements.txt
  src/
    api.py
    main.py
    config.py
    data_generator.py
    loader.py
    cleaner.py
    quality_validator.py
    scorer.py
    metrics.py
    reporter.py
  data/
    raw/
    processed/
  docs/
    validation-summary.md
    scoring-rules.md
    data-quality-rules.md
    final-report.md
    submission-checklist.md
  tests/
    conftest.py
    test_api.py
    test_metrics.py
    test_quality_validator.py
    test_scorer.py
```

## 5. 데이터 품질 검증 기준

HIGH:

- `missing_email`
- `invalid_lead_campaign_reference`
- `invalid_event_lead_reference`
- `invalid_event_campaign_reference`
- `invalid_conversion_lead_reference`
- `duplicate_email`
- `suspicious_bot_behavior`

MEDIUM:

- `duplicate_company_name`
- `missing_campaign_utm_code`

LOW:

- `unknown_source_or_blank_optional_field`

Manual Review 리드는 이메일 누락, 이메일 중복, 유효하지 않은 `source_campaign_id`, 10분 이내 15개 이상 이벤트가 발생한 봇성 행동 의심 조건 중 하나라도 만족하는 리드입니다.

## 6. 리드 스코어링 기준

Manual Review가 아닌 리드는 기본 10점에서 시작합니다. 행동 이벤트, 전환 이력, 회사 규모, 직무, 산업군, 캠페인 예산과 채널에 따라 점수를 더하고, UTM 누락 또는 최근 이벤트 부재는 감점합니다. 최종 점수는 0~100점으로 제한합니다.

등급 기준:

- `Hot`: 75점 이상
- `Warm`: 45점 이상 75점 미만
- `Cold`: 45점 미만
- `Manual Review`: 데이터 품질 확인 후 수동 검토

## 7. 산출물 설명

- `data/processed/lead_scores.csv`: 리드별 점수, 등급, 한국어 사유, 추천 후속 액션, 품질 상태
- `data/processed/campaign_metrics.csv`: 캠페인별 리드 수, 유효 리드 수, Hot 리드 수, 전환 수, 전환율, 품질 이슈 수
- `data/processed/data_quality_report.csv`: 품질 이슈 유형별 건수, 심각도, 샘플 ID

## 8. 선택 기능: FastAPI 결과 조회 API

이 API는 필수 파이프라인이 아니라, 생성된 CSV 산출물을 조회하기 위한 선택 확장 기능입니다. DB, 인증, 대시보드 없이 `data/processed/` 아래 CSV를 읽어 JSON으로 반환합니다.

먼저 파이프라인을 실행합니다.

```bash
python src/main.py
```

API 실행:

```bash
uvicorn src.api:app --reload
```

접속 예시:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/lead-scores`
- `http://127.0.0.1:8000/campaign-metrics`
- `http://127.0.0.1:8000/data-quality-report`

## 9. 제출용 설명 문서

- [검증 결과 요약](docs/validation-summary.md)
- [리드 스코어링 규칙](docs/scoring-rules.md)
- [데이터 품질 검증 규칙](docs/data-quality-rules.md)
- [최종 해설 보고서](docs/final-report.md)
- [제출 전 체크리스트](docs/submission-checklist.md)

## 10. 확장 가능성

- FastAPI 결과 조회 API
- 대시보드
- Airflow 스케줄링
- 실제 CRM/광고 API 연동
- 클라우드 저장소 연동
