# Bybit 자동 스탑로스 설정 봇

Bybit 선물 거래에서 포지션 진입 시 자동으로 스탑로스를 설정하는 Python 봇입니다.

## 기능

- 🎯 **자동 스탑로스 설정**
  - 롱 포지션: 최근 4시간 최저점에 스탑로스 설정
  - 숏 포지션: 최근 4시간 최고점에 스탑로스 설정

- 📊 **데이터 분석**
  - CCXT 라이브러리로 Bybit API 연동
  - Pandas DataFrame으로 캔들 데이터 가공
  - 실시간 리스크 분석 및 출력

- 🔄 **실시간 모니터링**
  - 새로운 포지션 자동 감지
  - 설정 가능한 체크 간격
  - 중복 처리 방지

## 설치

### 1. 저장소 클론 또는 파일 다운로드

```bash
cd autostoploss
```

### 2. 필요한 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 환경 변수 설정

`.env.example` 파일을 `.env`로 복사하고 API 키를 입력합니다:

```bash
cp .env.example .env
```

`.env` 파일 편집:

```env
BYBIT_API_KEY=your_actual_api_key
BYBIT_API_SECRET=your_actual_api_secret
USE_TESTNET=true  # 실거래는 false
CHECK_INTERVAL=5
```

## 사용 방법

### 봇 실행

```bash
cd src
python main.py
```

### 실행 예시

```
🚀 Bybit 자동 스탑로스 봇 시작
⚠️  테스트넷 모드로 실행 중
⏰ 포지션 체크 간격: 5초

📍 [2025-01-15 14:30:00] 활성 포지션: 1개

🎯 새 포지션 감지: BTCUSDT
   방향: 롱(Long)
   크기: 0.1
   진입가: 45000.00

📊 BTCUSDT - 최근 4시간 캔들 데이터:
================================================================================
datetime          open      high       low     close     volume
2025-01-15 11:00  44800.0  45200.0  44700.0  45100.0  1234.5
2025-01-15 12:00  45100.0  45300.0  44900.0  45000.0  1456.2
2025-01-15 13:00  45000.0  45400.0  44850.0  45200.0  1567.8
2025-01-15 14:00  45200.0  45500.0  45000.0  45300.0  1678.9

📈 4시간 최고가: 45500.00
📉 4시간 최저가: 44700.00
📊 가격 범위: 800.00 (1.79%)
================================================================================

🔴 롱 포지션 -> 최저점(44700.00)에 스탑로스 설정

📊 리스크 분석:
   현재가: 45300.00
   스탑로스: 44700.00
   리스크: 0.67%

✅ 스탑로스 설정: BTCUSDT SELL @ 44700.00
✅ BTCUSDT 스탑로스 설정 완료!
```

## 프로젝트 구조

```
autostoploss/
├── src/
│   ├── main.py              # 메인 실행 파일
│   ├── bybit_client.py      # Bybit API 클라이언트
│   └── data_handler.py      # 데이터 처리 (pandas)
├── requirements.txt         # Python 패키지 의존성
├── .env.example            # 환경 변수 예시
└── README.md               # 이 파일
```

## 주요 함수

### `bybit_client.py`
- `create_bybit_client()`: Bybit CCXT 클라이언트 생성
- `get_positions()`: 현재 포지션 조회
- `set_stop_loss()`: 스탑로스 주문 설정

### `data_handler.py`
- `fetch_4hour_candles()`: 4시간 캔들 데이터를 DataFrame으로 조회
- `get_high_low_from_df()`: DataFrame에서 최고/최저가 추출
- `analyze_position_risk()`: 포지션 리스크 분석

### `main.py`
- `process_position()`: 개별 포지션 처리
- `monitor_positions()`: 포지션 모니터링 루프

## 주의사항

⚠️ **실거래 전 반드시 테스트넷에서 테스트하세요!**

1. **API 권한**: Bybit API 키에 선물 거래 권한이 있어야 합니다
2. **리스크 관리**: 스탑로스는 손실 제한 도구이지만 완전한 손실 방지를 보장하지 않습니다
3. **시장 변동성**: 급격한 가격 변동 시 슬리피지가 발생할 수 있습니다
4. **네트워크**: 안정적인 인터넷 연결이 필요합니다

## 라이선스

MIT License

## 면책 조항

이 소프트웨어는 교육 목적으로 제공됩니다. 실제 거래에서 발생하는 손실에 대해 개발자는 책임지지 않습니다.
