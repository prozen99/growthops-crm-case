# Validation Summary

## 실행 환경

- OS: Windows
- Python: 3.12.10
- 실행 위치: `C:\Users\admin\PycharmProjects\portfolio\growthops-crm-case`
- 주요 의존성: `pandas`, `pytest`

## 실행 명령어

```bash
pip install -r requirements.txt
python src/main.py
pytest
```

`python src/main.py` 실행 시 더미데이터 생성, CSV 로딩, 정제, 품질 검증, 리드 스코어링, 캠페인 지표 계산, 결과 저장이 한 번에 수행된다.

## 생성된 입력 파일 목록

- `data/raw/campaigns.csv`
- `data/raw/leads.csv`
- `data/raw/events.csv`
- `data/raw/conversions.csv`

## 생성된 출력 파일 목록

- `data/processed/lead_scores.csv`
- `data/processed/campaign_metrics.csv`
- `data/processed/data_quality_report.csv`

## 실행 결과 요약

- Raw leads count: 12
- Manual Review leads count: 5
- Hot leads count: 2
- Data quality issue count: 12
- pytest: 13 passed

## 중복 리드 제거/분리 전후 해석

이 MVP에서는 원천 데이터를 물리적으로 삭제하지 않고, 문제가 있는 리드를 `Manual Review`로 분리한다. 따라서 원천 리드 12건은 모두 `lead_scores.csv`에 남아 있으며, 데이터 추적이 가능하다.

중복 이메일 리드인 `L006`, `L007`은 같은 사람 또는 같은 계정이 중복 수집되었을 가능성이 높기 때문에 자동 점수 계산에서 제외했다. 이렇게 분리하지 않으면 같은 잠재 고객에게 중복 영업 연락이 발생하거나, 특정 캠페인의 리드 수가 과대 계산될 수 있다.

동일 회사명 리드인 `L008`, `L009`는 같은 회사의 서로 다른 담당자일 수도 있으므로 자동 삭제하지 않는다. 다만 `duplicate_company_name` 이슈로 표시해 운영자가 계정 단위 중복 여부를 확인할 수 있게 했다.

정리하면, 분리 전 원천 리드는 12건이고, 분리 후 자동 스코어링 대상은 7건, 수동 검토 대상은 5건이다.

## 데이터 품질 이슈 유형별 발생 의미

- `missing_email`: 이메일이 없어 실제 영업 또는 마케팅 후속 연락이 어렵다.
- `invalid_lead_campaign_reference`: 리드가 존재하지 않는 캠페인을 참조해 캠페인 성과 귀속이 불가능하다.
- `invalid_event_lead_reference`: 이벤트가 존재하지 않는 리드를 참조해 행동 데이터 신뢰도가 낮다.
- `invalid_event_campaign_reference`: 이벤트가 존재하지 않는 캠페인을 참조해 채널 성과 분석이 왜곡될 수 있다.
- `invalid_conversion_lead_reference`: 전환 데이터가 존재하지 않는 리드를 참조해 리드 단위 전환 분석이 어렵다.
- `duplicate_email`: 같은 이메일이 여러 리드로 생성되어 리드 수와 후속 연락 대상이 중복될 수 있다.
- `suspicious_bot_behavior`: 짧은 시간에 과도한 이벤트가 발생해 실제 관심 행동이 아닐 가능성이 있다.
- `duplicate_company_name`: 같은 회사가 여러 리드로 존재한다. 반드시 오류는 아니지만 계정 단위 중복 확인이 필요하다.
- `missing_campaign_utm_code`: UTM 코드가 없어 외부 유입 경로나 광고 추적이 불완전하다.
- `unknown_source_or_blank_optional_field`: 산업군, 회사 규모, 직무 같은 보조 정보가 비어 있어 점수 계산 근거가 줄어든다.

## Hot Lead와 Manual Review Lead가 나뉘는 기준

`Hot Lead`는 데이터 품질상 자동 계산이 가능한 리드 중 점수가 75점 이상인 리드다. 예를 들어 데모 요청, 웨비나 신청, 전환 이력, 의사결정권자 직무, 우선순위 산업군 같은 신호가 많을수록 높은 점수를 받는다.

`Manual Review Lead`는 점수가 낮아서가 아니라 자동 계산에 사용하기 위험한 데이터 품질 문제가 있는 리드다. 이메일 누락, 중복 이메일, 잘못된 캠페인 참조, 봇성 행동 의심 중 하나라도 해당하면 수동 검토 대상으로 분리한다.

이번 실행에서는 `L001`, `L002`가 Hot Lead로 분류되었고, `L005`, `L006`, `L007`, `L010`, `L011`은 Manual Review로 분리되었다.

## 캠페인별 성과 지표 해석

- `CAMP001`: 전체 리드 3건 중 유효 리드는 1건이다. `L005`는 이메일 누락, `L011`은 봇성 행동 의심으로 분리되었고, 존재하지 않는 리드를 참조하는 이벤트도 1건 있다. 유효 리드 대비 전환 기록이 2건이라 전환율은 2.0으로 계산된다.
- `CAMP002`: 전체 리드 3건 중 중복 이메일 리드 2건이 Manual Review로 분리되어 유효 리드는 1건이다. 전환 기록은 2건이지만, 이 중 1건은 존재하지 않는 리드를 참조하므로 캠페인 성과 해석 시 품질 이슈를 함께 확인해야 한다.
- `CAMP003`: 전체 리드 3건이 모두 자동 계산 대상이다. 전환 기록은 없어 전환율은 0.0이며, 보조 필드가 비어 있는 리드가 1건 있다.
- `CAMP004`: 전체 리드 2건이 모두 자동 계산 대상이지만 캠페인 UTM 누락과 동일 회사명 이슈가 있다. 전환 기록은 없어 전환율은 0.0이다.

현재 `conversion_rate`는 요구사항에 따라 `conversion_count / valid_lead_count`로 계산한다. 여기서 `conversion_count`는 고유 리드 수가 아니라 전환 레코드 수이므로, 한 리드가 여러 전환을 가진 경우 1.0을 초과할 수 있다.

## 동일 입력에 대해 동일 결과가 재현되는 이유

더미데이터 생성 과정에 난수나 외부 API 호출을 사용하지 않는다. 모든 원천 데이터 행은 코드에 고정되어 있으며, 최근 30일 계산 기준일도 `2026-05-12`로 고정되어 있다. 따라서 같은 코드와 같은 입력으로 실행하면 매번 동일한 원천 CSV와 동일한 결과 CSV가 생성된다.
