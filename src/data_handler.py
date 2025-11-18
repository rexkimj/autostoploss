"""
캔들 데이터 조회 및 pandas DataFrame 가공
"""
import pandas as pd
from datetime import datetime, timedelta


def fetch_4hour_candles(exchange, symbol):
    """
    최근 4시간 동안의 1시간 캔들 데이터 조회 및 DataFrame 변환

    Args:
        exchange: CCXT exchange 객체
        symbol: 심볼 (예: 'BTC/USDT:USDT')

    Returns:
        pd.DataFrame: 캔들 데이터프레임
    """
    try:
        # 최근 4개의 1시간 캔들 가져오기
        ohlcv = exchange.fetch_ohlcv(
            symbol=symbol,
            timeframe='1h',
            limit=4
        )

        # DataFrame 생성
        df = pd.DataFrame(
            ohlcv,
            columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
        )

        # 타임스탬프를 datetime으로 변환
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='ms')

        # 숫자 타입 변환
        df[['open', 'high', 'low', 'close', 'volume']] = df[
            ['open', 'high', 'low', 'close', 'volume']
        ].astype(float)

        return df

    except Exception as e:
        print(f"❌ {symbol} 캔들 데이터 조회 실패: {e}")
        return pd.DataFrame()


def get_high_low_from_df(df):
    """
    DataFrame에서 최고가와 최저가 추출

    Args:
        df: 캔들 데이터프레임

    Returns:
        tuple: (최고가, 최저가)
    """
    if df.empty:
        return None, None

    high_price = df['high'].max()
    low_price = df['low'].min()

    return high_price, low_price


def display_candle_data(df, symbol):
    """
    캔들 데이터를 보기 좋게 출력

    Args:
        df: 캔들 데이터프레임
        symbol: 심볼 이름
    """
    if df.empty:
        print(f"⚠️  {symbol}: 데이터 없음")
        return

    print(f"\n📊 {symbol} - 최근 4시간 캔들 데이터:")
    print("=" * 80)

    # 보기 좋게 포맷팅
    display_df = df[['datetime', 'open', 'high', 'low', 'close', 'volume']].copy()
    display_df['datetime'] = display_df['datetime'].dt.strftime('%Y-%m-%d %H:%M')

    print(display_df.to_string(index=False))

    # 요약 정보
    high, low = get_high_low_from_df(df)
    print(f"\n📈 4시간 최고가: {high:.2f}")
    print(f"📉 4시간 최저가: {low:.2f}")
    print(f"📊 가격 범위: {high - low:.2f} ({((high - low) / low * 100):.2f}%)")
    print("=" * 80)


def analyze_position_risk(df, position_side, entry_price):
    """
    포지션 리스크 분석

    Args:
        df: 캔들 데이터프레임
        position_side: 'Buy' (롱) 또는 'Sell' (숏)
        entry_price: 진입 가격

    Returns:
        dict: 리스크 분석 결과
    """
    if df.empty:
        return None

    high, low = get_high_low_from_df(df)
    current_price = df.iloc[-1]['close']

    if position_side.lower() == 'buy':  # 롱 포지션
        stop_loss_price = low
        distance_pct = ((entry_price - stop_loss_price) / entry_price) * 100
    else:  # 숏 포지션
        stop_loss_price = high
        distance_pct = ((stop_loss_price - entry_price) / entry_price) * 100

    return {
        'stop_loss_price': stop_loss_price,
        'entry_price': entry_price,
        'current_price': current_price,
        'distance_pct': distance_pct,
        'position_side': position_side
    }
